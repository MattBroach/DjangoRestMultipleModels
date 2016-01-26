# Multiple Model View

[Django Rest Framework](https://github.com/tomchristie/django-rest-framework) provides some incredible tools for serializing data, but sometimes you need to combine many serializers and/or models into a single API call.  **drf-multiple-model** is an app designed to do just that.

# Installation

Install the package from pip:

```
pip install django-rest-multiple-models
```

Make sure to add 'drf_multiple_model' to your INSTALLED_APPS:

```
INSTALLED_APPS = (
    ....
    'drf_multiple_model',
)
```

Then simply import the view into any views.py in which you'd want to use it:

```
from drf_multiple_model.views import MultipleModelAPIView
```

**Note:** This package is built on top of Django Rest Framework's generic views and serializers, so it presupposes that Django Rest Framework is installed and added to your project as well.

# Usage

**drf-multiple-model** comes with the `MultipleModelAPIView` generic class-based-view for serializing multiple models.  `MultipleModelAPIView` requires a `queryList` attribute, which is a list or tutple of queryset/serializer pairs (in that order).  For example, let's say you have the following models and serializers:

```
# Models
class Play(models.Model):
    genre = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    pages = models.IntegerField()

class Poem(models.Model):
    title = models.CharField(max_length=200)
    style = models.CharField(max_length=100)
    lines = models.IntegerField()
    stanzas = models.IntegerField()

# Serializers
class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ('genre','title','pages')

class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = ('title','stanzas')
```

Then you might use the `MultipleModelAPIView` as follows:


```
from drf_multiple_model.views import MultipleModelAPIView

class TextAPIView(MultipleModelAPIView):
    queryList = [
        (Play.objects.all(),PlaySerializer),
        (Poem.objects.filter(style='Sonnet'),PoemSerializer),
        ....
    ]
```

which would return:

```
[
    {
        'play' : [
                {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
                {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
                ....
            ],
    },
    {
        'poem' : [
                {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
                {'title': 'As a decrepit father takes delight', 'stanzas': 1},
                ....
            ],
    }
]
```

By default, `MultipleModelAPIView` uses the model name as a label.  If you want to use a custome label, you can add a third attribute, a string, to the queryList tuples, like so:

```
from drf_multiple_model.views import MultipleModelAPIView

class TextAPIView(MultipleModelAPIView):
    queryList = [
        (Play.objects.all(),PlaySerializer,'plays'),
        (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
        ....
    ]
```

which would return:

```
[
    {
        'plays': [
            {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
            {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
            ....
        ]
    },
    {
        'sonnets':[
            {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
            {'title': 'As a decrepit father takes delight', 'stanzas': 1},
            ....
        ],
    }
]
```

# Options

### Flat

Add the attribute `flat = True` to return a single JSON array with all of the objects mixed together.  For example:


```
class TextAPIView(MultipleModelAPIView):
    flat = True

    queryList = [
        (Play.objects.all(),PlaySerializer,'plays'),
        (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
        ....
    ]
```

would return:

```
[
    {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
    {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
    ....
    {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
    {'title': 'As a decrepit father takes delight', 'stanzas': 1},
    ....
]
```

### sorting_field

When using `flat=True`, by default the objects will be arranged by the order in which the querysets were listed in your `queryList` attribute.  However, you can specify a different ordering by adding the `sorting_field` to your view:


```
class TextAPIView(MultipleModelAPIView):
    flat = True
    sorting_field = 'title'

    queryList = [
        (Play.objects.all(),PlaySerializer,'plays'),
        (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
        ....
    ]
```

would return:

```
[
    {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
    {'title': 'As a decrepit father takes delight', 'stanzas': 1},
    {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
    {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
    ....
]
```

**WARNING:** the field chosen for ordering must be shared by all models/serializers in your queryList.  Any attempt to sort objects along non_shared fields with throw a `KeyError`.

### add_model_type

If no label is explicitly specified in your `queryList`, `MultipleModelAPIView` will use the model from each queryset a label.  If you don't want any extra labeling and just want your data as is, set `add_model_type = False`:

```
class TextAPIView(MultipleModelAPIView):
    add_model_type = False

    queryList = [
        (Play.objects.all(),PlaySerializer,'plays'),
        (Poem.objects.filter(style='Sonnet'),PoemSerializer,'sonnets'),
        ....
    ]
```

would return:

```
[
    [
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'pages': 350},
        {'genre': 'Tragedy', 'title': "Romeo and Juliet", 'pages': 300},
        ....
    ],
    [
        {'title': 'Shall I compare thee to a summer's day?', 'stanzas': 1},
        {'title': 'As a decrepit father takes delight', 'stanzas': 1},
        ....
    ]
]
```


This works with `flat = True` set as well -- the `'type':'myModel'` won't be appended to each data point in that case.  **Note:** adding a custom label to your queryList elements will **always** override add_model_type.  However, labels are taken on an element-by-element basis, so you can add labels for some of your models/querysets, but not others.

### get_queryList

**drf-multiple-model** now supports the creation of dynamic queryLists, by overwriting the get_queryList() function rather than simply specifying the queryList variable.  This allows you to do things like construct queries using url kwargs, etc:

```
class DynamicQueryView(MultipleModelAPIView):
    def get_queryList(self):
        title = self.kwargs['play'].replace('-',' ')

        queryList = ((Play.objects.filter(title=title),PlaySerializer),
                     (Poem.objects.filter(style="Sonnet"),PoemSerializer))

        return queryList
```

would return:

```
[
    { 'play': [
            {'title':'Julius Caesar','genre':'Tragedy','year':1623},
        ]
    },
    { 'poem': [
            {'title':"Shall I compare thee to a summer's day?",'style':'Sonnet'},
            {'title':"As a decrepit father takes delight",'style':'Sonnet'}
    ]}
]
```
# Pagination

If (and only if) `flat = True` on your view, **drf-multiple-model** supports some of Django Rest Framework's built-in pagination classes, including `PageNumberPagination` and `LimitOffsetPagination`.  Implementatation might look like this:

```
class BasicPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10 

class PageNumberPaginationView(MultipleModelAPIView):
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))
    flat = True
    pagination_class = BasicPagination
```

which would return:

```
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
```

# Mixin

If you want to combine `MultipleModelAPIView`'s `list()` function with other views, you can use the included `MultipleModelMixin` instead.

# Version Notes

* 1.5 -- Added support for Django Rest Framework's pagination classes, custom filter functions (the latter thanks to @Symmetric), and some base refactoring

* 1.3 -- Improper context passing bug fixed by @rbreu

* 1.2 -- Fixed a bug with the Browsable API when using Django Rest Framework >= 3.3

* 1.1 -- Added `get_queryList()` function to support creation of dynamic queryLists

* 1.0 -- initial release
