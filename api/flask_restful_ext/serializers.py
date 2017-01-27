from datetime import date

from flask_restful import fields
from .models import DateField


class BaseSerializer:
    class Meta:
        model_class = None
        fields = None

    def __init__(self, many=False):
        self.many = many
        self.meta = self.Meta()
        self._model_class = self.meta.model_class

        if not hasattr(self.meta, 'fields'):
            def attr_gen():
                for attr in dir(self._model_class):
                    if not attr.startswith("_"):
                        yield attr

            self._fields = tuple(attr_gen())
        else:
            self._fields = self.meta.fields

        if not hasattr(self.meta, 'lookup_field'):
            self._lookup_field = None
        else:
            self._lookup_field = self.meta.lookup_field

    def get_lookup_field(self):
        return self._lookup_field

    def get_model_class(self):
        return self._model_class

    def serialize(self):
        raise NotImplementedError

    def get_default_fields(self):
        raise NotImplementedError


class ModelSerializer(BaseSerializer):
    def serialize(self, obj):
        attributes = dir(obj)
        data = dict()
        for k in attributes:
            v = getattr(obj, k)
            if k in self._fields:
                if hasattr(self, k) and isinstance(getattr(self, k), BaseSerializer):
                    data[k] = getattr(self, k).serialize(v)
                else:
                    data[k] = v
        return data

    def get_default_fields(self, obj):
        attributes = dir(obj)
        resource_fields = dict()
        for k in attributes:
            if k in self._fields:
                v = getattr(obj, k)
                if isinstance(v, date):
                    resource_fields[k] = DateField
                elif isinstance(v, str):
                    resource_fields[k] = fields.String
                elif isinstance(v, int):
                    resource_fields[k] = fields.Integer
                else:
                    if hasattr(self, k) and isinstance(getattr(self, k), BaseSerializer):
                        child_serializer = getattr(self, k)
                        if child_serializer.many:
                            resource_fields[k] = fields.List(fields.Nested(child_serializer.get_default_fields(v[0])))
                        else:
                            resource_fields[k] = fields.Nested(child_serializer.get_default_fields(v))
        return resource_fields


class MapModelSerializer(BaseSerializer):
    def serialize(self, obj_list):
        data = dict()
        for obj in obj_list:
            if obj.key in data:
                if isinstance(data[obj.key], list):
                    data[obj.key].append(obj.value)
                else:
                    data[obj.key] = [data[obj.key], obj.value]
            else:
                data[obj.key] = obj.value
        return data

    def get_default_fields(self, obj_list):
        resource_fields = dict()
        for obj in obj_list:
            if obj.key not in resource_fields:
                resource_fields[obj.key] = fields.String
        return resource_fields
