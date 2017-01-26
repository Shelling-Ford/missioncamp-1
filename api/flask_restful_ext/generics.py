from datetime import date
from flask_restful import Resource
from ..flask_restful_ext.auth import require_auth


def populate_dict(fields, source):
    del source['_sa_instance_state']

    result_dict = dict()
    for key, value in source.items():
        if fields is None or key in fields:
            if isinstance(value, date):
                result_dict[key] = value.strftime("%Y-%m-%d")
            else:
                result_dict[key] = value
    return result_dict


class APIView(Resource):
    serializer_class = None
    queryset = None
    lookup_field = None

    def __init__(self):
        super().__init__()
        self.serializer = self.serializer_class()
        self._fields = self.serializer.get_fields()
        self._lookup_field = self.serializer.get_lookup_field()
        self._model_class = self.serializer.get_model_class()

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return self.serializer.get_queryset()

    @require_auth
    def get(self, **kwargs):
        queryset = self.get_queryset()

        model_class = self._model_class
        lookup_field = self._lookup_field
        data = queryset.filter(getattr(model_class, lookup_field) == kwargs[lookup_field]).one().__dict__
        return self.response(data)

    def response(self, source):
        return populate_dict(self._fields, source)


class ListAPIView(APIView):
    def __init__(self):
        super().__init__()

    @require_auth
    def get(self, **kwargs):
        queryset = self.get_queryset()

        # model_class = self._model_class
        # lookup_field = self._lookup_field
        data = queryset.limit(20).offset(0).all()
        return self.response(data)

    def response(self, source):
        return list(populate_dict(self._fields, row.__dict__) for row in source)
