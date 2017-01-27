from flask_restful import Resource, marshal

from core.database import DB
from ..flask_restful_ext.auth import require_auth


class APIView(Resource):
    serializer_class = None
    queryset = None
    lookup_field = None

    def __init__(self):
        super().__init__()
        self.serializer = self.serializer_class()
        self._lookup_field = self.serializer.get_lookup_field()
        self._model_class = self.serializer.get_model_class()

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        model_class = self._model_class
        return DB.session.query(model_class)

    def get_data(self, **kwargs):
        queryset = self.get_queryset()
        model_class = self._model_class
        lookup_field = self._lookup_field
        data = queryset.filter(getattr(model_class, lookup_field) == kwargs[lookup_field]).one()
        return data

    @require_auth
    def get(self, **kwargs):
        data = self.get_data(**kwargs)
        resource_fields = self.serializer.get_default_fields(data)
        serialized_data = self.serializer.serialize(data)
        return marshal(serialized_data, resource_fields)


class ListAPIView(APIView):
    def __init__(self):
        super().__init__()

    def get_data(self, **kwargs):
        queryset = self.get_queryset()
        return queryset.limit(20).offset(0).all()

    @require_auth
    def get(self, **kwargs):
        data = self.get_data(**kwargs)
        if len(data) > 0:
            resource_fields = self.serializer.get_default_fields(data[0])
            return marshal(list(self.serializer.serialize(d) for d in data), resource_fields)
        return list()
