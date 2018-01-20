==================================
ObjectMultipleModelAPIView Options
==================================

Labels
======

By default, ``ObjectMultipleModelAPIView`` uses the model name as a label. If you want to use a custom label, you can add a ``label`` key to your ``querylist`` dicts, like so::

    from drf_multiple_model.views import ObjectMultipleModelAPIView

    class TextAPIView(ObjectMultipleModelAPIView):
        querylist = [
            {
                'querylist': Play.objects.all(),
                'serializer_class': PlaySerializer,
                'label': 'drama',
            },
            {
                'querylist': Poem.objects.filter(style='Sonnet'),
                'serializer_class': PoemSerializer,
                'label': 'sonnets'
            },
            ....
        ]

which would return::

    {
        'drama': [
            {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
            {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
            ....
        ],
        'sonnets':[
            {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
            {'title': 'As a decrepit father takes delight', 'stanzas': 1},
            ....
        ],
    }

