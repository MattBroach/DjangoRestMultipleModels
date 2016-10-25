from rest_framework.viewsets import GenericViewSet

from drf_multiple_model.mixins import MultipleModelMixin


class MultipleModelAPIViewSet(MultipleModelMixin, GenericViewSet):

    def get_queryset(self):
        return
