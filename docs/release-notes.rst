=============
Release Notes
=============

2.0 (2018-01-18)
================

* Refactored underlying code structure and API. Changes include:

  * Removed the nonsensical camelCase from querylist
  * Changing querylist items from lists/tupes to dicts (for more parameter flexibility). Eliminated the underlying ``Query`` model as a result.
  * Breaking the mixin into two separate mixins: ``ObjectMultipleModelMixing`` and ``FlatMultipleModelMixin``, as well as their respective views and viewsets
  * Removing the previously default response structure of ``list(dict(list( ... )``

* Adding limit/offset pagination that actually only queries the items it fetches (rather than iterating the whole queryset)
* Removing pagination functionality from the ``FlatMultipleModelMixin`` and adding it to the ``ObjectMultipleModelMixin``

1.8.1 (2017-12-20)
==================

* Dropped support for Django 1.8 and 1.9 (in keeping with Django Rest Framework's support)
* Expanded test coverage for Django 1.11 and Django 2.0

1.8 (2016-09-04)
================

* Added ``objectify`` property to return JSON object instead of an array (implemented by @ELIYAHUT123)
* Added ``MultipleModelAPIViewSet`` for working with Viewsets (credit to Mike Hwang (@mehwang) for working out the implementation)
* implemented tox for simultaneous testing of all relevant python/django combos
* dropped support for Django 1.7 (based on Django Rest Frameworks's concurrent lack of support)

1.7 (2016-06-09)
================

* Expanded documentation
* Moved to sphynx docs/readthedocs.org
* Moved data formatting to ``format_data()`` function to allow for custom post-serialization data handling

1.6 (2016-02-23)
================

* Incorporated and expanded on reverse sort implemented by @schweickism

1.5 (2016-01-28)
================

* Added support for Django Rest Framework's pagination classes
* Custom filter functions (implemented by @Symmetric)
* Created Query class for handling queryList elements (implemented by @Symmetric)

1.3 (2015-12-10)
================

* Improper context passing bug fixed by @rbreu

1.2 (2015-11-11)
================

* Fixed a bug with the Browsable API when using Django Rest Framework >= 3.3

1.1 (2015-07-06)
================

* Added ``get_queryList()`` function to support creation of dynamic queryLists

1.0 (2015-06-29)
================

* initial release
