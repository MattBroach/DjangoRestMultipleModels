=========
Filtering
=========

Django Rest Framework Filters
=============================

Django Rest Frameworks default Filter Backends work out of the box.  These filters will be applied to **every** queryset in your queryList.  For example, using the `SearchFilter` Backend in a view::

    class SearchFilterView(ObjectMultipleModelAPIView):
        querylist = (
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
        )
        filter_backends = (filters.SearchFilter,)
        search_fields = ('title',)

accessed with a url like ``http://www.example.com/texts?search=as`` would return only the ``Plays`` and ``Poems`` with "as" in the title::

    {
        'Play': [
            {'title':'As You Like It','genre':'Comedy','year':1623},
        ],
        'Poem': [
            {'title':"As a decrepit father takes delight",'style':'Sonnet'},
        ]
    }

Per Queryset Filtering
======================

Using the built in Filter Backends is a nice DRY solution, but it doesn't work well if you want to apply the filter to some items in your queryList, but not others.  In order to apply more targeted queryset filtering, DRF Multiple Models provides two technique:

Override get_querylist()
------------------------

**drf-multiple-model** now supports the creation of dynamic queryLists, by overwriting the get_querylist() function rather than simply specifying the queryList variable.  This allows you to do things like construct queries using url kwargs, etc::

    class DynamicQueryView(ObjectMultipleModelAPIView):
        def get_querylist(self):
            title = self.request.query_params['play'].replace('-',' ')

            querylist = (
                {'queryset': Play.objects.filter(title=title), 'serializer_class': PlaySerializer},
                {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
            )

            return querylist

That view, if accessed via a url like ``http://www.example.com/texts?play=Julius-Caesar`` would return only plays that match the provided title, but the poems would be untouched::

        { 
            'play': [
                {'title':'Julius Caesar','genre':'Tragedy','year':1623},
            ],
            'poem': [
                {'title':"Shall I compare thee to a summer's day?",'style':'Sonnet'},
                {'title':"As a decrepit father takes delight",'style':'Sonnet'}
            ],
        }

Custom Filter Functions
-----------------------

If you want to create a more complicated filter or use a custom filtering function, you can pass a custom filter function as an element in your querylist using the ``filter_fn`` key::

    from drf_multiple_model.views import MultipleModelAPIView

    def title_without_letter(queryset, request, *args, **kwargs):
        letter_to_exclude = request.query_params['letter']
        return queryset.exclude(title__icontains=letter_to_exclude)

    class FilterFnView(MultipleModelAPIView):
        querylist = (
            {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer, 'filter_fn': title_without_letter},
            {'queryset': Poem.objects.all(), 'serializer_class':PoemSerializer},
        )

The above view will use the ``title_without_letter()`` function to filter the queryset and remove and title that contains the provided letter.  Accessed from the url ``http://www.example.com/texts?letter=o`` would return all plays without the letter 'o', but the poems would be untouched::

    {
        'play': [
            {'title':"A Midsummer Night's Dream",'genre':'Comedy','year':1600},
            {'title':'Julius Caesar','genre':'Tragedy','year':1623},
        ],
        'poem': [
            {'title':"Shall I compare thee to a summer's day?",'style':'Sonnet'},
            {'title':"As a decrepit father takes delight",'style':'Sonnet'},
            {'title':"A Lover's Complaint",'style':'Narrative'} 
        ],
    }
