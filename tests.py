import logging.config
import os
from sqlalchemy.orm.attributes import flag_modified
from flask import Flask, Blueprint
from src.common.settings import *
from src.api.restplus import api
from src.database import db
import requests
import json
import sys
# ,tracebacks
import uuid
import time
from datetime import datetime

from src.utils.utils_http import HTTPHelper
from src.api.service.endpoints.service_accounts_namespace import ns as service_accounts_namespace
from src.api.service.endpoints.service_channels_namespace import ns as service_channels_namespace
from src.api.service.endpoints.service_ccs_namespace import ns as service_ccs_namespace
from src.api.service.endpoints.service_settlement_namespace import ns as service_settlement_namespace
from src.api.service.endpoints.service_withdraw_namespace import ns as service_withdraw_namespace
from src.api.service.endpoints.service_maintenance_namespace import ns as service_maintenance_namespace

from src.database.models.channel_model import Channel
from src.blockchain.common.utils.utils_json import Utils

from src.blockchain.common.bc_helper import BlockChainHelper
from src.blockchain.service.rpc_provider import RPCProvider
from src.blockchain.service.erc20token import ERC20Token
from src.blockchain.service.blockchain_service import BlockChainService
from src.blockchain.service.adp_channel import ADPChannelBC
from src.blockchain.service.adp_channel_manager import ADPChannelManagerBC


def get_json_pathes():
    my_path = os.path.abspath(os.path.dirname(__file__))
    token_abi_path = os.path.join(my_path, "src/blockchain/common/ABI/{}".format(ERC20_TOKEN_JSON))
    adp_channel_manager_path = os.path.join(my_path,
                                            "src/blockchain/common/ABI/{}".format(ADPCHANNEL_MANAGER_JSON))
    adp_channel_path = os.path.join(my_path, "src/blockchain/common/ABI/{}".format(ADPCHANNEL_JSON))
    return adp_channel_manager_path, adp_channel_path, token_abi_path


app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

if TESTER_DEBUG:
    base_uri = '{}:{}'.format(FLASK_SERVER_HOST, FLASK_SERVER_PORT)
else:
    base_uri = TEST_API_BASE_URL

post_account_part = 'api/accounts/'
post_ccs_part = 'api/ccs/'
get_channel_part = 'api/channels/'
post_settlement_part = 'api/settlement/'
post_withdraw_part = 'api/withdraw/'

token_address = "0x102199295fc31f2298a05136affcad9d68233ead"

adp_channel_manager_path, adp_channel_path, token_abi_path = get_json_pathes()
channel_manager_json = Utils.read_json(adp_channel_manager_path)
channel_json = Utils.read_json(adp_channel_path)
token_abi = Utils.read_json(token_abi_path)

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

    # postgresql_connect(user='itps_admin',
    #                    password='itps_admin',
    #                    db='itps_staging',
    #                    host='itps-staging.ctyhtso2qejb.us-east-1.rds.amazonaws.com',
    #                    port=5432)

    # monitor(flask_app)

    # log.info('>>>>>  "Starting bc monitoring.... Interval: {}"  <<<<<'.format(BC_MONITOR_INTERVAL))
    # rt = RepeatedTimer(1, monitor, flask_app)  # it auto-starts, no need of rt.start()


