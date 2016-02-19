from rest_framework.response import Response

from itertools import chain

from django.db import connection


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

    optionally, you can add a third element to the queryList, a label to define that particular
    data type:

    queryList = [
            (querysetA,serializerA,'labelA'),
            (querysetB,serializerB,'labelB'),
            (querysetC,serializerC),
            .....
    ]

    """

    queryList = None

    # Flag to determine whether to mix objects together or keep them distinct
    flat = False

    # Optional keyword to sort flat lasts by given attribute
    # note that the attribute must by shared by ALL models
    sorting_field = None

    # Sort order for sorting_field
    sort_descending = False

    # Flag to append the particular django model being used to the data
    add_model_type = True

    def get_queryList(self):
        assert self.queryList is not None, (
            "'%s' should either include a `queryList` attribute, "
            "or override the `get_queryList()` method."
            % self.__class__.__name__
        )

        queryList = self.queryList

        return queryList

    def paginate_queryList(self,queryList):
        """
        Wrapper for pagination function.
        By default it just calls paginate_queryset, but can be overwritten for custom functionality
        """
        return self.paginate_queryset(queryList) 

    def list(self, request, *args, **kwargs):
        queryList = self.get_queryList()

        # Iterate through the queryList, run each queryset and serialize the data
        results = []
        for query in queryList:
            if not isinstance(query, Query):
                query = Query.new_from_tuple(query)
            # Run the queryset through Django Rest Framework filters
            queryset = self.filter_queryset(query.queryset)

            # If there is a user-defined filter, run that too.
            if query.filter_fn is not None:
                queryset = query.filter_fn(queryset, *args, **kwargs)

            # Run the paired serializer
            context = self.get_serializer_context()
            data = query.serializer(queryset, many=True, context=context).data

            # Get the label, unless add_model_type is note set
            label = None
            if query.label is not None:
                label = query.label
            else:
                if self.add_model_type:
                    label = queryset.model.__name__.lower()

            # if flat=True, Organize the data in a flat manner
            if self.flat:
                for datum in data:
                    if label:
                        datum.update({'type': label})
                    results.append(datum)

            # Otherwise, group the data by Model/Queryset
            else:
                if label:
                    data = {label: data}

                results.append(data)

        if self.flat:
            # Sort by given attribute, if sorting_attribute is provided
            if self.sorting_field:
                results = self.sort(results)
            
            # Return paginated results if pagination is enabled
            page = self.paginate_queryList(results)
            if page is not None:
                return self.get_paginated_response(page)

        if request.accepted_renderer.format == 'html':
            return Response({'data': results})

        return Response(results)

    def sort(self, results):
        return sorted(results, reverse=self.sort_descending, key=lambda datum: datum[self.sorting_field])


class Query(object):
    def __init__(self, queryset, serializer, label=None,filter_fn=None, ):
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
