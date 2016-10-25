from collections import OrderedDict

import django.template.loader
from django.conf.urls import url
from django.core.cache import cache
from django.db import models
from django.template import TemplateDoesNotExist, Template
from django.test import TestCase, override_settings
from rest_framework import serializers, status, renderers, \
    pagination, filters, routers
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from drf_multiple_model.mixins import Query
from drf_multiple_model.views import MultipleModelAPIView
from drf_multiple_model.viewsets import MultipleModelAPIViewSet

factory = APIRequestFactory()


# Models

class RestTestModels(models.Model):
    """
    Taking idea from Rest Framework's own tests
    Base for test models that creates a unified app label
    """

    class Meta:
        app_label = "mm_tests"
        abstract = True


class Play(models.Model):
    genre = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    year = models.IntegerField(max_length=4)


class Poem(models.Model):
    title = models.CharField(max_length=200)
    style = models.CharField(max_length=100)


# Serializers

class PlaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Play
        fields = ('genre', 'title', 'year')


class PoemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poem
        fields = ('title', 'style')


# Views

# For testing that the default settings behave normally
class BasicTestView(MultipleModelAPIView):
    queryList = ((Play.objects.all(), PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"), PoemSerializer))


class TestBrowsableAPIView(BasicTestView):
    renderer_classes = (renderers.BrowsableAPIRenderer,)


# Testing the objectify property (should return a dict/object instead
# of a list/array
class AsObjectView(BasicTestView):
    objectify = True


# Testing label functionality
class LabelTestView(MultipleModelAPIView):
    queryList = ((Play.objects.all(), PlaySerializer, 'The Plays'),
                 (Poem.objects.filter(style="Sonnet"), PoemSerializer, 'The Sonnets'))


# For no label, set add_model_type to False
class BasicNoLabelView(BasicTestView):
    add_model_type = False


# Testing flat, without labels
class BasicFlatView(BasicTestView):
    flat = True


# Testing sort
class OrderedFlatView(BasicFlatView):
    sorting_field = 'title'


# Testing reverse sort
class ReversedFlatView(BasicFlatView):
    sorting_field = '-title'


# Testing incorrect sort
class OrderedWrongView(BasicFlatView):
    sorting_field = 'year'


# Testing No Label
class FlatNoLabelView(BasicFlatView):
    add_model_type = False


# Testing label functionality when flat
class FlatLabelView(MultipleModelAPIView):
    flat = True
    queryList = ((Play.objects.all(), PlaySerializer, 'Drama'),
                 (Poem.objects.filter(style="Sonnet"), PoemSerializer, 'Poetry'))


# Testing missing queryList
class BrokenView(MultipleModelAPIView):
    pass


# Testing get_queryList function
class DynamicQueryView(MultipleModelAPIView):

    def get_queryList(self):
        title = self.kwargs['play'].replace('-', ' ')

        queryList = ((Play.objects.filter(title=title), PlaySerializer),
                     (Poem.objects.filter(style="Sonnet"), PoemSerializer))

        return queryList


class CachedQueryView(MultipleModelAPIView):

    def get_queryList(self):
        queryList = cache.get('cachedquerylist')
        if not queryList:
            title = self.kwargs['play'].replace('-', ' ')
            queryList = ((Play.objects.filter(title=title), PlaySerializer),
                         (Poem.objects.filter(style="Sonnet"), PoemSerializer))
            cache.set('cachedquerylist', queryList)
        return queryList


# Testing PageNumberPagination
class BasicPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class PageNumberPaginationView(BasicFlatView):
    pagination_class = BasicPagination


# Testing LinitOffsetPagination
class LimitPagination(pagination.LimitOffsetPagination):
    default_limit = 5
    max_limit = 15


class LimitOffsetPaginationView(BasicFlatView):
    pagination_class = LimitPagination


# Testing TemplateHTMLRenderer view bug
class HTMLRendererView(BasicFlatView):
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)
    template_name = 'test.html'


# Testing filter_fn
def title_without_letter(queryset, request, *args, **kwargs):
    letter_to_exclude = request.query_params['letter']
    return queryset.exclude(title__icontains=letter_to_exclude)


class FilterFnView(MultipleModelAPIView):
    queryList = (Query(Play.objects.all(), PlaySerializer, filter_fn=title_without_letter),
                 (Poem.objects.all(), PoemSerializer))


# Testing Built-in DRF Filter
class SearchFilterView(BasicTestView):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title',)


# Testing Base Viewset
class BasicTestViewSet(MultipleModelAPIViewSet):
    queryList = ((Play.objects.all(), PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"), PoemSerializer))


# Routers for testing viewset
router = routers.SimpleRouter()
router.register(r'viewset', BasicTestViewSet, base_name='viewset')

urlpatterns = router.urls

# Fake URL Patterns for running tests
urlpatterns += [
    url(r"^$", TestBrowsableAPIView.as_view()),
    url(r"^template$", HTMLRendererView.as_view()),
]


# Tests
@override_settings(ROOT_URLCONF=__name__)
class TestMMViews(TestCase):

    def setUp(self):
        Play.objects.bulk_create([
            Play(title='Romeo And Juliet',
                 genre='Tragedy',
                 year=1597),
            Play(title="A Midsummer Night's Dream",
                 genre='Comedy',
                 year=1600),
            Play(title='Julius Caesar',
                 genre='Tragedy',
                 year=1623),
            Play(title='As You Like It',
                 genre='Comedy',
                 year=1623)
        ])

        Poem.objects.bulk_create([
            Poem(title="Shall I compare thee to a summer's day?",
                 style="Sonnet"),
            Poem(title="As a decrepit father takes delight",
                 style="Sonnet"),
            Poem(title="A Lover's Complaint",
                 style="Narrative")
        ])

    def test_defaults(self):
        """
        Tests the default case for the MultipleModelAPIView, which should be:
            flat = False
            sorting_field = None
            add_model_type = True
            objectify = False
        """

        view = BasicTestView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, [
            {'play': [
                {'title': 'Romeo And Juliet', 'genre': 'Tragedy', 'year': 1597},
                {'title': "A Midsummer Night's Dream", 'genre': 'Comedy', 'year': 1600},
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
                {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623},
            ]
            },
            {'poem': [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]}
        ])

    def test_post(self):
        """
        POST requests should throw a 405 Error
        """
        view = BasicTestView.as_view()

        data = {'fake': 'data'}
        request = factory.post('/', data, format='json')

        with self.assertNumQueries(0):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data, {"detail": 'Method "POST" not allowed.'})

    def test_put(self):
        """
        PUT requests should throw a 405 Error
        """
        view = BasicTestView.as_view()

        data = {'fake': 'data'}
        request = factory.put('/', data, format='json')

        with self.assertNumQueries(0):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})

    def test_delete(self):
        """
        DELETE requests should throw a 405 Error
        """
        view = BasicTestView.as_view()

        request = factory.delete('/')

        with self.assertNumQueries(0):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})

    def test_objectify(self):
        """
        Tests the 'objectify' property, which allows returning an object/dict
        instead of a list/array
        """

        view = AsObjectView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'play': [
                {'title': 'Romeo And Juliet', 'genre': 'Tragedy', 'year': 1597},
                {'title': "A Midsummer Night's Dream", 'genre': 'Comedy', 'year': 1600},
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
                {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623},
            ],
            'poem': [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]
        })

    def test_no_label(self):
        """
        Tests that no label (aka add_model_type = False) just gives the data
        """

        view = BasicNoLabelView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, [
            [
                {'title': 'Romeo And Juliet', 'genre': 'Tragedy', 'year': 1597},
                {'title': "A Midsummer Night's Dream", 'genre': 'Comedy', 'year': 1600},
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
                {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623},
            ],
            [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]
        ])

    def test_new_labels(self):
        """
        Adding labels as a third element in the queryList elements should use those labels
        instead of the model names
        """

        view = LabelTestView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertIn('The Plays', response.data[0].keys())
        self.assertIn('The Sonnets', response.data[1].keys())

    def test_simple_flat(self):
        """
        Putting flat=True should flatten the data to a single list of elements
        """

        view = BasicFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            OrderedDict([('genre', 'Tragedy'), ('title', 'Romeo And Juliet'), ('year', 1597), ('type', 'play')]),
            OrderedDict([('genre', 'Comedy'), ('title', "A Midsummer Night's Dream"), ('year', 1600), ('type', 'play')]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Julius Caesar'), ('year', 1623), ('type', 'play')]),
            OrderedDict([('genre', 'Comedy'), ('title', 'As You Like It'), ('year', 1623), ('type', 'play')]),
            OrderedDict([('title', "Shall I compare thee to a summer's day?"), ('style', 'Sonnet'), ('type', 'poem')]),
            OrderedDict([('title', "As a decrepit father takes delight"), ('style', 'Sonnet'), ('type', 'poem')]),
        ])

    def test_ordered_flat(self):
        """
        Adding the sorting_field attribute should order the flat items according to whatever field
        """

        view = OrderedFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            OrderedDict([('genre', 'Comedy'), ('title', "A Midsummer Night's Dream"), ('year', 1600), ('type', 'play')]),
            OrderedDict([('genre', 'Comedy'), ('title', 'As You Like It'), ('year', 1623), ('type', 'play')]),
            OrderedDict([('title', "As a decrepit father takes delight"), ('style', 'Sonnet'), ('type', 'poem')]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Julius Caesar'), ('year', 1623), ('type', 'play')]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Romeo And Juliet'), ('year', 1597), ('type', 'play')]),
            OrderedDict([('title', "Shall I compare thee to a summer's day?"), ('style', 'Sonnet'), ('type', 'poem')]),
        ])

    def test_reversed_ordered(self):
        """
        Adding the sorting_field attribute should order the flat items according to whatever field
        """

        view = ReversedFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            OrderedDict([('title', "Shall I compare thee to a summer's day?"), ('style', 'Sonnet'), ('type', 'poem')]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Romeo And Juliet'), ('year', 1597), ('type', 'play')]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Julius Caesar'), ('year', 1623), ('type', 'play')]),
            OrderedDict([('title', "As a decrepit father takes delight"), ('style', 'Sonnet'), ('type', 'poem')]),
            OrderedDict([('genre', 'Comedy'), ('title', 'As You Like It'), ('year', 1623), ('type', 'play')]),
            OrderedDict([('genre', 'Comedy'), ('title', "A Midsummer Night's Dream"), ('year', 1600), ('type', 'play')]),
        ])

    def test_ordered_wrong_sorting(self):
        """
        Sorting by a non-shared field should throw a KeyError
        """

        view = OrderedWrongView.as_view()

        request = factory.get('/')
        self.assertRaises(KeyError, view, request)

    def test_flat_no_label(self):
        """
        Putting flat=True should flatten the data to a single list of elements
        """

        view = FlatNoLabelView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            OrderedDict([('genre', 'Tragedy'), ('title', 'Romeo And Juliet'), ('year', 1597)]),
            OrderedDict([('genre', 'Comedy'), ('title', "A Midsummer Night's Dream"), ('year', 1600)]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Julius Caesar'), ('year', 1623)]),
            OrderedDict([('genre', 'Comedy'), ('title', 'As You Like It'), ('year', 1623)]),
            OrderedDict([('title', "Shall I compare thee to a summer's day?"), ('style', 'Sonnet')]),
            OrderedDict([('title', "As a decrepit father takes delight"), ('style', 'Sonnet')]),
        ])

    def test_flat_custom_labels(self):
        """
        Putting flat=True should flatten the data to a single list of elements
        """

        view = FlatLabelView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            OrderedDict([('genre', 'Tragedy'), ('title', 'Romeo And Juliet'), ('year', 1597), ('type', 'Drama')]),
            OrderedDict([('genre', 'Comedy'), ('title', "A Midsummer Night's Dream"), ('year', 1600), ('type', 'Drama')]),
            OrderedDict([('genre', 'Tragedy'), ('title', 'Julius Caesar'), ('year', 1623), ('type', 'Drama')]),
            OrderedDict([('genre', 'Comedy'), ('title', 'As You Like It'), ('year', 1623), ('type', 'Drama')]),
            OrderedDict([('title', "Shall I compare thee to a summer's day?"), ('style', 'Sonnet'), ('type', 'Poetry')]),
            OrderedDict([('title', "As a decrepit father takes delight"), ('style', 'Sonnet'), ('type', 'Poetry')]),
        ])

    def test_missing_queryList(self):
        """
        not specifying a queryList or a get_queryList should raise an AssertionError
        """

        view = BrokenView.as_view()

        request = factory.get('/')

        self.assertRaises(AssertionError, view, request)

    def test_dynamic_queryList(self):
        """
        using get_QueryList allows the construction of dynamic queryLists
        """

        view = DynamicQueryView.as_view()

        request = factory.get('/Julius-Caesar')
        with self.assertNumQueries(2):
            response = view(request, play="Julius-Caesar")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, [
            {'play': [
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
            ]
            },
            {'poem': [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]}
        ])

    def test_cached_queryList(self):
        view = CachedQueryView.as_view()

        request = factory.get('/Julius-Caesar')
        with self.assertNumQueries(2):
            response = view(request, play="Julius-Caesar")
        with self.assertNumQueries(0):
            response = view(request, play="Julius-Caesar")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, [
            {'play': [
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
            ]
            },
            {'poem': [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]}
        ])

    def test_url_endpoint(self):
        """
        DRF 3.3 broke the MultipleModelAPIView with a get_queryset call
        This test is to replicate (and then fix) that problem
        """

        client = APIClient()
        response = client.get('/', format='api')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_number_pagination(self):
        """
        When flat is True, PageNumberPagination should work as in
        a normal DRF generic ListAPIView
        """

        view = PageNumberPaginationView.as_view()

        request = factory.get('/')

        with self.assertNumQueries(2):
            response = view(request).render()

        # Check first page of results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], 'http://testserver/?page=2')
        self.assertEqual(len(response.data['results']), 5)

        # Check second page of results
        request = factory.get('/', {'page': 2})
        response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Check change max size
        request = factory.get('/', {'page_size': 3})
        response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_limit_offset_pagination(self):
        """
        When Flat is True, LimitOffsetPagination should work
        as in a normal DRF ListAPIView
        """

        view = LimitOffsetPaginationView.as_view()

        request = factory.get('/')

        with self.assertNumQueries(2):
            response = view(request).render()

        # Check first page of results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], 'http://testserver/?limit=5&offset=5')
        self.assertEqual(response.data['count'], 6)
        self.assertEqual(len(response.data['results']), 5)

        # Check second page of results
        request = factory.get('/', {'offset': 5})
        response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['previous'], 'http://testserver/?limit=5')
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['count'], 6)
        self.assertEqual(len(response.data['results']), 1)

        # Check manually set limits
        request = factory.get('/', {'limit': 3})
        response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_filter_fn_view(self):
        """
        The filter function is useful if you want to apply filtering to one query
        but not another (unlike adding view level filtering, which will filter all the
        querysets), but that filtering can't be provided at the beginning (for example, it
        needs to access a query_param).  This is testing the filter_fn.
        """

        view = FilterFnView.as_view()

        request = factory.get('/', {'letter': 'o'})

        with self.assertNumQueries(2):
            response = view(request).render()

        # Check that the plays have been filter to remove those with the letter 'o'
        # But the poems haven't been affected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                'play': [
                    {'title': "A Midsummer Night's Dream", 'genre': 'Comedy', 'year': 1600},
                    {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
                ]
            },
            {
                'poem': [
                    {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                    {'title': "As a decrepit father takes delight", 'style': 'Sonnet'},
                    {'title': "A Lover's Complaint", 'style': 'Narrative'}
                ]
            }
        ])

    def test_search_filter_view(self):
        """
        Tests use of built in DRF filtering with MultipleModelAPIView
        """

        view = SearchFilterView.as_view()

        request = factory.get('/', {'search': 'as'})

        with self.assertNumQueries(2):
            response = view(request).render()

        # Check first page of results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                'play': [
                    {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623},
                ]
            },
            {
                'poem': [
                    {'title': "As a decrepit father takes delight", 'style': 'Sonnet'},
                ]
            }
        ])

    def test_base_viewset(self):
        """
        Tests the Base MutlipleModelAPIViewSet with the default settings
        """
        client = APIClient()
        response = client.get('/viewset/', format='api')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, [
            {'play': [
                {'title': 'Romeo And Juliet', 'genre': 'Tragedy', 'year': 1597},
                {'title': "A Midsummer Night's Dream", 'genre': 'Comedy', 'year': 1600},
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
                {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623},
            ]
            },
            {'poem': [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]}
        ])


