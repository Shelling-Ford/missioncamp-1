from .flask_restful_ext.serializers import ModelSerializer
from core.models import Area, Camp, Member, Group


class AreaSerializer(ModelSerializer):
    class Meta:
        model_class = Area
        lookup_field = 'idx'


class CampSerializer(ModelSerializer):
    class Meta:
        model_class = Camp
        lookup_field = 'idx'


class MemberSerializer(ModelSerializer):
    class Meta:
        model_class = Member
        lookup_field = 'idx'


class GroupSerializer(ModelSerializer):
    class Meta:
        model_class = Group
        lookup_field = 'idx'
