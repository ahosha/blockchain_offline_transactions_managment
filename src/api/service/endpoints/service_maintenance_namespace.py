import logging

from flask_restplus import Resource
from src.api.restplus import api


log = logging.getLogger(__name__)

ns = api.namespace('service', description='Operations related to maintenance')


@ns.route('/healthcheck/')
class Healthcheck(Resource):
    def get(self):
        str_health_check = "Health check done"
        return str_health_check, 200

