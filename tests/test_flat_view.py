from django.test import override_settings
from django.core.exceptions import ValidationError
from django.conf.urls import url
from django.core.cache import cache
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status, filters

from .utils import MultipleModelTestCase
from .models import Play, Poem, Author
from .serializers import PlaySerializer, PoemSerializer, PlayWithAuthorSerializer, PoemWithAuthorSerializer, \
    AuthorListSerializer
from drf_multiple_model.views import FlatMultipleModelAPIView

factory = APIRequestFactory()


# Regular Views
class BasicFlatView(FlatMultipleModelAPIView):
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
    )


class SortedFlatView(BasicFlatView):
    sorting_field = 'title'


class ReversedFlatView(BasicFlatView):
    sorting_field = '-title'


class SortingFlatView(FlatMultipleModelAPIView):
    sorting_fields_map = {'author': 'author__name'}

    querylist = (
        {'queryset': Play.objects.select_related('author'), 'serializer_class': PlayWithAuthorSerializer},
        {
            'queryset': Poem.objects.select_related('author').filter(style="Sonnet"),
            'serializer_class': PoemWithAuthorSerializer
        },
    )


class SortingMultipleFieldsFlatView(SortingFlatView):
    sorting_fields = ['type', 'title']


class ReversedSortingMultipleFieldsFlatView(SortingFlatView):
    sorting_fields = ['-type', 'title']


class SortingFlatViewListData(FlatMultipleModelAPIView):
    sorting_field = 'plays'
    querylist = (
        {'queryset': Author.objects.prefetch_related('plays', 'poems'), 'serializer_class': AuthorListSerializer},
    )


class CustomSortingParamFlatView(SortingFlatView):
    sorting_parameter_name = 'custom_o'


class NoLabelView(BasicFlatView):
    add_model_type = False


class CustomLabelView(FlatMultipleModelAPIView):
    querylist = (
        {
            'queryset': Play.objects.all(),
            'serializer_class': PlaySerializer,
            'label': 'Drama',
        },
        {
            'queryset': Poem.objects.filter(style="Sonnet"),
            'serializer_class': PoemSerializer,
            'label': 'Poetry',
        },
    )


class DynamicQueryView(FlatMultipleModelAPIView):
    def get_querylist(self):
        title = self.kwargs['play'].replace('-', ' ')

        querylist = (
            {'queryset': Play.objects.filter(title=title), 'serializer_class': PlaySerializer},
            {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
        )

        return querylist


class SearchFilterView(BasicFlatView):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title',)


# Testing filter_fn
def title_without_letter(queryset, request, *args, **kwargs):
    letter_to_exclude = request.query_params['letter']
    return queryset.exclude(title__icontains=letter_to_exclude)


class FilterFnView(FlatMultipleModelAPIView):
    querylist = (
        {
            'queryset': Play.objects.all(),
            'serializer_class': PlaySerializer,
            'filter_fn': title_without_letter,
        },
        {
            'queryset': Poem.objects.filter(style="Sonnet"),
            'serializer_class': PoemSerializer,
        },
    )


class CachedQueryView(FlatMultipleModelAPIView):
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
    )

    def load_queryset(self, query_data, request, *args, **kwargs):
        queryset = cache.get('{}-queryset'.format(query_data['queryset'].model.__name__))
        if not queryset:
            queryset = query_data['queryset'].all()
            cache.set('{}-queryset'.format(query_data['queryset'].model.__name__), queryset)
        return queryset


# Broken Views
class NoQuerylistView(FlatMultipleModelAPIView):
    pass


class NoQuerysetView(FlatMultipleModelAPIView):
    querylist = [
        {'serializer_class': PlaySerializer},
        {'serializer_class': PoemSerializer},
    ]


class NoSerializerClassView(FlatMultipleModelAPIView):
    querylist = [
        {'queryset': Play.objects.all()},
        {'queryset': Poem.objects.all()},
    ]


class WrongSortFieldView(BasicFlatView):
    sorting_field = 'year'


urlpatterns = [
    url(r'^$', BasicFlatView.as_view()),
]


