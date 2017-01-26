from flask import Flask
from flask_restful import Api

from .flask_restful_ext.generics import APIView, ListAPIView
from .serializers import AreaSerializer, CampSerializer, MemberSerializer, GroupSerializer

APP = Flask(__name__)
API = Api(APP)


class AreaView(APIView):
    serializer_class = AreaSerializer


class AreaListView(ListAPIView):
    serializer_class = AreaSerializer


class CampView(APIView):
    serializer_class = CampSerializer


class CampListView(ListAPIView):
    serializer_class = CampSerializer


class MemberView(APIView):
    serializer_class = MemberSerializer


class MemberListView(ListAPIView):
    serializer_class = MemberSerializer


class GroupView(APIView):
    serializer_class = GroupSerializer


API.add_resource(AreaView, '/area/<idx>')
API.add_resource(AreaListView, '/areas')
API.add_resource(AreaListView, '/areas/<camp_code>', endpoint="areas_by_camp")
API.add_resource(CampView, '/camp/<idx>')
API.add_resource(CampListView, '/camps')
API.add_resource(MemberView, '/member/<idx>')
API.add_resource(MemberListView, '/members')
API.add_resource(GroupView, '/group/<idx>')
