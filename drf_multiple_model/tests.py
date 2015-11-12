from django.db import models
from django.test import TestCase, override_settings
from django.conf.urls import url

from rest_framework import serializers, status, renderers
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient

from drf_multiple_model.views import MultipleModelAPIView

from collections import OrderedDict

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
        fields = ('genre','title','year')

class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = ('title','style')


# Views

# For testing that the default settings behave normally
class BasicTestView(MultipleModelAPIView):
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

class TestBrowsableAPIView(MultipleModelAPIView):
    renderer_classes = (renderers.BrowsableAPIRenderer,)

    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

# Testing label functionality
class LabelTestView(MultipleModelAPIView):
    queryList = ((Play.objects.all(),PlaySerializer,'The Plays'),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer,'The Sonnets'))

# For no label, set add_model_type to False
class BasicNoLabelView(MultipleModelAPIView):
    add_model_type = False
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

# Testing flat, without labels
class BasicFlatView(MultipleModelAPIView):
    flat = True
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

# Testing sort
class OrderedFlatView(MultipleModelAPIView):
    flat = True
    sorting_field = 'title'
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

# Testing incorrect sort
class OrderedWrongView(MultipleModelAPIView):
    flat = True
    sorting_field = 'year'
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

# Testing No Label
class FlatNoLabelView(MultipleModelAPIView):
    flat = True
    add_model_type = False
    queryList = ((Play.objects.all(),PlaySerializer),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer))

# Testing label functionality when flat
class FlatLabelView(MultipleModelAPIView):
    flat = True
    queryList = ((Play.objects.all(),PlaySerializer,'Drama'),
                 (Poem.objects.filter(style="Sonnet"),PoemSerializer,'Poetry'))

# Testing missing queryList
class BrokenView(MultipleModelAPIView):
    pass

# Testing get_queryList function
class DynamicQueryView(MultipleModelAPIView):
    def get_queryList(self):
        title = self.kwargs['play'].replace('-',' ')

        queryList = ((Play.objects.filter(title=title),PlaySerializer),
                     (Poem.objects.filter(style="Sonnet"),PoemSerializer))

        return queryList

