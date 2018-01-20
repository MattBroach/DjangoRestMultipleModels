=====
Usage
=====

Basic Usage
============

**drf-multiple-model** comes with two generic class-based-view for serializing multiple models: the ``ObjectMultipleModelAPIView`` and the ``FlatMultipleModelAPIView``.  Both views require a ``querylist`` attribute, which is a list or tuple of dicts containing (at minimum) a ``queryset`` key and a ``serializer_class`` key; the main difference between the views is the format of the response data.  For example, let's say you have the following models and serializers::

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

Then you might use the ``ObjectMultipleModelAPIView`` as follows::

    from drf_multiple_model.views import ObjectMultipleModelAPIView

    class TextAPIView(ObjectMultipleModelAPIView):
        querylist = [
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style='Sonnet'), 'serializer_class': PoemSerializer},
            ....
        ]

which would return::

    {
        'Play' : [
            {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
            {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
            ....
        ],
        'Poem' : [
            {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
            {'title': 'As a decrepit father takes delight', 'stanzas': 1},
            ....
        ],
    }

Or you coulde use the ``FlatMultipleModelAPIView`` as follows::
  
    from drf_multiple_model.views import FlatMultipleModelAPIView

    class TextAPIView(FlatMultipleModelAPIView):
        querylist = [
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style='Sonnet'), 'serializer_class': PoemSerializer},
            ....
        ]

which would return::

    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350, 'type': 'Play'},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300, 'type': 'Play'},
        ....
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1, 'type': 'Poem'},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1, 'type': 'Poem'},
        ....
    ]


Mixins
======

If you want to combine ``ObjectMultipleModelAPIView`` or ``FlatMultipleModelAPIViews``'s ``list()`` function with other views, you can use their base mixins from ``mixins.py`` instead.
