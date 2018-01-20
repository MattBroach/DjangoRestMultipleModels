============
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

