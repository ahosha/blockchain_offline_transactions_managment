import logging.config
import os
from flask import Flask, Blueprint
from src.common.settings import *
from src.api.restplus import api
from src.database import db
import sys, traceback
from src.utils.utils_http import HTTPHelper
from src.common.consts import *
from src.utils.repeated_timer import RepeatedTimer

from src.api.service.endpoints.service_accounts_namespace import ns as service_accounts_namespace
from src.api.service.endpoints.service_channels_namespace import ns as service_channels_namespace
from src.api.service.endpoints.service_ccs_namespace import ns as service_ccs_namespace
from src.api.service.endpoints.service_settlement_namespace import ns as service_settlement_namespace
from src.api.service.endpoints.service_withdraw_namespace import ns as service_withdraw_namespace
from src.api.service.endpoints.service_maintenance_namespace import ns as service_maintenance_namespace

from src.monitoring.db_monitor import DBMonitorService

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)


def configure_app(flask_app):
    if FLASK_DEBUG:
        flask_app.config['FLASK_SERVER_NAME'] = '{}:{}'.format(FLASK_SERVER_HOST_DEBUG,
                                                               FLASK_SERVER_PORT_DEBUG)
    else:
        flask_app.config['FLASK_SERVER_NAME'] = '{}:{}'.format(FLASK_SERVER_HOST,
                                                               FLASK_SERVER_PORT)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI.format(SQLALCHEMY_DATABASE_USER,
                                                                                 SQLALCHEMY_DATABASE_PASSWORD,
                                                                                 SQLALCHEMY_DATABASE_HOST,
                                                                                 SQLALCHEMY_DATABASE_PORT,
                                                                                 SQLALCHEMY_DATABASE_DATABASE)
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = RESTPLUS_ERROR_404_HELP

    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI.format(SQLALCHEMY_DATABASE_USER,
                                                                           SQLALCHEMY_DATABASE_PASSWORD,
                                                                           SQLALCHEMY_DATABASE_HOST,
                                                                           SQLALCHEMY_DATABASE_PORT,
                                                                           SQLALCHEMY_DATABASE_DATABASE)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'itps'


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(service_accounts_namespace)
    api.add_namespace(service_channels_namespace)
    api.add_namespace(service_ccs_namespace)
    api.add_namespace(service_settlement_namespace)
    api.add_namespace(service_withdraw_namespace)
    api.add_namespace(service_maintenance_namespace)

    flask_app.register_blueprint(blueprint)

    db.init_app(flask_app)


def post_settlement(ext_account_id=None, sender_withdrawal_amount=None):
    # settlement flow (receiver)
    # {
    #     "ext_account_id_to_settle": "Account2805",
    #     "sender_withdrawal_amount": 0
    # }
    if not sender_withdrawal_amount:
        sender_withdrawal_amount = 0

    if FLASK_DEBUG:
        base_url = "{}:{}".format(FLASK_SERVER_HOST_DEBUG, FLASK_SERVER_PORT_DEBUG)
    else:
        base_url = "{}:{}".format(FLASK_SERVER_HOST, FLASK_SERVER_PORT)

    print(base_url)

    post_settlement_url = "{}://{}/{}".format(API_PROTOCOL, base_url, POST_SETTLEMENT_PART)
    payload = {}
    payload['ext_account_id_to_settle'] = ext_account_id
    payload['sender_withdrawal_amount'] = sender_withdrawal_amount
    HTTPHelper().post_to_url(final_url=post_settlement_url, payload=payload)
    return


def scheduled_settlement(app):
    log.info('>>>>> "run scheduled settlement flow ..."  <<<<<')
    try:
        log.info('>>>>> "try run scheduled settlement flow ..."  <<<<<')
        with app.app_context():
            settlements_to_do = DBMonitorService().get_settlements_to_do(app)
            if settlements_to_do:
                log.info('scheduled settlement service  handle {} commands'.format(str(len(settlements_to_do))))
                for settlement in settlements_to_do:
                    post_settlement(ext_account_id=settlement)
                log.info('>>>>> "scheduled settlement done "  <<<<<')
            else:
                log.info('>>>>> "no  settlements_to_do "  <<<<<')
    except Exception as expected:
        traceback.print_exc()
        e = sys.exc_info()[0]
        log.info('scheduled_settlement Error: %s' % e)
        return


def main():
    initialize_app(app)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['FLASK_SERVER_NAME']))

    # scheduled_settlement(app)

    log.info('>>>>>  "Starting scheduled settlement .... Interval:*{}*"  <<<<<'.format(SCHEDULED_SETTLEMENT_INTERVAL))
    rt_bc = RepeatedTimer(SCHEDULED_SETTLEMENT_INTERVAL, scheduled_settlement, app)

    if FLASK_DEBUG:
        @app.before_first_request
        def create_tables():
            db.create_all()

        app.run(debug=True, host=FLASK_SERVER_HOST_DEBUG, port=FLASK_SERVER_PORT_DEBUG)
        log.info('>>>>> Starting development server at http://{} <<<<<'.format(app.config['FLASK_SERVER_NAME']))
    else:
        app.run(debug=True, host=FLASK_SERVER_HOST, port=FLASK_SERVER_PORT)
        log.info('>>>>> Starting development server at http://{} <<<<<'.format(app.config['FLASK_SERVER_NAME']))


if __name__ == "__main__":
    main()
