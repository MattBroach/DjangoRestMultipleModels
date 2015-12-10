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

    def list(self, request, *args, **kwargs):
        queryList = self.get_queryList()

        # Iterate through the queryList, run each queryset and serialize the data
        results = []
        for pair in queryList:
            # Run the queryset through Django Rest Framework filters
            queryset = self.filter_queryset(pair[0])

            # Run the paired serializer
            context = self.get_serializer_context()
            data = pair[1](queryset,many=True,context=context).data

            # Get the label, unless add_model_type is note set
            try:
                label = pair[2]
            except IndexError:
                if self.add_model_type:
                    label = queryset.model.__name__.lower()
                else:
                    label = None

            # if flat=True, Organize the data in a flat manner
            if self.flat:
                for datum in data:
                    if label:
                        datum.update({'type':label})
                    results.append(datum)

            # Otherwise, group the data by Model/Queryset
            else:
                if label:
                    data = { label: data }

                results.append(data)



        # Sort by given attribute, if sorting_attribute is provided
        if self.sorting_field and self.flat:
            results = sorted(results, key=lambda datum: datum[self.sorting_field])


        return Response(results)
