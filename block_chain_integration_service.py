import logging.config
import os
from flask import Flask, Blueprint
from src.common.settings import *
from src.api.restplus import api
from src.database import db
import sys, traceback

import sqlalchemy

from src.api.service.endpoints.service_accounts_namespace import ns as service_accounts_namespace
from src.api.service.endpoints.service_channels_namespace import ns as service_channels_namespace
from src.api.service.endpoints.service_ccs_namespace import ns as service_ccs_namespace
from src.api.service.endpoints.service_settlement_namespace import ns as service_settlement_namespace
from src.api.service.endpoints.service_withdraw_namespace import ns as service_withdraw_namespace
from src.api.service.endpoints.service_maintenance_namespace import ns as service_maintenance_namespace

from src.state.serverstate import ServerState
from src.callback.call_back_service import CallBackService
from src.blockchain.service.blockchain_service import BlockChainService
from src.monitoring.bc_monitoring import BCMonitorService
from src.monitoring.db_monitor import DBMonitorService
from src.blockchain.common.utils.utils_json import Utils

from src.utils.repeated_timer import RepeatedTimer
from time import sleep


def get_json_pathes():
    my_path = os.path.abspath(os.path.dirname(__file__))
    token_abi_path = os.path.join(my_path, "src/blockchain/common/ABI/{}".format(ERC20_TOKEN_JSON))
    adp_channel_manager_path = os.path.join(my_path,
                                            "src/blockchain/common/ABI/{}".format(ADPCHANNEL_MANAGER_JSON))
    adp_channel_path = os.path.join(my_path, "src/blockchain/common/ABI/{}".format(ADPCHANNEL_JSON))

    log.info('get json pathes token:{}, channel_manager{} channel:{}'.format(token_abi_path,
                                                                             adp_channel_manager_path,
                                                                             adp_channel_path))

    return adp_channel_manager_path, adp_channel_path, token_abi_path


app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

adp_channel_manager_path, adp_channel_path, token_abi_path = get_json_pathes()
channel_manager_json = Utils.read_json(adp_channel_manager_path)
channel_json = Utils.read_json(adp_channel_path)
token_abi = Utils.read_json(token_abi_path)
log.info(
    'block_chain_integration_service.create BlockChainService->token_abi:{} ADPCHANNEL_MANAGER_ADDRESS:{} channel_manager_json["abi"]:{} channel_json["abi"]:{}'.format(
        token_abi,
        ADPCHANNEL_MANAGER_ADDRESS,
        channel_manager_json["abi"],
        channel_json["abi"]))
blockchain_service = BlockChainService(token_abi=token_abi,
                                       adp_channel_manager_address=ADPCHANNEL_MANAGER_ADDRESS,
                                       adp_channel_manager_abi=channel_manager_json["abi"],
                                       adp_channel_abi=channel_json["abi"])


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


def db_monitor(app):
    log.info('>>>>> "run db monitor ..."  <<<<<')
    try:
        log.info('>>>>> "try run db monitor ..."  <<<<<')
        with app.app_context():
            commands_to_do = DBMonitorService().get_commands_to_do(app)
            if commands_to_do:
                log.info('blockchain integration service  handle {} commands'.format(str(len(commands_to_do))))
                blockchain_service.perform_commands(commands_to_do)
                log.info('>>>>> "perform_commands done "  <<<<<')
            else:
                log.info('>>>>> "no  commands_to_do "  <<<<<')
    except Exception as expected:
        traceback.print_exc()
        e = sys.exc_info()[0]
        log.info('db_monitor Error: %s' % e)
        # traceback.print_exc(file=sys.stdout)
        return


def monitor(app):
    log.info('>>>>> "run bc monitor ..."  <<<<<')
    try:
        with app.app_context():
            BCMonitorService().monitor(app)
        return
    except Exception as error:
        traceback.print_exc()
        e = sys.exc_info()[0]
        log.info('monitor Error: %s' % e)
        return


def do_nothing():
    log.info('>>>>> "run do nothing ..."  <<<<<')


def print_setting():
    print(FLASK_DEBUG)

    print(FLASK_SERVER_HOST)
    print(FLASK_SERVER_HOST_DEBUG)
    print(FLASK_SERVER_PORT)
    print(FLASK_SERVER_PORT_DEBUG)

    # Flask-Restplus settings
    print(RESTPLUS_SWAGGER_UI_DOC_EXPANSION)
    print(RESTPLUS_VALIDATE)
    print(RESTPLUS_MASK_SWAGGER)
    print(RESTPLUS_ERROR_404_HELP)

    # SQLAlchemy settings
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    print(SQLALCHEMY_DATABASE_HOST)
    print(SQLALCHEMY_DATABASE_PORT)
    print(SQLALCHEMY_DATABASE_DATABASE)
    print(SQLALCHEMY_DATABASE_USER)
    print(SQLALCHEMY_DATABASE_PASSWORD)
    print(SQLALCHEMY_DATABASE_URI)
    # SQLALCHEMY_DATABASE_URI = 'postgresql://itps_admin:itps_admin@itps-staging.ctyhtso2qejb.us-east-1.rds.amazonaws.com:5432/itps_staging'
    print(SQLALCHEMY_TRACK_MODIFICATIONS)

    # ___________________ BC Setting ____________________

    print(ITPS_SERVICE_ADDRESS)
    print(ITPS_SERVICE_PRIVATE_KEY)

    print(NODE_PROTOCOL)
    print(NODE_PORT)
    print(NODE_HOST)

    print(ADPCHANNEL_MANAGER_ADDRESS)
    print(ADPCHANNEL_MANAGER_JSON)
    print(ADPCHANNEL_JSON)
    print(ERC20_TOKEN_JSON)

    # replace with real CLIENT_SYSTEM_ADDRESS for production
    print(CLIENT_SYSTEM_ADDRESS)
    print(TRX_GRACETIME)

    print(GAS_PRICE)
    # GAS_PRICE * 1000
    print(GAS_LIMIT_CHANNEL_CREATION)
    print(GAS_LIMIT_WITHDRAW)
    print(GAS_LIMIT_SETTLEMENT)

    print(EMPTY_CHANNEL)
    print(TRANSFER_EVENT_NAME)
    print(SETTLEMENT_EVENT_NAME)
    print(TOKEN_DEPOSIT_EVENT_NAME)
    print(TOKEN_WITHDRAW_EVENT_NAME)

    print(BC_MONITOR_INTERVAL)

    print(RUN_MONITOR)
    print(TRANSFER_AMOUNT)


def main():
    initialize_app(app)

    print_setting()
    
    # db_monitor(app)
    # monitor(app)

    if RUN_MONITOR:
        log.info('>>>>>  "Starting periodic monitoring.... Interval:*{}*"  <<<<<'.format(BC_MONITOR_INTERVAL))
        rt_db = RepeatedTimer(BC_MONITOR_INTERVAL, db_monitor, app)  # it auto-starts, no need of rt.start()

        log.info('>>>>>  "Starting bc monitoring.... Interval:*{}*"  <<<<<'.format(BC_MONITOR_INTERVAL))
        rt_bc = RepeatedTimer(BC_MONITOR_INTERVAL, monitor, app)  # it auto-starts, no need of rt.start()
    else:
        log.info('>>>>>  "Starting bc monitoring.... Interval:*{}*"  <<<<<'.format(BC_MONITOR_INTERVAL))
        rt_bc = RepeatedTimer(BC_MONITOR_INTERVAL*100, do_nothing, None)  # it auto-starts, no need of rt.start()



if __name__ == "__main__":
    main()
