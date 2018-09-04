import logging
import os
from flask import request
from flask_restplus import Resource
from src.api.service.serializers import channel_snapshot, settlement_data
from src.api.restplus import api
from src.business.business import *
from sqlalchemy.orm.attributes import flag_modified
from src.database.models.command_model import Command
from src.common.bc_commands import BCCommands, BCCommandsStatus

from src.blockchain.service.blockchain_service import BlockChainService
from src.common.settings import *
from src.blockchain.common.bc_helper import BlockChainHelper
from src.blockchain.common.utils.utils_json import Utils

log = logging.getLogger(__name__)

ns = api.namespace('settlement', description='Operations related to settlement')


@ns.route('/')
class Settlement(Resource):

    @api.expect(settlement_data, validate=True)
    @api.marshal_with(channel_snapshot)
    def post(self):
        """
         Initiates a new settlement. Set sender_withdrawal_amount to zero to indicate Client System - initiated settlement
        """
        request_data = request.json
        ext_account_id = request_data.get('ext_account_id_to_settle')
        sender_withdrawal_amount = request_data.get('sender_withdrawal_amount')
        # get external account id from db table account by account id
        account_from_db = Account.find_by_ext_account_id(ext_account_id)
        if account_from_db:
            address_sender = account_from_db.user_public_key
            token_address = account_from_db.token_address
            if FLASK_DEBUG:
                pk_sender = account_from_db.pk_sender
        else:
            print("wrong ext_account_id")
            return "wrong ext_account_id", 500
        if address_sender:
            # improperly signed
            channel = Channel.find_by_ext_account_id(ext_account_id)
            if channel:
                adp_channel = self.get_adp_channel(token_address=token_address,
                                                   address_sender=address_sender,
                                                   channel_address=channel.channel_address)
                if adp_channel:
                    ccs = CurrentChannelState.find_by_ext_account_id(ext_account_id)
                    if ccs:
                        nonce = ccs.nonce
                        last_settled_nonce = channel.last_settled_nonce
                        if nonce <= last_settled_nonce:
                            print("nonce too low")
                            return "nonce too low", 500
                        else:
                            total_paid_to_receiver = float(ccs.total_paid_to_receiver)
                            receiver_signature = ccs.receiver_signature
                            sender_signature = ccs.sender_signature
                            total_paid_to_receiver_for_sign = BlockChainHelper().transfer_token_decimal_to_bc(
                                token_address,
                                total_paid_to_receiver)
                            sha3_message = BlockChainHelper().create_message_sha3(nonce,
                                                                                  total_paid_to_receiver_for_sign)

                            b_sender_signature = BlockChainHelper().bytes_of_signature(sender_signature)
                            sender_signature_verified = BlockChainHelper().verify_signature_sha3(adp_channel,
                                                                                                 sha3_message,
                                                                                                 b_sender_signature,
                                                                                                 address_sender)
                            print(
                                'api settlement sender_signature_verified:{} sha3_message:{} receiver_signature:{}'.format(
                                    sender_signature_verified,
                                    sha3_message,
                                    receiver_signature))

                            b_receiver_signature = BlockChainHelper().bytes_of_signature(receiver_signature)
                            receiver_signature_verified = BlockChainHelper().verify_signature_sha3(adp_channel,
                                                                                                   sha3_message,
                                                                                                   b_receiver_signature,
                                                                                                   ITPS_SERVICE_ADDRESS)
                            print(
                                'api settlement receiver_signature_verified:{} sha3_message:{} receiver_signature:{}'.format(
                                    receiver_signature_verified,
                                    sha3_message,
                                    receiver_signature))

                            if sender_signature_verified and receiver_signature_verified:
                                command_args = {}
                                command_args['ccs_nonce'] = ccs.nonce
                                command_args['total_paid_to_receiver'] = total_paid_to_receiver
                                command_args['receiver_signature'] = receiver_signature
                                command_args['sender_signature'] = sender_signature
                                command_args['withdrawal_amount'] = sender_withdrawal_amount
                                command_args['token_address'] = token_address

                                Command(command_name=BCCommands.SETTLEMENT.name,
                                        user_public_key=address_sender,
                                        command_status=BCCommandsStatus.TODO.value,
                                        command_args=command_args).save_to_db()
                            else:
                                log.info(
                                    'wrong signature: receiver_signature_verified:{}  and sender_signature_verified:{} '.format(
                                        receiver_signature_verified, sender_signature_verified))
                                return 'wrong signature: receiver_signature_verified:{}  and sender_signature_verified:{} '.format(
                                        receiver_signature_verified, sender_signature_verified), 500

                    else:
                        log.info('no ccs for sender address: {} '.format(address_sender))
                        return 'no ccs for sender address: {} '.format(address_sender), 500
                else:
                    return "wrong ext_account_id", 500
            else:
                print("wrong ext_account_id")
                return "wrong ext_account_id", 500

        return None, 201

    def compose_channel_obj_for_update(self, adp_channel_from_bc, ccs, channel_from_db, sender_withdrawal_amount):
        if not sender_withdrawal_amount:
            channel_from_db.receiver_withdrawable = ccs.total_paid_to_receiver - channel_from_db.total_withdrawed_by_receiver
        else:
            channel_from_db.sender_withdrawable = sender_withdrawal_amount
        channel_from_db.last_settled_nonce = ccs.nonce
        flag_modified(channel_from_db, "receiver_withdrawable")
        flag_modified(channel_from_db, "last_settled_nonce")
        channel_from_db.channel_balance = adp_channel_from_bc[0]
        channel_from_db.channel_capacity = adp_channel_from_bc[1]
        channel_from_db.sender_withdrawable = adp_channel_from_bc[2]
        channel_from_db.receiver_withdrawable = adp_channel_from_bc[3]
        channel_from_db.last_settled_nonce = adp_channel_from_bc[4]
        channel_from_db.total_withdrawed_by_receiver = adp_channel_from_bc[5]
        channel_from_db.channel_status = adp_channel_from_bc[6]
        flag_modified(channel_from_db, "channel_balance")
        flag_modified(channel_from_db, "channel_capacity")
        flag_modified(channel_from_db, "sender_withdrawable")
        flag_modified(channel_from_db, "receiver_withdrawable")
        flag_modified(channel_from_db, "last_settled_nonce")
        flag_modified(channel_from_db, "total_withdrawed_by_receiver")
        flag_modified(channel_from_db, "channel_status")

    def get_json_pathes(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        token_abi_path = os.path.join(my_path, "../../../blockchain/common/ABI/{}".format(ERC20_TOKEN_JSON))
        adp_channel_manager_path = os.path.join(my_path,
                                                "../../../blockchain/common/ABI/{}".format(ADPCHANNEL_MANAGER_JSON))
        adp_channel_path = os.path.join(my_path, "../../../blockchain/common/ABI/{}".format(ADPCHANNEL_JSON))
        return adp_channel_manager_path, adp_channel_path, token_abi_path

    def get_adp_channel(self, token_address, address_sender, channel_address):
        adp_channel_manager_path, adp_channel_path, token_abi_path = self.get_json_pathes()
        channel_manager_json = Utils.read_json(adp_channel_manager_path)
        channel_json = Utils.read_json(adp_channel_path)
        token_abi = Utils.read_json(token_abi_path)
        blockchain_service = BlockChainService(token_abi=token_abi,
                                               adp_channel_manager_address=ADPCHANNEL_MANAGER_ADDRESS,
                                               adp_channel_manager_abi=channel_manager_json["abi"],
                                               adp_channel_abi=channel_json["abi"])
        adp_channel_manager = blockchain_service.get_adp_channel_manager()
        adp_channel = blockchain_service.get_adp_channel(token_address=token_address,
                                                         address_sender=address_sender,
                                                         channel_address=channel_address)
        return adp_channel
