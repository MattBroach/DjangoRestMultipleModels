from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from rest_framework.response import Response


class BaseMultipleModelMixin(object):
    """
    Base class that holds functions need for all MultipleModelMixins/Views
    """
    querylist = None

    # Keys required for every item in a querylist
    required_keys = ['queryset', 'serializer_class']

    def get_querylist(self):
        assert self.querylist is not None, (
            '{} should either include a `querylist` attribute, '
            'or override the `get_querylist()` method.'.format(
                self.__class__.__name__
            )
        )

        return self.querylist

    def check_query_data(self, query_data):
        """
        All items in a `querylist` must at least have `queryset` key and a
        `serializer_class` key. Any querylist item lacking both those keys
        will raise a ValidationError
        """
        for key in self.required_keys:
            if not key in query_data:
                raise ValidationError(
                    'All items in the {} querylist attribute should contain a '
                    '`{}` key'.format(self.__class__.__name__, key)
                )

    def get_queryset(self, query_data, request, *args, **kwargs):
        """
        Fetches the queryset and runs any necessary filtering, both
        built-in rest_framework filters and custom filters passed into
        the querylist
        """
        queryset = query_data.get('queryset', [])

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        
        # run rest_framework filters
        queryset = self.filter_queryset(queryset)

        # run custom filters
        filter_fn = query_data.get('filter_fn', None)
        if filter_fn is not None:
            queryset = filter_fn(queryset, request, *args, **kwargs)

        return queryset

    def list(self, request, *args, **kwargs):
        raise NotImplementedError(
            '{} provides some standard Multiple Model Tools, but is not '
            'meant to be used directly .'.format(
                self.__class__.__name__
            )
        )


class FlatMultipleModelMixin(BaseMultipleModelMixin):
    """
    Create a List of objects from multiple models/serializers.

    Mixin is expecting the view will have a querylist variable, which is
    a list/tuple of dicts containing, at mininum, a `queryset` key and a 
    `serializer_class` key,  as below:

    queryList = [
        {'queryset': MyModalA.objects.all(), 'serializer_class': MyModelASerializer ),
        {'queryset': MyModalB.objects.all(), 'serializer_class': MyModelBSerializer ),
        {'queryset': MyModalC.objects.all(), 'serializer_class': MyModelCSerializer ),
        .....
    ]

    This mixin returns a list of serialized data merged together in a single list, eg:

    [
        { 'id': 1, 'type': 'myModelA', 'title': 'some_object' },
        { 'id': 4, 'type': 'myModelB', 'title': 'some_other_object' },
        { 'id': 8, 'type': 'myModelA', 'title': 'anotherother_object' },
        ...
    ]
    """
    # Optional keyword to sort flat lasts by given attribute
    # note that the attribute must by shared by ALL models
    sorting_field = None

    # Flag to append the particular django model being used to the data
    add_model_type = True

    def list(self, request, *args, **kwargs):
        querylist = self.get_querylist()

        results = []

        for query_data in querylist:
            self.check_query_data(query_data)

            queryset = self.get_queryset(query_data, request, *args, **kwargs)

            # Run the paired serializer
            context = self.get_serializer_context()
            data = query_data['serializer_class'](queryset, many=True, context=context).data

            label = self.get_label(queryset, query_data)

            for datum in data:
                if label is not None:
                    datum.update({'type': label})

                results.append(datum)

        if self.sorting_field:
            results = self.sort_results(results)

        if request.accepted_renderer.format == 'html':
            return Response({'data': results})

        return Response(results)

    def get_label(self, queryset, query_data):
        """
        Gets option label for each datum. Can be used for type identification
        of individual serialized objects
        """
        if query_data.get('label', False):
            return query_data['label']
        elif self.add_model_type:
            return queryset.model.__name__

    def sort_results(self, results):
        """
        determing if sort is ascending or descending
        based on the presence of '-' at the beginning of the
        sorting_field attribute
        """
        sorting_field = self.sorting_field
        sort_descending = self.sorting_field[0] == '-'

        # Remove the '-' if sort descending
        if sort_descending:
            sorting_field = sorting_field[1:len(sorting_field)]

        return sorted(
            results,
            reverse=sort_descending,
            key=lambda datum: datum[sorting_field]
        )


class ObjectMultipleModelMixin(BaseMultipleModelMixin):
    """
    Create a Dictionary of objects from multiple models/serializers.

    Mixin is expecting the view will have a querylist variable, which is
    a list/tuple of dicts containing, at mininum, a `queryset` key and a 
    `serializer_class` key,  as below:

    queryList = [
        {'queryset': MyModalA.objects.all(), 'serializer_class': MyModelASerializer ),
        {'queryset': MyModalB.objects.all(), 'serializer_class': MyModelBSerializer ),
        {'queryset': MyModalC.objects.all(), 'serializer_class': MyModelCSerializer ),
        ...
    ]

    This mixin returns a dictionary of serialized data separated by object type, e.g.:

    {
        'MyModelA': [
            { 'id': 1, 'type': 'myModelA', 'title': 'some_object' },
            { 'id': 8, 'type': 'myModelA', 'title': 'anotherother_object' },
            ...
        ],
        'MyModelB': [
            { 'id': 4, 'type': 'myModelB', 'title': 'some_other_object' },
            ...
        ]
        ...
    }
    """
    def list(self, request, *args, **kwargs):
        querylist = self.get_querylist()

        results = {}

        for query_data in querylist:
            self.check_query_data(query_data)

            queryset = self.get_queryset(query_data, request, *args, **kwargs)

            # Run the paired serializer
            context = self.get_serializer_context()
            data = query_data['serializer_class'](queryset, many=True, context=context).data

            label = self.get_label(queryset, query_data)

            results[label] = data

        if request.accepted_renderer.format == 'html':
            return Response({'data': results})

        return Response(results)

    def get_label(self, queryset, query_data):
        """
        Gets option label for each datum. Can be used for type identification
        of individual serialized objects
        """
        if query_data.get('label', False):
            return query_data['label']

        return queryset.model.__name__
