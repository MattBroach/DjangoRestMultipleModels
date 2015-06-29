from rest_framework.response import Response 

from itertools import chain

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

    def list(self, request, *args, **kwargs):

        # Iterate through the queryList, run each queryset and serialize the data
        results = []
        for pair in self.queryList:
            queryset = self.filter_queryset(pair[0])

            if self.flat:
                for obj in queryset:

                    data = pair[1](obj)

                    # Add the model type to each value, if flag is set
                    try:
                        data.update('type':pair[2])
                    except IndexError:
                        if self.add_model_type:
                            model = obj.__class__.__name__.lower()   
                            data.update('type':model)   

                    results.append(data)  
            else:  
                data = pair[1](queryset,many=True)

                try:
                    data = { pair[2]: data}
                except IndexError:
                    if self.add_model_type:
                        model = queryset[0].__class__.__name__.lower() 
                        data = { model: data }

                results.append(data)


        # Sort by given attribute, if sorting_Attribute is required
        if self.sorting_field and self.flat:
            object_list = sorted(object_list, key=lambda datum: datum[self.sorting_field]))


        return Response(results)