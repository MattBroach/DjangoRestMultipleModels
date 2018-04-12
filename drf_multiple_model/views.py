from drf_multiple_model.mixins import FlatMultipleModelMixin, ObjectMultipleModelMixin

from rest_framework.generics import GenericAPIView


class FlatMultipleModelAPIView(FlatMultipleModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        super(GenericAPIView, self).initial(request, *args, **kwargs)
        if self.sorting_parameter_name in request.query_params:
            # Extract sorting parameter from query string
            self.sorting_field = request.query_params.get(self.sorting_parameter_name)

        if self.sorting_field:
            # Handle sorting direction and sorting field mapping
            self.sort_descending = self.sorting_field[0] == '-'
            if self.sort_descending:
                self.sorting_field = self.sorting_field[1:]
            self.sorting_field = self.sorting_fields_map.get(self.sorting_field, self.sorting_field)

    def get_queryset(self):
        return None


class ObjectMultipleModelAPIView(ObjectMultipleModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return None
