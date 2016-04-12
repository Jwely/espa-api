from flask import request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.interfaces.admin.version0 import API


espa = API()


class AdminConfig(Resource):
    def get(self, key=None):
        return espa.configuration_management(key=key)

    def post(self, key):
        val = request.get_json()

        return espa.configuration_management(key=key, value=val)

    def put(self, key):
        val = request.get_json()

        return espa.configuration_management(key=key, value=val)

    def delete(self, key):
        return espa.configuration_management(key=key, delete=True)


class AdminOrder(Resource):
    pass


class AdminProcessing(Resource):
    pass


class AdminSystems(Resource):
    pass


class AdminStorage(Resource):
    pass
