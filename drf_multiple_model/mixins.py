from rest_framework.response import Response


class MultipleModelMixin(object):
    """
    Create a list of objects from multiple models/serializers.

    Mixin is expecting the view will have a queryList variable, which is
    a list/tuple of queryset/serailizer pairs, like as below:

    queryList = [
            (querysetA,serializerA),
            (querysetB,serializerB),
            (querysetC,serializerC),
            .....
    ]

    optionally, you can add a third element to the queryList,
    a label to define that particular data type:

    queryList = [
            (querysetA,serializerA,'labelA'),
            (querysetB,serializerB,'labelB'),
            (querysetC,serializerC),
            .....
    ]

    """

    objectify = False

    queryList = None

    # Flag to determine whether to mix objects together or keep them distinct
    flat = False

    paginating_label = None

    # Optional keyword to sort flat lasts by given attribute
    # note that the attribute must by shared by ALL models
    sorting_field = None

    # Flag to append the particular django model being used to the data
    add_model_type = True

    def get_queryList(self):
        assert self.queryList is not None, (
            "'%s' should either include a `queryList` attribute, "
            "or override the `get_queryList()` method."
            % self.__class__.__name__
        )

        queryList = self.queryList
        qlist = []
        for query in queryList:
            if not isinstance(query, Query):
                query = Query.new_from_tuple(query)
            qs = query.queryset.all()
            query.queryset = qs
            qlist.append(query)

        return qlist

    def paginate_queryList(self, queryList):
        """
        Wrapper for pagination function.

        By default it just calls paginate_queryset, but can be overwritten for custom functionality
        """
        return self.paginate_queryset(queryList)

    def list(self, request, *args, **kwargs):
        queryList = self.get_queryList()

        results = {} if self.objectify else []

        # Iterate through the queryList, run each queryset and serialize the data
        for query in queryList:
            if not isinstance(query, Query):
                query = Query.new_from_tuple(query)
            # Run the queryset through Django Rest Framework filters
            queryset = self.filter_queryset(query.queryset)

            # If there is a user-defined filter, run that too.
            if query.filter_fn is not None:
                queryset = query.filter_fn(queryset, request, *args, **kwargs)

            # Run the paired serializer
            context = self.get_serializer_context()
            data = query.serializer(queryset, many=True, context=context).data

            results = self.format_data(data, query, results)

        if self.flat:
            # Sort by given attribute, if sorting_attribute is provided
            if self.sorting_field:
                results = self.queryList_sort(results)

            # Return paginated results if pagination is enabled
            page = self.paginate_queryList(results)
            if page is not None:
                return self.get_paginated_response(page)


        if request.accepted_renderer.format == 'html':
            return Response({'data': results})

        return Response(results)

    # formats the serialized data based on various view properties (e.g. flat=True)
    def format_data(self, new_data, query, results):
        # Get the label, unless add_model_type is note set
        label = None
        if query.label is not None:
            label = query.label
        else:
            if self.add_model_type:
                label = query.queryset.model.__name__.lower()

        if self.flat and self.objectify:
            raise RuntimeError("Cannot objectify data with flat=True. Try to use flat=False")

        # if flat=True, Organize the data in a flat manner
        elif self.flat:
            for datum in new_data:
                if label:
                    datum.update({'type': label})
                results.append(datum)

        # if objectify=True, Organize the data in an object
        elif self.objectify:
            if not label:
                raise RuntimeError("Cannot objectify data. Try to use objectify=False")

            # Get paginated data for selected label, if paginating_label is provided
            if label == self.paginating_label:
                paginated_results = self.get_paginated_response(new_data).data
                paginated_results.pop("results", None)
                results.update(paginated_results)

            results[label] = new_data

        # Otherwise, group the data by Model/Queryset
        else:
            if label:
                new_data = {label: new_data}

            results.append(new_data)

        return results

    # Sort based on the given sorting field property
    def queryList_sort(self, results):
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


class Query(object):

    def __init__(self, queryset, serializer, label=None, filter_fn=None, ):
        self.queryset = queryset
        self.serializer = serializer
        self.filter_fn = filter_fn
        self.label = label

    @classmethod
    def new_from_tuple(cls, tuple_):
        try:
            queryset, serializer, label = tuple_
        except ValueError:
            queryset, serializer = tuple_
            label = None
        query = Query(queryset, serializer, label)
        return query
