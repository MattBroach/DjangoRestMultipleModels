==========
Pagination
==========

Because Django and Rest Framework's paginators are designed to work with a single model/queryset, they cannot simply be dropped into a ``MultipleModelAPIView`` and function properly.  Currently, only **Limit/Offset** pagination has been ported to **drf_mutliple_model**, although other ``rest_framework`` paginators may be ported in the future.

.. _pagination:

Limit/Offset Pagination
=======================

Limit/Offset functions very similarly to (and with the same query parameters as) `Rest Framework's LimitOffsetPagination <(http://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination)>`_, but formatted to handle multiple models::

    from drf_multiple_model.views import ObjectMultipleModelAPIView
    from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination

    class LimitPagination(MultipleModelLimitOffsetPagination):
        default_limit = 2


    class ObjectLimitPaginationView(ObjectMultipleModelAPIView):
        pagination_class = LimitPagination
        querylist = (
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.all(), 'serializer_class': PoemSerializer},
        )

which would return::

    {
        'highest_count': 4,   # Play model has four objects in the database
        'overall_total': 7,   # 4 Plays + 3 Poems
        'next': 'http://yourserver/yourUrl/?page=2',
        'previous': None,
        'results': 
            {
                'Play': [
                    {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                    {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                ],
                'Poem': [
                    {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                    {'title': 'As a decrepit father takes delight', 'stanzas': 1},
                ],
            }
    }

This would also work with the ``FlatMultipleModelAPIView`` (with caveats, see below)::

    class FlatLimitPaginationView(FlatMultipleModelAPIView):
        pagination_class = LimitPagination
        querylist = (
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.all(), 'serializer_class': PoemSerializer},
        )

which would return::

    {
        'highest_count': 4,   # Play model has four objects in the database
        'overall_total': 7,   # 4 Plays + 3 Poems
        'next': 'http://yourserver/yourUrl/?page=2',
        'previous': None,
        'results': 
            [
                {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                {'title': 'As a decrepit father takes delight', 'stanzas': 1}
            ]
    }

.. warning::
   Important ``FlatMultipleModel`` caveats below!

The ``limit`` in LimitOffsetPagination is applied **per queryset**.  This means that the number of results returned is actually *number_of_querylist_items* * *limit*.  This is intuitive for the ``ObjectMultipleModelAPIView``, but the ``FlatMultipleModelAPIView`` may confuse some developers at first when a view with a limit of 50 and three different model/serializer combinations in the ``querylist`` returns a list of 150 items.

The other thing to note about ``MultipleModelLimitOffsetPagination`` and ``FlatMultipleModelAPIView`` is that sorting is done **after** the querylists have been filter by the limit/offset pair.  To understand why this may return some internal results, imagine a project ``ModalA``, which has 50 rows whose ``name`` field all start with 'A', and ModelB, which has 50 rows whose ``name`` field all start with 'B'.  If limit/offset pagination with a limit of 10 is used in a view that sorts by ``name``, the first page will return 10 results with names that start with 'A' followed by 10 results that start with 'B'.  The second page with then **also** contain 10 results that start with 'A' followed by 10 results that start with 'B', which certainly won't map onto a users expectation of alphabetical sorting.  Unfortunately, sorting before fetching the data would likely require bypassing Django's querysets entirely and writing raw SQL with a join on the ``sorting_field`` field, which would be difficult to integrate cleanly into the current system.  It is therefore recommended that when using ``MultipleModelLimitOffsetPagination`` that ``sorting_field`` values by hidden fields like ``id`` that won't be visible to the end user.