def main():
    initialize_app(app)

    action_string = """"select action(1 - create address, 2 - generate signature,
    3 - transfer, 4 - post account flow, 5 - get channel flow, 6 - post ccs flow,
    7 - settlement flow, 8 - withdraw flow,
    9 - ccs )""".replace('\n', ' ')

    action = input(action_string)

    web3 = RPCProvider().create_rpc_provider()

    if action == '1':
        # create address
        gen_address(web3)
        print("create address done")
    elif action == '2':
        # generate signature
        gen_signature()
        print("generate signature done")
    elif action == '3':
        # transfer
        transfer(web3)
        print("transfer done")
    elif action == '4':
        # post account
        public_key, private_key, ext_account_id = post_account(web3)
        print(" post account flow done")
    elif action == '5':
        # get channel
        ext_account_id = input('ext_account_id:')
        get_channel(web3, ext_account_id)
        print("get channel flow done")
    elif action == '6':
        #  post ccs flow
        ext_account_id = post_ccs_flow(web3)
        print("post ccs flow done")
    elif action == '7':
        ext_account_id = input('ext_account_id:')
        sender_withdrawal_amount = input('sender_withdrawal_amount:')
        post_settlement(web3, ext_account_id)
        print("post settlement flow done")
    elif action == '8':
        ext_account_id = input('ext_account_id:')
        post_withdraw(web3, ext_account_id)
        print("post withdraw flow done")
    elif action == '9':
        #  post ccs flow
        ext_account_id = post_ccs(web3)
        print("post ccs done")
    else:
        print("wrong action")


def post_settlement(web3, ext_account_id=None, sender_withdrawal_amount=None):
    # settlement flow (receiver)
    # {
    #     "ext_account_id_to_settle": "Account2805",
    #     "sender_withdrawal_amount": 0
    # }
    if not ext_account_id:
        ext_account_id = post_ccs_flow(web3)
    if not sender_withdrawal_amount:
        sender_withdrawal_amount = 0
    post_account_url = "http://{}/{}".format(base_uri, post_settlement_part)
    payload = {}
    payload['ext_account_id_to_settle'] = ext_account_id

    payload['sender_withdrawal_amount'] = sender_withdrawal_amount
    response_text, response_status_code, response_reason = HTTPHelper().post_to_url(final_url=post_account_url,
                                                                                    payload=payload)

    print('response_text:{}, response_status_code:{}, response_reason:{}'.format(response_text,
                                                                                 response_status_code,
                                                                                 response_reason))


def post_withdraw(web3, ext_account_id=None):
    if not ext_account_id:
        ext_account_id = post_ccs_flow(web3)
    # /api/withdraw/?ext_account_id=account1
    post_withdraw_url = "http://{}/{}".format(base_uri, post_withdraw_part)
    payload = {}
    payload['ext_account_id'] = ext_account_id
    withdraw_params = {'ext_account_id': ext_account_id}
    response_text, response_status_code, response_reason = HTTPHelper().post_to_url(payload=payload,
                                                                                    final_url=post_withdraw_url,
                                                                                    params=withdraw_params)
    print('response_text:{}, response_status_code:{}, response_reason:{}'.format(response_text,
                                                                                 response_status_code,
                                                                                 response_reason))


def post_ccs(web3):
    # post ccs
    ext_account_id = input('ext_account_id:')
    channel_responce = get_channel(web3=web3, ext_account_id=ext_account_id)
    channel_responce = channel_responce.replace('\n', ' ')
    print('channel after transfer:{} '.format(channel_responce))
    channel_json_after_transfer = json.loads(channel_responce)
    if channel_json_after_transfer['channel_capacity'] > 0:
        private_key = input('pk:')
        transfer_amount = input("transfer_amount:")
        transfer_amount = float(transfer_amount)/100000000
        nonce = input("nonce:")
        total_paid_to_receiver = input("total_paid_to_receiver:")
        total_paid_to_receiver = float(total_paid_to_receiver)/100000000
        post_ccs_call(ext_account_id, nonce, private_key, total_paid_to_receiver, transfer_amount, token_address)

    return ext_account_id


