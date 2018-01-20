from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework import routers, status

from .utils import MultipleModelTestCase
from .models import Play, Poem
from .serializers import PlaySerializer, PoemSerializer
from drf_multiple_model.viewsets import FlatMultipleModelAPIViewSet, ObjectMultipleModelAPIViewSet


class FlatViewSet(FlatMultipleModelAPIViewSet):
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
    )


class ObjectViewSet(ObjectMultipleModelAPIViewSet):
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
    )


# Routers for testing viewset
router = routers.SimpleRouter()
router.register(r'flat', FlatViewSet, base_name='flat')
router.register(r'object', ObjectViewSet, base_name='object')

urlpatterns = router.urls


# TESTS
@override_settings(ROOT_URLCONF=__name__)
class TestMMObjectViews(MultipleModelTestCase):
    maxDiff = None

    def test_object_viewset(self):
        """
        Tests the ObjectMutlipleModelAPIViewSet with the default settings
        """
        client = APIClient()
        response = client.get('/object/', format='api')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, {
            'Play': [
                {'title': 'Romeo And Juliet', 'genre': 'Tragedy', 'year': 1597},
                {'title': "A Midsummer Night's Dream", 'genre': 'Comedy', 'year': 1600},
                {'title': 'Julius Caesar', 'genre': 'Tragedy', 'year': 1623},
                {'title': 'As You Like It', 'genre': 'Comedy', 'year': 1623},
            ],
            'Poem': [
                {'title': "Shall I compare thee to a summer's day?", 'style': 'Sonnet'},
                {'title': "As a decrepit father takes delight", 'style': 'Sonnet'}
            ]
        })

    def test_flat_viewset(self):
        """
        Tests the ObjectMutlipleModelAPIViewSet with the default settings
        """
        client = APIClient()
        response = client.get('/flat/', format='api')
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
