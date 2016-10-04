=============
Release Notes
=============

1.8 (2016-09-04)
==============

* Added ``objectify`` property to return JSON object instead of an array (implemented by @ELIYAHUT123)
* Added ``MultipleModelAPIViewSet`` for working with Viewsets (credit to Mike Hwang (@mehwang) for working out the implementation)
* implemented tox for simultaneous testing of all relevant python/django combos
* dropped support for Django 1.7 (based on Django Rest Frameworks's concurrent lack of support)

1.7 (2016-06-09)
===============

* Expanded documentation
* Moved to sphynx docs/readthedocs.org
* Moved data formatting to ``format_data()`` function to allow for custom post-serialization data handling

1.6 (2016-02-23)
================

* Incorporated and expanded on reverse sort implemented by @schweickism

1.5 (2016-01-28)
===============

* Added support for Django Rest Framework's pagination classes
* Custom filter functions (implemented by @Symmetric)
* Created Query class for handling queryList elements (implemented by @Symmetric)

1.3 (2015-12-10)
================

* Improper context passing bug fixed by @rbreu

1.2 (2015-11-11)
===============

* Fixed a bug with the Browsable API when using Django Rest Framework >= 3.3

1.1 (2015-07-06)
================

* Added `get_queryList()` function to support creation of dynamic queryLists

1.0 (2016-06-29)
================

* initial release
