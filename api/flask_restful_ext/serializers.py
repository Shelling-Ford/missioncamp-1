from datetime import date, datetime

from flask_restful import fields
from .models import DateField, DateTimeField


class BaseSerializer:
    class Meta:
        model_class = None
        fields = None

    def __init__(self, obj=None, many=False):
        self.obj = obj
        self.many = many
        self.meta = self.Meta()

        if not hasattr(self.meta, 'fields'):
            def attr_gen():
                for attr in dir(self.meta.model_class):
                    if not attr.startswith("_"):
                        yield attr

            self._fields = tuple(attr_gen())
        else:
            self._fields = self.meta.fields

        self.resource_fields = dict()
        self.data = self._get_data()

    def get_lookup_field(self):
        if not hasattr(self.meta, 'lookup_field'):
            return None
        else:
            return self.meta.lookup_field

    def get_model_class(self):
        return self.meta.model_class

    def _get_data(self):
        if self.obj is None:
            return {}
        else:
            if self.many:
                return list(self.serialize_many(self.obj))
            else:
                return self.serialize(self.obj)

    def serialize(self):
        raise NotImplementedError

    def serialize_many(self, obj_list):
        if type(obj_list) is not list:
            raise ValueError("serialize_many requires list type argument")
        for obj in obj_list:
            yield self.serialize(obj)


class ModelSerializer(BaseSerializer):
    def serialize(self, obj):
        def _determine_field_type(v):
            if type(v) is datetime:
                return DateTimeField
            if type(v) is date:
                return DateField
            if type(v) is str:
                return fields.String
            if type(v) is int:
                return fields.Integer

            return None

        attributes = dir(obj)
        data = dict()
        for k in attributes:
            if k in self._fields:
                v = getattr(obj, k)
                if hasattr(self, k) and isinstance(getattr(self, k), BaseSerializer):
                    child = getattr(self, k)
                    if child.many:
                        data[k] = child.serialize_many(v)
                        self.resource_fields[k] = fields.List(fields.Nested(child.resource_fields))
                    else:
                        data[k] = child.serialize(v)
                        self.resource_fields[k] = fields.Nested(child.resource_fields)
                else:
                    data[k] = v
                    field_type = _determine_field_type(v)
                    if field_type is not None:
                        self.resource_fields[k] = field_type
        return data

    def deserialize(self, data):
        model_object = self.meta.model_class()
        for k, v in data.items():
            if k in self._fields:
                if hasattr(self, k) and isinstance(getattr(self, k), BaseSerializer):
                    child_object = getattr(self, k).deserialize(v)
                    setattr(model_object, k, child_object)
                else:
                    setattr(model_object, k, v)
        return model_object


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

            if obj.key not in self.resource_fields:
                self.resource_fields[obj.key] = fields.String
        return data