# TESTS
@override_settings(ROOT_URLCONF=__name__)
class TestMMFlatViews(MultipleModelTestCase):
    maxDiff = None
    sorted_results = [
        {'genre': 'Comedy', 'title': 'A Midsummer Night\'s Dream', 'year': 1600, 'type': 'Play'},
        {'genre': 'Comedy', 'title': 'As You Like It', 'year': 1623, 'type': 'Play'},
        {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poem'},
        {'genre': 'Tragedy', 'title': 'Julius Caesar', 'year': 1623, 'type': 'Play'},
        {'genre': 'Tragedy', 'title': 'Romeo And Juliet', 'year': 1597, 'type': 'Play'},
        {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet', 'type': 'Poem'},
    ]
    sorted_results_w_author = [
        {'genre': 'Tragedy', 'title': 'Romeo And Juliet', 'year': 1597, 'author': {'name': 'Play Shakespeare 1'},
         'type': 'Play'},
        {'genre': 'Comedy', 'title': "A Midsummer Night's Dream", 'year': 1600,
         'author': {'name': 'Play Shakespeare 2'}, 'type': 'Play'},
        {'genre': 'Tragedy', 'title': 'Julius Caesar', 'year': 1623, 'author': {'name': 'Play Shakespeare 3'},
         'type': 'Play'},
        {'genre': 'Comedy', 'title': 'As You Like It', 'year': 1623, 'author': {'name': 'Play Shakespeare 4'},
         'type': 'Play'},
        {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet',
         'author': {'name': 'Poem Shakespeare 1'}, 'type': 'Poem'},
        {'title': 'As a decrepit father takes delight', 'style': 'Sonnet',
         'author': {'name': 'Poem Shakespeare 2'}, 'type': 'Poem'}
    ]
    unsorted_results = [
        {'genre': 'Tragedy', 'title': 'Romeo And Juliet', 'year': 1597, 'type': 'Play'},
        {'genre': 'Comedy', 'title': 'A Midsummer Night\'s Dream', 'year': 1600, 'type': 'Play'},
        {'genre': 'Tragedy', 'title': 'Julius Caesar', 'year': 1623, 'type': 'Play'},
        {'genre': 'Comedy', 'title': 'As You Like It', 'year': 1623, 'type': 'Play'},
        {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet', 'type': 'Poem'},
        {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poem'},
    ]

    def test_post(self):
        """
        POST requests should throw a 405 Error
        """
        view = BasicFlatView.as_view()

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
        view = BasicFlatView.as_view()

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
        view = BasicFlatView.as_view()

        request = factory.delete('/')

        with self.assertNumQueries(0):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})

    def test_no_querylist(self):
        """
        A view with no querylist and no `get_querylist` overwrite should raise
        an assertion error with the appropriate message
        """
        view = NoQuerylistView.as_view()

        request = factory.get('/')

        with self.assertRaises(AssertionError) as error:
            view(request).render()

        self.assertEqual(str(error.exception), (
            'NoQuerylistView should either include a `querylist` attribute, '
            'or override the `get_querylist()` method.'
        ))

    def test_no_queryset(self):
        """
        A querylist with no `queryset` key should raise a ValidationError with the
        appropriate message
        """
        view = NoQuerysetView.as_view()

        request = factory.get('/')

        with self.assertRaises(ValidationError) as error:
            view(request).render()

        self.assertEqual(error.exception.message, (
            'All items in the NoQuerysetView querylist attribute '
            'should contain a `queryset` key'
        ))

    def test_no_serializer_class(self):
        """
        A querylist with no `serializer_class` key should raise a ValidationError with the
        appropriate message
        """
        view = NoSerializerClassView.as_view()

        request = factory.get('/')

        with self.assertRaises(ValidationError) as error:
            view(request).render()

        self.assertEqual(error.exception.message, (
            'All items in the NoSerializerClassView querylist attribute '
            'should contain a `serializer_class` key'
        ))

    def test_basic_flat_view(self):
        """
        The default setting for the `FlatMultipleModelView` should return
        the serialized objects in querylist order
        """
        view = BasicFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, self.unsorted_results)

    def test_no_label(self):
        """
        Tests that no label (aka add_model_type = False) just gives the data
        """
        view = NoLabelView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [{k: v for k, v in i.items() if k != 'type'} for i in self.unsorted_results])

    def test_new_labels(self):
        """
        Adding the 'label' key to queryList elements should use those labels
        instead of the model names
        """
        view = CustomLabelView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            {'genre': 'Tragedy', 'title': 'Romeo And Juliet', 'year': 1597, 'type': 'Drama'},
            {'genre': 'Comedy', 'title': 'A Midsummer Night\'s Dream', 'year': 1600, 'type': 'Drama'},
            {'genre': 'Tragedy', 'title': 'Julius Caesar', 'year': 1623, 'type': 'Drama'},
            {'genre': 'Comedy', 'title': 'As You Like It', 'year': 1623, 'type': 'Drama'},
            {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet', 'type': 'Poetry'},
            {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poetry'},
        ])

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
            {'genre': 'Comedy', 'title': 'A Midsummer Night\'s Dream', 'year': 1600, 'type': 'Play'},
            {'genre': 'Tragedy', 'title': 'Julius Caesar', 'year': 1623, 'type': 'Play'},
            {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet', 'type': 'Poem'},
            {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poem'},
        ])

    def test_sorted_flat(self):
        """
        Adding the sorting_field attribute should order the flat items according to whatever field
        """
        view = SortedFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, self.sorted_results)

    def test_reverse_sorted(self):
        """
        Adding a '-' to the front of the sorting_field attribute should order the
        flat items in reverse
        """
        view = ReversedFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, list(reversed(self.sorted_results)))

    def test_sorting_by_request_parameter(self):
        """
        Adding the sorting_field attribute should order the flat items according to whatever field
        """
        view = SortingFlatView.as_view()

        for sorting_arg in ('author', '-author'):
            request = factory.get('/?o={}'.format(sorting_arg))
            with self.assertNumQueries(2):
                response = view(request).render()

            self.assertEqual(len(response.data), 6)
            self.assertEqual(response.data, list(reversed(self.sorted_results_w_author))
                             if '-' in sorting_arg else self.sorted_results_w_author)

    def test_sorting_by_custom_request_parameter(self):
        """
        Adding the sorting_field attribute should order the flat items according to whatever field
        """
        view = CustomSortingParamFlatView.as_view()

        for sorting_arg in ('author', '-author'):
            request = factory.get('/?custom_o={}'.format(sorting_arg))
            with self.assertNumQueries(2):
                response = view(request).render()

            self.assertEqual(len(response.data), 6)
            self.assertEqual(response.data, list(reversed(self.sorted_results_w_author))
                             if '-' in sorting_arg else self.sorted_results_w_author)

    def test_sorting_list_attribute_failure(self):
        """
        Attempts to sort by data value that is a list should fail
        """
        view = SortingFlatViewListData.as_view()
        request = factory.get('/')
        self.assertRaises(ValidationError, view, request, msg='Invalid sorting field: year')

    def test_sorting_by_multiple_parameters(self):
        """
        Sorting by multiple fields should work
        """
        view = SortingMultipleFieldsFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data, sorted(
                sorted(self.sorted_results_w_author, key=lambda x: x['title']),
                key=lambda x: x['type'],
            )
        )

    def test_sorting_by_multiple_parameters_reversed(self):
        """
        Sorting by multiple fields in descending order should work
        """
        view = ReversedSortingMultipleFieldsFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data, sorted(
                sorted(self.sorted_results_w_author, key=lambda x: x['title']),
                key=lambda x: x['type'],
                reverse=True
            )
        )

    def test_sorting_by_multiple_parameters_via_request(self):
        """
        Sorting by multiple fields should work
        """
        view = SortingFlatView.as_view()
        request = factory.get('/?o=type,-title')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data, sorted(
                sorted(self.sorted_results_w_author, key=lambda x: x['title'], reverse=True),
                key=lambda x: x['type']
            )
        )

    def test_ordered_wrong_sorting(self):
        """
        Sorting by a non-shared field should throw a KeyError
        """
        view = WrongSortFieldView.as_view()

        request = factory.get('/')
        self.assertRaises(ValidationError, view, request)

    def test_dynamic_querylist(self):
        """
        using get_querylist allows the construction of dynamic queryLists
        """
        view = DynamicQueryView.as_view()

        request = factory.get('/Julius-Caesar')
        with self.assertNumQueries(2):
            response = view(request, play="Julius-Caesar")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data, [
            {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623, 'type': 'Play'},
            {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet', 'type': 'Poem'},
            {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poem'}
        ])

    def test_search_filter_view(self):
        """
        Tests use of built in DRF filtering with FlatMultipleModelAPIView
        """
        view = SearchFilterView.as_view()

        request = factory.get('/', {'search': 'as'})

        with self.assertNumQueries(2):
            response = view(request).render()

        # Check first page of results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623, 'type': 'Play'},
            {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poem'},
        ])

    def test_url_endpoint(self):
        """
        DRF 3.3 broke the MultipleModelAPIView with a load_queryset call
        This test is to replicate (and then fix) that problem
        """
        client = APIClient()
        response = client.get('/', format='api')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cached_querylist(self):
        view = CachedQueryView.as_view()

        request = factory.get('/Julius-Caesar')
        with self.assertNumQueries(2):
            response = view(request, play="Julius-Caesar")
        with self.assertNumQueries(0):
            response = view(request, play="Julius-Caesar")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data, [
            {'genre': 'Tragedy', 'title': 'Romeo And Juliet', 'year': 1597, 'type': 'Play'},
            {'genre': 'Comedy', 'title': 'A Midsummer Night\'s Dream', 'year': 1600, 'type': 'Play'},
            {'genre': 'Tragedy', 'title': 'Julius Caesar', 'year': 1623, 'type': 'Play'},
            {'genre': 'Comedy', 'title': 'As You Like It', 'year': 1623, 'type': 'Play'},
            {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet', 'type': 'Poem'},
            {'title': "As a decrepit father takes delight", 'style': 'Sonnet', 'type': 'Poem'},
        ])