@override_settings(ROOT_URLCONF=__name__)
class TestMMVHTMLRenderer(TestCase):

    def setUp(self):
        Play.objects.bulk_create([
            Play(title='Romeo And Juliet',
                 genre='Tragedy',
                 year=1597),
            Play(title="A Midsummer Night's Dream",
                 genre='Comedy',
                 year=1600),
            Play(title='Julius Caesar',
                 genre='Tragedy',
                 year=1623),
            Play(title='As You Like It',
                 genre='Comedy',
                 year=1623)
        ])

        Poem.objects.bulk_create([
            Poem(title="Shall I compare thee to a summer's day?",
                 style="Sonnet"),
            Poem(title="As a decrepit father takes delight",
                 style="Sonnet"),
            Poem(title="A Lover's Complaint",
                 style="Narrative")
        ])

        """
        Monkeypatch get_template
        Taken from DRF Tests
        """
        self.get_template = django.template.loader.get_template

        def get_template(template_name, dirs=None):
            if template_name == 'test.html':
                return Template("<html>test: {{ data }}</html>")
            raise TemplateDoesNotExist(template_name)

        def select_template(template_name_list, dirs=None, using=None):
            if template_name_list == ['test.html']:
                return Template("<html>test: {{ data }}</html>")
            raise TemplateDoesNotExist(template_name_list[0])

        django.template.loader.get_template = get_template
        django.template.loader.select_template = select_template

    def test_html_renderer(self):
        """
        Testing bug in which results dict failed to be passed into template context
        """

        client = APIClient()
        response = client.get('/template', {'format': 'html'})

        # test the data is formatted properly and shows up in the template
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertContains(response, "Tragedy")
        self.assertContains(response, "<html>")
        self.assertContains(response, "decrepit")

        # test that the JSONRenderer does NOT add the dictionary wrapper to the data
        response = client.get('/template?format=json')

        # test the data is formatted properly and shows up in the template
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('data', response.data)
        self.assertNotIn('<html>', response)

    def tearDown(self):
        """
        Revert monkeypatching
        """
        django.template.loader.get_template = self.get_template