def post_ccs_flow(web3):
    # post ccs
    public_key, private_key, ext_account_id = post_account(web3)
    save_pk_to_file(ext_account_id, private_key)

    print(str(datetime.now()) + ' sleep 60 sec ')
    time.sleep(60)
    channel_responce = get_channel(web3=web3, ext_account_id=ext_account_id)
    channel_responce = channel_responce.replace('\n', ' ')
    channel_json = json.loads(channel_responce)
    channel_address = channel_json['channel_address']

    transfer(web3=web3, token_address=token_address, transfer_amount=TRANSFER_AMOUNT, channel_address=channel_address)
    print(str(datetime.now()) + ' sleep 60 sec ')
    time.sleep(60)
    # add update channel db from channel bc
    channel_responce_after_transfer = get_channel(web3=web3, ext_account_id=ext_account_id)
    channel_responce_after_transfer = channel_responce_after_transfer.replace('\n', ' ')
    print('channel after transfer:{} '.format(channel_responce_after_transfer))
    channel_json_after_transfer = json.loads(channel_responce_after_transfer)
    if channel_json_after_transfer['channel_capacity'] > 0:
        transfer_amount = 1 / 100000000
        # input("transfer_amount:")
        nonce = 1
        # input("nonce:")
        total_paid_to_receiver = 1 / 100000000
        # input("total_paid_to_receiver:")
        post_ccs_call(ext_account_id, nonce, private_key, total_paid_to_receiver, transfer_amount)

        transfer_amount = 1 / 100000000
        nonce = 2
        total_paid_to_receiver = 2 / 100000000
        post_ccs_call(ext_account_id, nonce, private_key, total_paid_to_receiver, transfer_amount)

    return ext_account_id


def save_pk_to_file(ext_account_id, private_key):
    import os
    dir_path = os.path.dirname(os.path.abspath(__file__))
    coll_path = os.path.join(dir_path, "pk.txt")
    with open(coll_path, 'a') as coll:
        new_string = ext_account_id + "  " + private_key
        coll.write("%r\n" % new_string)
    return


def post_ccs_call(ext_account_id, nonce, private_key, total_paid_to_receiver, transfer_amount):
    print(
        "post_ccs_call ext_account_id:{} , nonce:{} , private_key:{} , total_paid_to_receiver:{} , transfer_amount:{} ".format(
            ext_account_id, nonce, private_key, total_paid_to_receiver, transfer_amount))
    # add check capasity from db > 0
    post_ccs_url = "http://{}/{}".format(base_uri, post_ccs_part)
    # transfer_amount_for_sign = BlockChainHelper().transfer_token_decimal_to_bc(token_address,
    #                                                                            transfer_amount)
    transfer_amount_for_sign = int(transfer_amount * 100000000)
    sender_signature = gen_signature(nonce=nonce, amount_for_signature=transfer_amount_for_sign, pk_sender=private_key)

    # {
    #     "ext_account_id": "Account2805",
    #     "transfer_amount": 1,
    #     "ccs": {
    #         "nonce": 8,
    #         "total_paid_to_receiver": 8,
    #         "receiver_signature": "string",
    #         "sender_signature": "0x874c5a08e321ac51cdbfa056417b3edede096d69cc84680670fae1bcd71ccc7129127b622774958335d5acc1b532f534214c703c7748da4aa856c49f703721a71c",
    #         "channel_status": "string",
    #         "last_settled_nonce": 0,
    #         "available_for_withdrawal_to_sender": 0,
    #         "available_for_withdrawal_to_receiver": 0,
    #         "available_for_settlement_to_sender": 0,
    #         "available_for_settlement_to_receiver": 0
    #     }
    # }
    payload = {}
    payload['ext_account_id'] = ext_account_id
    payload['transfer_amount'] = float(transfer_amount)
    payload['ccs'] = {}
    payload['ccs']['nonce'] = int(nonce)
    payload['ccs']['total_paid_to_receiver'] = float(total_paid_to_receiver)
    payload['ccs']['receiver_signature'] = ""
    payload['ccs']['sender_signature'] = BlockChainHelper().hex_of_signature(sender_signature)
    payload['ccs']['channel_status'] = "0"
    payload['ccs']['last_settled_nonce'] = 0
    payload['ccs']['available_for_withdrawal_to_sender'] = 0
    payload['ccs']['available_for_withdrawal_to_receiver'] = 0
    payload['ccs']['available_for_settlement_to_sender'] = 0
    payload['ccs']['available_for_settlement_to_receiver'] = 0

    response_text, response_status_code, response_reason = HTTPHelper().post_to_url(final_url=post_ccs_url,
                                                                                    payload=payload)
    print('response_text:{}, response_status_code:{}, response_reason:{}'.format(response_text,
                                                                                 response_status_code,
                                                                                 response_reason))


