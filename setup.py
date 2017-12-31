import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'PYPI_README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rest-multiple-models',
    version='1.8.2',
    packages=['drf_multiple_model'],
    include_package_data=True,
    license='MIT License',
    description='Multiple model/queryset view (and mixin) for Django Rest Framework',
    long_description=README,
    url='https://github.com/Axiologue/DjangoRestMultipleModels',
    author='Matt Nishi-Broach',
    author_email='go.for.dover@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
