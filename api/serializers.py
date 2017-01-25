from .flask_restful_ext.serializers import ModelSerializer
from core.models import Area


class AreaSerializer(ModelSerializer):
    class Meta:
        model_class = Area
        lookup_field = 'idx'
