==================================
FlatMultipleModelAPIView Options
==================================

Labels
======

By default, ``FlatMultipleModelAPIView`` adds a ``type`` property to returned items with the model name. If you want to use a custom value for the ``type`` property other than the model name, you can add a ``label`` key to your ``querylist`` dicts, like so::

    from drf_multiple_model.views import FlatMultipleModelAPIView

    class TextAPIView(FlatMultipleModelAPIView):
        querylist = [
            {
                'queryset': Play.objects.all(),
                'serializer_class': PlaySerializer,
                'label': 'drama',
            },
            {
                'queryset': Poem.objects.filter(style='Sonnet'),
                'serializer_class': PoemSerializer,
                'label': 'sonnet'
            },
            ....
        ]

which would return::

    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350, 'type': 'drama'},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300, 'type': 'drama'},
        ....
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1, 'type': 'sonnet'},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1, 'type': 'sonnet'},
        ....
    ]

If you'd prefer not to add the ``type`` property to returned items, you can set the class-level field of ``add_model_type`` to ``False``::

    class TextAPIView(FlatMultipleModelAPIView):
        add_model_type = False

        querylist = [
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style='Sonnet'), 'serializer_class': PoemSerializer},
            ....
        ]

which would return::

    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
        ....
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1},
        ....
    ]

**Note:** adding a custom label to your querylist elements will **always** override ``add_model_type``.  However, labels are taken on an element-by-element basis, so you can add labels for some of your models/querysets, but not others.

sorting_field
=============

By default the objects will be arranged by the order in which the querysets were listed in your ``querylist`` attribute.  However, you can specify a different ordering by adding the ``sorting_fields`` to your view, which works similar to Django's ``ordering``::

    class TextAPIView(FlatMultipleModelAPIView):
        sorting_fields = ['title']

        querylist = [
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style='Sonnet'), 'serializer_class': PoemSerializer},
            ....
        ]

would return::

    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350, 'type': 'Play'},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1, 'type': 'Poem'},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300, 'type': 'Play'},
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1, 'type': 'Poem'},
        ....
    ]

As with django field ordering, add '-' to the beginning of the field to enable reverse sorting.  Setting ``sorting_fields=['-title', 'name']`` would sort the title fields in __descending__ order and name in __ascending__

Also, a DRF-style sorting is supported. By default it uses ``o`` parameter from request query string. ``sorting_parameter_name`` property controls what parameter to use for sorting.
Lookups are working in the django-filters style, like ``property_1__property_2`` (which will use object's ``property_1`` and, in turn, its ``property_2`` as key argument to ``sorted()``)
Sorting is also possible by several fields. Sorting field have to be split with commas for that. Could be passed either via ``sorting_parameter_name`` in request parameters, or via view property.

**WARNING:** the field chosen for ordering must be shared by all models/serializers in your ``querylist``.  Any attempt to sort objects along non_shared fields will throw a ``KeyError``.

