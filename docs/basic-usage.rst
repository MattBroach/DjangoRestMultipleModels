=====
Usage
=====

Basic Usage
============

**drf-multiple-model** comes with the ``MultipleModelAPIView`` generic class-based-view for serializing multiple models.  ``MultipleModelAPIView`` requires a ``queryList`` attribute, which is a list or tuple of queryset/serializer pairs (in that order).  For example, let's say you have the following models and serializers::

    # Models
    class Play(models.Model):
        genre = models.CharField(max_length=100)
        title = models.CharField(max_length=200)
        pages = models.IntegerField()

    class Poem(models.Model):
        title = models.CharField(max_length=200)
        style = models.CharField(max_length=100)
        lines = models.IntegerField()
        stanzas = models.IntegerField()

    # Serializers
    class PlaySerializer(serializers.ModelSerializer):
        class Meta:
            model = Play
            fields = ('genre','title','pages')

    class PoemSerializer(serializers.ModelSerializer):
        class Meta:
            model = Poem
            fields = ('title','stanzas')

Then you might use the ``MultipleModelAPIView`` as follows::

    from drf_multiple_model.views import MultipleModelAPIView

    class TextAPIView(MultipleModelAPIView):
        queryList = [
            (Play.objects.all(),PlaySerializer),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer),
            ....
        ]

which would return::

    [
        {
            'play' : [
                    {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                    {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                    ....
                ],
        },
        {
            'poem' : [
                    {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                    {'title': 'As a decrepit father takes delight', 'stanzas': 1},
                    ....
                ],
        }
    ]

Configuration Options
=====================

Objectify
---------

When using the results of the ``MultipleModelAPIView``, it's often easier to parse the results as a JSON object rather than as an array.  To facilitate this, ``MultipleModelAPIView`` has the ``objectify`` property, which when set to ``True`` returns the results as an object.  For example, the following::

    from drf_multiple_model.views import MultipleModelAPIView

    class TextAPIView(MultipleModelAPIView):
        objectify = True
        queryList = [
            (Play.objects.all(),PlaySerializer),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer),
            ....
        ]

would return::

    {
        'play' : [
                {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                ....
            ],
        'poem' : [
                {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                {'title': 'As a decrepit father takes delight', 'stanzas': 1},
                ....
            ],
    }


Labels
------

By default, ``MultipleModelAPIView`` uses the model name as a label.  If you want to use a custome label, you can add a third attribute, a string, to the queryList tuples, like so::

    from drf_multiple_model.views import MultipleModelAPIView

    class TextAPIView(MultipleModelAPIView):
        queryList = [
            (Play.objects.all(),PlaySerializer,'plays'),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
            ....
        ]

which would return::

    [
        {
            'plays': [
                {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                ....
            ]
        },
        {
            'sonnets':[
                {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                {'title': 'As a decrepit father takes delight', 'stanzas': 1},
                ....
            ],
        }
    ]


Flat
----

Add the attribute ``flat = True`` to return a single JSON array with all of the objects mixed together.  For example::

    class TextAPIView(MultipleModelAPIView):
        flat = True

        queryList = [
            (Play.objects.all(),PlaySerializer,'plays'),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
            ....
        ]

would return::

    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
        ....
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1},
        ....
    ]

sorting_field
-------------

When using ``flat=True``, by default the objects will be arranged by the order in which the querysets were listed in your ``queryList`` attribute.  However, you can specify a different ordering by adding the ``sorting_field`` to your view::

    class TextAPIView(MultipleModelAPIView):
        flat = True
        sorting_field = 'title'

        queryList = [
            (Play.objects.all(),PlaySerializer,'plays'),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
            ....
        ]

would return::

    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
        ....
    ]

As with django field ordering, add '-' to the beginning of the field to enable reverse sorting.  Setting ``sorting_field='-title'`` would sort the title fields in __descending__ order.

**WARNING:** the field chosen for ordering must be shared by all models/serializers in your queryList.  Any attempt to sort objects along non_shared fields will throw a ``KeyError``.

add_model_type
--------------

If no label is explicitly specified in your ``queryList``, ``MultipleModelAPIView`` will use the model from each queryset a label.  If you don't want any extra labeling and just want your data as is, set ``add_model_type = False``::

    class TextAPIView(MultipleModelAPIView):
        add_model_type = False

        queryList = [
            (Play.objects.all(),PlaySerializer,'plays'),
            (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
            ....
        ]

would return::

    [
        [
            {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
            {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
            ....
        ],
        [
            {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
            {'title': 'As a decrepit father takes delight', 'stanzas': 1},
            ....
        ]
    ]


This works with ``flat = True`` set as well -- the ``'type':'myModel'`` won't be appended to each data point in that case.  **Note:** adding a custom label to your queryList elements will **always** override add_model_type.  However, labels are taken on an element-by-element basis, so you can add labels for some of your models/querysets, but not others.

Mixin
=====

If you want to combine ``MultipleModelAPIView``'s ``list()`` function with other views, you can use the included ``MultipleModelMixin`` instead.
