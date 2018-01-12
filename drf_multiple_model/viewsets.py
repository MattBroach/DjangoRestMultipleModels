from rest_framework.viewsets import GenericViewSet

from drf_multiple_model.mixins import FlatMultipleModelMixin, ObjectMultipleModelMixin


class FlatMultipleModelAPIViewSet(FlatMultipleModelMixin, GenericViewSet):
    pass


class ObjectMultipleModelAPIViewSet(ObjectMultipleModelMixin, GenericViewSet):
    pass
