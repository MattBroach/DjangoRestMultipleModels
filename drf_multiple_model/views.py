from drf_multiple_model.mixins import FlatMultipleModelMixin, ObjectMultipleModelMixin

from rest_framework.generics import GenericAPIView


class FlatMultipleModelAPIView(FlatMultipleModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if 'o' in request.query_params:
            sorting_parameter = request.query_params.get(self.sorting_parameter_name)
            self.sorting_field = self.sorting_fields_map.get(sorting_parameter.lstrip('-'), sorting_parameter)

    def get_queryset(self):
        return None


class ObjectMultipleModelAPIView(ObjectMultipleModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return None
