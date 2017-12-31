========
ViewSets
========

For user with ViewSets and Routers, **drf-multiple-model** provides the ``MultipleModelAPIViewSet``.  A simple configuration for using the provided ViewSet might look like::

    from rest_framework import routers
    
    from drf_multiple_model.viewsets import MultipleModelAPIViewSet

    class TextAPIView(MultipleModelAPIViewSet):
        queryList = [
            (Play.objects.all(),PlaySerializer),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer),
            ....
        ]

     router = routers.SimpleRouter()
     router.register('texts', TextAPIView, base_name='texts')


**WARNING:** Because the MultipleModel views do not provide the ``queryset`` property, you **must** specify the ``base_name`` property when you register a ``MultipleModelAPIViewSet`` with a router. 

The ``MultipleModelAPIViewSet`` has all the same configuration options as the ``MultipleModelAPIView`` object.  For more information, see the :doc:`basic usage <basic-usage>`  section. 
