from drf_multiple_model.mixins import MultipleModelMixin

from rest_framework.generics import GenericAPIView


class MultipleModelAPIView(MultipleModelMixin, GenericAPIView):

    def get_queryset(self):
        return

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
