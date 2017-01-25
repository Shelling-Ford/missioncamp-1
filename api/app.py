from datetime import date
from flask import Flask
from flask_restful import Resource, Api

from core.database import DB
from core.models import Camp
from .flask_restful_ext.generics import APIViewMixin, ListAPIViewMixin

APP = Flask(__name__)
API = Api(APP)


class CampView(Resource, APIViewMixin):
    queryset = DB.session.query(Camp)
    lookup_field = Camp.idx
    fields = ('idx', 'year', 'term', 'name', 'code', 'startday', 'campday')

    def get(self, idx):
        return self.response(self.queryset.filter(Camp.idx == idx).one().__dict__)


class CampListView(Resource, ListAPIViewMixin):
    queryset = DB.session.query(Camp)
    fields = ('idx', 'year', 'term', 'name', 'code', 'startday', 'campday')

    def get(self):
        return self.response(self.queryset.all())


API.add_resource(CampView, '/camp/<idx>')
API.add_resource(CampListView, '/camps')
