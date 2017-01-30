import hashlib
import json
from flask import request
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
        serializer = self.serializer_class(data)
        return marshal(serializer.data, serializer.resource_fields)


class ListAPIView(APIView):
    def __init__(self):
        super().__init__()

    def list(self, **kwargs):
        queryset = self.get_queryset()
        return queryset.limit(20).offset(0).all()

    @require_auth
    def get(self, **kwargs):
        data = self.list(**kwargs)
        if len(data) > 0:
            serializer = self.serializer_class(data, many=True)
            return marshal(serializer.data, serializer.resource_fields)
        return list()


class ListCreateAPIView(ListAPIView):
    def create(self):
        def parse_request(k, v):
            if "__" not in k:
                return k, v
            else:
                parent, child = k.split("__")
                return parent, dict(parse_request(child, v))

        form_data = dict()
        for k, v in request.form.items():
            key, value = parse_request(k, v)
            form_data[key] = value

        serializer = self.serializer_class()
        model_object = serializer.deserialize(form_data)
        DB.session.add(model_object)
        DB.session.commit()

    @require_auth
    def put(self, **kwargs):
        try:
            self.create()
            return {"status": "success"}, 201
        except Exception as e:
            raise e
            return {"status": "failed"}, 400


class RetrieveUpdateAPIView(APIView):
    def get_etag(self, obj):
        serializer = self.serializer_class(obj)
        serialized_data = marshal(serializer.data, serializer.resource_fields)
        return hashlib.sha512(json.dumps(serialized_data).encode()).hexdigest()[:40]

    @require_auth
    def get(self, **kwargs):
        data = self.get_data(**kwargs)
        serializer = self.serializer_class(data)
        serialized_data = marshal(serializer.data, serializer.resource_fields)
        serialized_data['_etag'] = self.get_etag(data)
        return serialized_data

    @require_auth
    def patch(self, **kwargs):
        data = self.get_data(**kwargs)
        etag = self.get_etag(data)

        def parse_request(k, v):
            if "__" not in k:
                return k, v
            else:
                parent, child = k.split("__")
                return parent, dict(parse_request(child, v))

        form_data = dict()
        for k, v in request.form.items():
            key, value = parse_request(k, v)
            form_data[key] = value

        if etag != form_data['_etag']:
            return {"status": "failed", "message": "Mismatch: etags"}, 412
