from flask import Flask
from flask_restful import Resource, Api

from core.database import DB
from core.models import Area, Camp, Member, Group
from .flask_restful_ext.generics import APIViewMixin, ListAPIViewMixin, APIView
from .flask_restful_ext.auth import require_auth

from .serializers import AreaSerializer

APP = Flask(__name__)
API = Api(APP)


class AreaView(APIView):
    serializer_class = AreaSerializer


class AreaListView(Resource, ListAPIViewMixin):
    queryset = DB.session.query(Area)

    @require_auth
    def get(self, **kwargs):
        if 'camp_code' in kwargs:
            return self.response(Area.get_list(kwargs['camp_code'], use_model=True))
        return self.response(self.queryset.all())


class CampView(Resource, APIViewMixin):
    queryset = DB.session.query(Camp)
    lookup_field = Camp.idx

    @require_auth
    def get(self, idx):
        return self.response(self.queryset.filter(Camp.idx == idx).one().__dict__)


class CampListView(Resource, ListAPIViewMixin):
    queryset = DB.session.query(Camp)

    @require_auth
    def get(self):
        return self.response(self.queryset.all())


class MemberView(Resource, APIViewMixin):
    queryset = DB.session.query(Member)
    lookup_field = Member.idx

    @require_auth
    def get(self, idx):
        return self.response(self.queryset.filter(Member.idx == idx).one().__dict__)


class MemberListView(Resource, ListAPIViewMixin):
    queryset = DB.session.query(Member)

    @require_auth
    def get(self):
        limit = 20
        offset = 0
        return self.response(self.queryset.limit(limit).offset(offset).all())


class GroupView(Resource, APIViewMixin):
    queryset = DB.session.query(Group)
    lookup_field = Group.idx

    @require_auth
    def get(self, idx):
        return self.response(self.queryset.filter(Group.idx == idx).one().__dict__)


API.add_resource(AreaView, '/area/<idx>')
API.add_resource(AreaListView, '/areas')
API.add_resource(AreaListView, '/areas/<camp_code>', endpoint="areas_by_camp")
API.add_resource(CampView, '/camp/<idx>')
API.add_resource(CampListView, '/camps')
API.add_resource(MemberView, '/member/<idx>')
API.add_resource(MemberListView, '/members')
API.add_resource(GroupView, '/group/<idx>')
