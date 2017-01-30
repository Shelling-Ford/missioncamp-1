from .flask_restful_ext.serializers import ModelSerializer, MapModelSerializer
from core.models import Area, Camp, Member, Membership, Group, Payment, Room


class AreaSerializer(ModelSerializer):
    class Meta:
        model_class = Area
        lookup_field = 'idx'


class CampSerializer(ModelSerializer):
    class Meta:
        model_class = Camp
        lookup_field = 'idx'


class GroupSerializer(ModelSerializer):
    class Meta:
        model_class = Group
        lookup_field = 'idx'


class PaymentSerializer(ModelSerializer):
    class Meta:
        model_class = Payment
        lookup_field = 'idx'


class MembershipSerializer(MapModelSerializer):
    class Meta:
        model_class = Membership
        lookup_field = 'idx'
        fields = ('key', 'value')


class RoomSerializer(ModelSerializer):
    class Meta:
        model_class = Room
        lookup_field = 'idx'


class MemberSerializer(ModelSerializer):

    area = AreaSerializer()
    camp = CampSerializer()
    group = GroupSerializer()
    payment = PaymentSerializer()
    membership = MembershipSerializer()
    room = RoomSerializer()

    class Meta:
        model_class = Member
        lookup_field = 'idx'
