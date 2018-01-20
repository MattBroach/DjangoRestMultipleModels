import django.template.loader
from django.template import TemplateDoesNotExist, engines
from django.test import override_settings
from django.conf.urls import url
from rest_framework.test import APIClient
from rest_framework import renderers, status

from .utils import MultipleModelTestCase
from .models import Play, Poem
from .serializers import PlaySerializer, PoemSerializer
from drf_multiple_model.views import FlatMultipleModelAPIView


# Testing TemplateHTMLRenderer view bug
class HTMLRendererView(FlatMultipleModelAPIView):
    querylist = (
        {'queryset': Play.objects.all(), 'serializer_class': PlaySerializer},
        {'queryset': Poem.objects.filter(style="Sonnet"), 'serializer_class': PoemSerializer},
    )
    renderer_classes = (renderers.TemplateHTMLRenderer, renderers.JSONRenderer)
    template_name = 'test.html'


# Fake URL Patterns for running tests
urlpatterns = [
    url(r"^template$", HTMLRendererView.as_view()),
]


@override_settings(ROOT_URLCONF=__name__)
class TestMMVHTMLRenderer(MultipleModelTestCase):
    def setUp(self):
        super(TestMMVHTMLRenderer, self).setUp()

        """
        Monkeypatch get_template
        Taken from DRF Tests
        """
        self.get_template = django.template.loader.get_template

        def get_template(template_name, dirs=None):
            if template_name == 'test.html':
                return engines['django'].from_string("<html>test: {{ data }}</html>")
            raise TemplateDoesNotExist(template_name)

        def select_template(template_name_list, dirs=None, using=None):
            if template_name_list == ['test.html']:
                return engines['django'].from_string("<html>test: {{ data }}</html>")
            raise TemplateDoesNotExist(template_name_list[0])

        django.template.loader.get_template = get_template
        django.template.loader.select_template = select_template

    def test_html_renderer(self):
        """
        Testing bug in which results dict failed to be passed into template context
        """
        client = APIClient()
        response = client.get('/template', format='html')

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
