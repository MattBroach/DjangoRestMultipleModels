=========================
Upgrading from 1.x to 2.0
=========================

**drf_multiple_model** went through a substantial re-write from 1.x to 2.0. Not only did much of the underlying code get re-structured and streamlined, but the classes and API changed as well.  Here are some of the biggest changes developers need to be aware of.

views/mixins split in two
=========================

Earlier iterations of **drf_multiple_model** tried to shoehorn many different formats and functionalities into a single view/mixin.  This was making development increasingly difficult, as potentially problematic interactions grew expenentionally with the number of competing options.  Instead of the the single ``MultipleModelAPIView``, you should use the following views:

1. If your 1.x view had ``flat = True``, you should use the ``FlatMultipleModelAPIView``
2. If your 1.x view had ``objectify = True``, you should use the ``ObjectMultipleModelAPIView``
3. If your 1.x view had both ``flat = True`` and ``objectify = True``, your view was broken and likely raised an Exception.  Use one of the options above.
4. If your 1.x view had neither ``flat = True`` nor ``objectify = True``, you should reconsider and use one of the options above.  The previously default response structure of ``list(dict(list( ... )`` made no sense, was overly complicated to consume, and has been removed from v2.0.

querylist is no longer camelCased
=================================

The bizarrely camelCased ``queryList`` field has been renamed the much more pythonic ``querylist``

querylist items are now dicts, not lists/tuples
===============================================

If your 1.x querylist looked like this::

    queryList = (
        (Poem.objects.all(), PoemSerializer),
        (Play.objects.all(), PlaySerializer),
    )

your 2.0 querlist should look like this::

    querylist = (
        {'queryset': Poem.objects.all(), 'serializer_class': PoemSerializer},
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
    )

Although this structure is slightly more verbose, is **much** more extensible.  Consider, for example, what was needed previously in order to add a per-queryset filter function::

    from drf_multiple_model.views import MultipleModelAPIView
    from drf_multiple_model.mixins import Query

    def my_custom_filter_fn(queryset, request, *args, **kwargs):
        ....

    class FilterFnView(MultipleModelAPIView):
        queryList = (
            Query(Play.objects.all(), PlaySerializer, filter_fn=my_custom_filter_Fn),
            (Poem.objects.all(), PoemSerializer),
        )

This requires importing a special ``Query`` item, and confusingly mixing types (``Query`` object and ``tuple``) in the querylist. With the ``dict`` querylist structure, any number of extra parameters can be added simply by adding an extra key::

    querylist = (
        {'queryset': Poem.objects.all(), 'serializer_class': PoemSerializer, 'filter_fn': my_custom_filter_fn},
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
    )

pagination uses custom-built paginators
=======================================

Pagination in 1.x used the built in **rest_framework** paginators, but didn't actually restricted the items being queried; it simply formated the data **after** it had been fetched to remove extra items.  Pagination has been re-written to only query the items request in 2.0, but this means paginators had to be re-written/extended to properly handle multiple querysets.  As such, you can longer simply drop in **rest_framework** paginators and should only use the pagination available in ``drf_multiple_model.pagination``.  See :ref:`pagination` for more details.