def get_channel(web3, ext_account_id=None):
    # http://itps-1010825944.us-east-1.elb.amazonaws.com/api/channels/?ext_account_id=account1
    if not ext_account_id:
        public_key, private_key, ext_account_id = post_account(web3)
    get_channel_url = "http://{}/{}".format(base_uri, get_channel_part)
    payload = {'ext_account_id': ext_account_id}
    response_text, response_status_code, response_reason = get_from_url(payload=payload,
                                                                        final_url=get_channel_url)
    print('response_text:{}, response_status_code:{}, response_reason:{}'.format(response_text,
                                                                                 response_status_code,
                                                                                 response_reason))
    return response_text


def get_from_url(payload, final_url):
    try:
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate'}
        response = requests.get(url=final_url, params=payload, headers=headers)
        print(response.url)
        print(response.text)  # TEXT/HTML
        print(response.status_code, response.reason)  # HTTP
        return response.text, response.status_code, response.reason
    except Exception as expected:
        e = sys.exc_info()[0]
        print('post_to_url Error: %s' % e)
        pass


def post_account(web3):
    public_key, private_key = gen_address(web3)
    post_account_url = "http://{}/{}".format(base_uri, post_account_part)
    ext_account_id = str(uuid.uuid4())
    payload = {}
    payload['ext_account_id'] = ext_account_id
    payload['user_public_key'] = public_key
    payload['token_address'] = token_address
    # {
    #     "ext_account_id": "Account2904",
    #     "user_public_key": "0x4a0D9b254F2a9bdD17E68411881767a83867d0c1",
    #     "token_address": "0x102199295fc31f2298a05136affcad9d68233ead"
    # }
    response_text, response_status_code, response_reason = HTTPHelper().post_to_url(final_url=post_account_url,
                                                                                    payload=payload)
    print('response_text:{}, response_status_code:{}, response_reason:{}'.format(response_text,
                                                                                 response_status_code,
                                                                                 response_reason))
    return public_key, private_key, ext_account_id


def transfer(web3, token_address=None, transfer_amount=None, channel_address=None):
    if not token_address:
        token_address = input("token_address:")
    if not transfer_amount:
        transfer_amount = input("transfer_amount:")
    if not channel_address:
        channel_address = input("channel_address:")
    print('token_address:_{}_ transfer_amount:_{}_ channel_address:_{}_'.format(token_address, transfer_amount,
                                                                                channel_address))
    erc20_token = blockchain_service.get_erc20_token(token_address)
    erc20_token.transfer(transfer_amount=int(transfer_amount), channel_address=channel_address)

    return


def gen_signature(nonce=None, amount_for_signature=None, pk_sender=None):
    if not nonce:
        nonce = input("nonce:")
    if not amount_for_signature:
        amount_for_signature = input("amount_for_signature:")
    if not pk_sender:
        pk_sender = input("pk_sender:")
    signature = compose_signature(amount_for_signature, nonce, pk_sender)
    print("signature:" + BlockChainHelper().hex_of_signature(signature))
    return signature


def compose_signature(amount_for_signature, nonce, pk_sender):
    sha3_message = BlockChainHelper().create_message_sha3(int(nonce), int(amount_for_signature))
    print('test-> compose_signature nonce:{} amount_for_signature:{} sha3_message:{}'.format(nonce,
                                                                                             amount_for_signature,
                                                                                             sha3_message))
    signature = BlockChainHelper().prepare_sender_signature_sha3(sha3_message,
                                                                 pk_sender)
    return signature


def gen_address(web3):
    passphrase = 'KEYSMASH FJAFJKLDSKF7JKFDJ 1530'
    account = web3.eth.account.create('%s' % passphrase)
    address_sender = account.address
    pk_sender = web3.toHex(account.privateKey)
    print("public_key:" + address_sender)
    print("private_key:" + pk_sender)
    return address_sender, pk_sender


if __name__ == "__main__":
    main()
