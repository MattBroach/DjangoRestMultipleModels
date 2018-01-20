from rest_framework.test import APIRequestFactory
from rest_framework import status

from .utils import MultipleModelTestCase
from .models import Play, Poem
from .serializers import PlaySerializer, PoemSerializer
from drf_multiple_model.views import ObjectMultipleModelAPIView, FlatMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination


factory = APIRequestFactory()


class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 2


class ObjectLimitPaginationView(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.all(), 'serializer_class': PoemSerializer},
    )


class FlatLimitPaginationView(FlatMultipleModelAPIView):
    pagination_class = LimitPagination
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.all(), 'serializer_class': PoemSerializer},
    )


class LimitPaginationTests(MultipleModelTestCase):
    def test_basic_object_pagination(self):
        view = ObjectLimitPaginationView.as_view()

        request = factory.get('/')

        # Additional queries for getting counts
        with self.assertNumQueries(4):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Each response should contain the same number of items as the limit
        self.assertEqual(len(response.data['results']['Play']), 2)
        self.assertEqual(len(response.data['results']['Poem']), 2)

        # The count should be equal to the greatest count value/table size
        self.assertEqual(response.data['highest_count'], 4)
        self.assertEqual(response.data['overall_total'], 7)

        # check that links are properly formed
        self.assertEqual(response.data['next'], 'http://testserver/?limit=2&offset=2')
        self.assertEqual(response.data['previous'], None)

        # check second page of results
        request = factory.get('/', {'offset': 2})
        response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # There are only three Poems, so this response should have only 1 Poem, but 2 Plays
        self.assertEqual(len(response.data['results']['Play']), 2)
        self.assertEqual(len(response.data['results']['Poem']), 1)

        # The count values should not change
        self.assertEqual(response.data['highest_count'], 4)
        self.assertEqual(response.data['overall_total'], 7)

        # Check the new links
        self.assertEqual(response.data['previous'], 'http://testserver/?limit=2')
        self.assertEqual(response.data['next'], None)

    def test_basic_flat_pagination(self):
        view = FlatLimitPaginationView.as_view()

        request = factory.get('/')

        # Additional queries for getting counts
        with self.assertNumQueries(4):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Results length should be number_querylist_items * limit
        self.assertEqual(len(response.data['results']), 4)

        # The count should be equal to the greatest count value/table size
        self.assertEqual(response.data['highest_count'], 4)
        self.assertEqual(response.data['overall_total'], 7)

        # check that links are properly formed
        self.assertEqual(response.data['next'], 'http://testserver/?limit=2&offset=2')
        self.assertEqual(response.data['previous'], None)

        # check second page of results
        request = factory.get('/', {'offset': 2})
        response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # There are only three Poems, so this response should have only 1 Poem, but 2 Plays
        self.assertEqual(len(response.data['results']), 3)

        # The count values should not change
        self.assertEqual(response.data['highest_count'], 4)
        self.assertEqual(response.data['overall_total'], 7)

        # Check the new links
        self.assertEqual(response.data['previous'], 'http://testserver/?limit=2')
        self.assertEqual(response.data['next'], None)
