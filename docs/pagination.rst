Pagination
==========

If (and only if) ``flat = True`` on your view, **drf-multiple-model** supports some of Django Rest Framework's built-in pagination classes, including ``PageNumberPagination`` and ``LimitOffsetPagination``.  Implementatation might look like this::

    class BasicPagination(pagination.PageNumberPagination):
        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 10 

    class PageNumberPaginationView(MultipleModelAPIView):
        queryList = ((Play.objects.all(),PlaySerializer),
                     (Poem.objects.filter(style="Sonnet"),PoemSerializer))
        flat = True
        pagination_class = BasicPagination

which would return::

    {
        'count': 6,
        'next': 'http://yourserver/yourUrl/?page=2',
        'previous': None,
        'results': 
            [
                {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                {'genre': 'Comedy', 'title': "The Tempest", 'pages': 250},
                {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                {'title': 'As a decrepit father takes delight', 'stanzas': 1}
            ]
    }

**WARNING**: In its currently implementation, pagination does NOT limit database queries, only the amount of information sent.  Due to the way multiple models are serializer and combined, the entire queryList is evaluated and then combined before pagination happens.  This means that Pagination in DRF Multiple Models is only useful for formating you API calls, not for creating more efficient queries.
