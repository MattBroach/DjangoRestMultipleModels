.. DjangoRestMultipleModels documentation master file, created by
   sphinx-quickstart on Thu Jun  9 15:00:02 2016.

========================
DjangoRestMultipleModels
========================

`Django Rest Framework <https://github.com/tomchristie/django-rest-framework>`_ provides some incredible tools for serializing data, but sometimes you need to combine many serializers and/or models into a single API call.  **drf-multiple-model** is an app designed to do just that.


Installation
============

Install the package from pip::

    pip install django-rest-multiple-models

Make sure to add 'drf_multiple_model' to your INSTALLED_APPS::

    INSTALLED_APPS = (
        ....
        'drf_multiple_model',
    )

Then simply import the view into any views.py in which you'd want to use it::

    from drf_multiple_model.views import ObjectMultipleModelAPIView

**Note:** This package is built on top of Django Rest Framework's generic views and serializers, so it presupposes that Django Rest Framework is installed and added to your project as well.


Contents:

.. toctree::
   :maxdepth: 2

   basic-usage
   installation
   object-options
   flat-options
   filtering
   pagination
   viewsets
   one-to-two
   release-notes
   acknowledgments 

