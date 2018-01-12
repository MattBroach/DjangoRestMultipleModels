from rest_framework import serializers, status, renderers, \
    pagination, filters
# Views



class TestBrowsableAPIView(BasicTestView):
    renderer_classes = (renderers.BrowsableAPIRenderer,)


# Testing PageNumberPagination
# class BasicPagination(pagination.PageNumberPagination):
    # page_size = 5
    # page_size_query_param = 'page_size'
    # max_page_size = 10


# class PageNumberPaginationView(BasicFlatView):
    # pagination_class = BasicPagination


# # Testing LinitOffsetPagination
# class LimitPagination(pagination.LimitOffsetPagination):
    # default_limit = 5
    # max_limit = 15


# class LimitOffsetPaginationView(BasicFlatView):
    # pagination_class = LimitPagination


# Testing Base Viewset



# Tests
class TestMMViews(TestCase):



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



