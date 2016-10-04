================================
Django Rest Multiple Model View
================================

drf-multiple-models provides an easy view (and mixin) for serializing multiple models in a single view.  It is built on top of (and meant to be an extension for) Django Rest Framework.

Installation
------------


1. Install the package from pip:

    .. code-block:: python 

        pip install django-rest-multiple-models

2. Make sure to add 'drf_multiple_model' to your INSTALLED_APPS:

    .. code-block:: python 

        INSTALLED_APPS = (
            ...
            'drf_multiple_model',
        )

3. Then simply import the view into any views.py in which you'd want to use it:

    .. code-block:: python 

        from drf_multiple_model.views import MultipleModelAPIView


Usage
-----

Documentation is on ReadTheDocs:
https://django-rest-multiple-models.readthedocs.io/en/latest/