# Fake URL Patterns for running tests
urlpatterns = [
    url(r"^$",TestBrowsableAPIView.as_view()),
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
        """

        view = BasicTestView.as_view()
        

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data),2)
        self.assertEqual(response.data,[
            { 'play': [
                    {'title':'Romeo And Juliet','genre':'Tragedy','year':1597},
                    {'title':"A Midsummer Night's Dream",'genre':'Comedy','year':1600},
                    {'title':'Julius Caesar','genre':'Tragedy','year':1623},
                    {'title':'As You Like It','genre':'Comedy','year':1623},
                ]
            },
            { 'poem': [
                    {'title':"Shall I compare thee to a summer's day?",'style':'Sonnet'},
                    {'title':"As a decrepit father takes delight",'style':'Sonnet'}
            ]}
        ]);


    def test_post(self):
        """
        POST requests should throw a 405 Error 
        """
        view = BasicTestView.as_view()

        data = {'fake': 'data'}
        request = factory.post('/',data,format='json')

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
        request = factory.put('/',data,format='json')

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

    def test_no_label(self):
        """
        Tests that no label (aka add_model_type = False) just gives the data
        """

        view = BasicNoLabelView.as_view()
        

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data),2)
        self.assertEqual(response.data,[
            [
                {'title':'Romeo And Juliet','genre':'Tragedy','year':1597},
                {'title':"A Midsummer Night's Dream",'genre':'Comedy','year':1600},
                {'title':'Julius Caesar','genre':'Tragedy','year':1623},
                {'title':'As You Like It','genre':'Comedy','year':1623},
            ],
            [
                {'title':"Shall I compare thee to a summer's day?",'style':'Sonnet'},
                {'title':"As a decrepit father takes delight",'style':'Sonnet'}
            ]
        ]);
        
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

        self.assertEqual(len(response.data),2)
        self.assertIn('The Plays',response.data[0].keys())
        self.assertIn('The Sonnets',response.data[1].keys())

    def test_simple_flat(self):
        """
        Putting flat=True should flatten the data to a single list of elements
        """

        view = BasicFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data),6)
        self.assertEqual(response.data,[
            OrderedDict([('genre','Tragedy'),('title','Romeo And Juliet'),('year',1597),('type', 'play')]),
            OrderedDict([('genre','Comedy'),('title',"A Midsummer Night's Dream"),('year',1600),('type', 'play')]),
            OrderedDict([('genre','Tragedy'),('title','Julius Caesar'),('year',1623),('type', 'play')]),
            OrderedDict([('genre','Comedy'),('title','As You Like It'),('year',1623),('type', 'play')]),
            OrderedDict([('title',"Shall I compare thee to a summer's day?"),('style','Sonnet'),('type', 'poem')]),
            OrderedDict([('title',"As a decrepit father takes delight"),('style','Sonnet'),('type', 'poem')]),
        ])

    def test_ordered_flat(self):
        """
        Adding the sorting_field attribute should order the flat items according to whatever field 
        """

        view = OrderedFlatView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(len(response.data),6)
        self.assertEqual(response.data,[
            OrderedDict([('genre','Comedy'),('title',"A Midsummer Night's Dream"),('year',1600),('type', 'play')]),
            OrderedDict([('genre','Comedy'),('title','As You Like It'),('year',1623),('type', 'play')]),
            OrderedDict([('title',"As a decrepit father takes delight"),('style','Sonnet'),('type', 'poem')]),
            OrderedDict([('genre','Tragedy'),('title','Julius Caesar'),('year',1623),('type', 'play')]),
            OrderedDict([('genre','Tragedy'),('title','Romeo And Juliet'),('year',1597),('type', 'play')]),
            OrderedDict([('title',"Shall I compare thee to a summer's day?"),('style','Sonnet'),('type', 'poem')]),
        ])

    def test_ordered_wrong_sorting(self):
        """
        Sorting by a non-shared field should throw a KeyError
        """

        view = OrderedWrongView.as_view()

        request = factory.get('/')
        self.assertRaises(KeyError,view,request)

    def test_flat_no_label(self):
        """
        Putting flat=True should flatten the data to a single list of elements
        """

        view = FlatNoLabelView.as_view()

        request = factory.get('/')
        with self.assertNumQueries(2):
            response = view(request).render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data),6)
        self.assertEqual(response.data,[
            OrderedDict([('genre','Tragedy'),('title','Romeo And Juliet'),('year',1597)]),
            OrderedDict([('genre','Comedy'),('title',"A Midsummer Night's Dream"),('year',1600)]),
            OrderedDict([('genre','Tragedy'),('title','Julius Caesar'),('year',1623)]),
            OrderedDict([('genre','Comedy'),('title','As You Like It'),('year',1623)]),
            OrderedDict([('title',"Shall I compare thee to a summer's day?"),('style','Sonnet')]),
            OrderedDict([('title',"As a decrepit father takes delight"),('style','Sonnet')]),
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

        self.assertEqual(len(response.data),6)
        self.assertEqual(response.data,[
            OrderedDict([('genre','Tragedy'),('title','Romeo And Juliet'),('year',1597),('type', 'Drama')]),
            OrderedDict([('genre','Comedy'),('title',"A Midsummer Night's Dream"),('year',1600),('type', 'Drama')]),
            OrderedDict([('genre','Tragedy'),('title','Julius Caesar'),('year',1623),('type', 'Drama')]),
            OrderedDict([('genre','Comedy'),('title','As You Like It'),('year',1623),('type', 'Drama')]),
            OrderedDict([('title',"Shall I compare thee to a summer's day?"),('style','Sonnet'),('type', 'Poetry')]),
            OrderedDict([('title',"As a decrepit father takes delight"),('style','Sonnet'),('type', 'Poetry')]),
        ])

    def test_missing_queryList(self):
        """
        not specifying a queryList or a get_queryList should raise an AssertionError
        """

        view = BrokenView.as_view()

        request = factory.get('/')

        self.assertRaises(AssertionError,view,request)

    def test_dynamic_queryList(self):
        """
        using get_QueryList allows the construction of dynamic queryLists
        """

        view = DynamicQueryView.as_view()

        request = factory.get('/Julius-Caesar')
        with self.assertNumQueries(2):
            response = view(request,play="Julius-Caesar")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data),2)
        self.assertEqual(response.data,[
            { 'play': [
                    {'title':'Julius Caesar','genre':'Tragedy','year':1623},
                ]
            },
            { 'poem': [
                    {'title':"Shall I compare thee to a summer's day?",'style':'Sonnet'},
                    {'title':"As a decrepit father takes delight",'style':'Sonnet'}
            ]}
        ]);


    def test_url_endpoint(self):
        """
        DRF 3.3 broke the MultipleModelAPIView with a get_queryset call
        This test is to replicate (and then fix) that problem
        """

        client = APIClient()
        response = client.get('/',format='api')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

