========
ViewSets
========

For use with ViewSets and Routers, **drf-multiple-model** provides the ``ObjectMultipleModelAPIViewSet`` and ``FlatMultipleModelAPIViewSet``.  A simple configuration for using the provided ViewSets might look like::

    from rest_framework import routers
    
    from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet

    class TextAPIView(ObjectMultipleModelAPIViewSet):
        querylist = [
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style='Sonnet'), 'serializer_class': PoemSerializer},
            ....
        ]

     router = routers.SimpleRouter()
     router.register('texts', TextAPIView, base_name='texts')


**WARNING:** Because the ObjectMultipleModel views do not provide the ``queryset`` property, you **must** specify the ``base_name`` property when you register a ``ObjectMultipleModelAPIViewSet`` with a router. 

The ``ObjectMultipleModelAPIViewSet`` has all the same configuration options as the ``ObjectMultipleModelAPIView`` object.  For more information, see the :doc:`basic usage <basic-usage>` section. 
