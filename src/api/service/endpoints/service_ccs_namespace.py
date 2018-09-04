import logging
import os
import json
from flask import request
from flask_restplus import Resource
from src.api.service.serializers import current_channel_state, post_current_channel_state
from src.api.service.parsers import ext_account_id_arguments
from src.api.restplus import api

from src.business.business import *
from src.database.models.ccs_model import CurrentChannelState
from src.blockchain.service.blockchain_service import BlockChainService
from src.common.settings import *
from src.blockchain.common.bc_helper import BlockChainHelper
from src.blockchain.common.utils.utils_json import Utils

log = logging.getLogger(__name__)

ns = api.namespace('ccs', description='Current Channel State operations')


@ns.route('/')
class CCSCollection(Resource):

    @api.expect(ext_account_id_arguments, validate=True)
    @api.marshal_with(current_channel_state)
    def get(self):
        """   
       Returns Client System's version of Current Channel State

       This is an optional call
       Use this method to get the receiver's version of the current system state to compare to User's version
        """

        args = ext_account_id_arguments.parse_args(request)
        ext_account_id = args.get('ext_account_id', 1)
        ccs_query = CurrentChannelState.query.filter(CurrentChannelState.ext_account_id == ext_account_id).all()
        if ccs_query:
            return ccs_query
        else:
            return None

    @api.expect(post_current_channel_state, validate=True)
    @api.marshal_with(current_channel_state)
    @api.response(500, 'input validation error')
    @api.response(200, 'OK')
    def post(self):
        """
        Use to perform payment transaction.
        Pass signed current channel state with incremented amount.

        This is an off-chain operation.
        It validates user's signature.
        Signed channel states will not be broadcasted, but will be kept in the database.
        transfer_amount parameter is used to verify CSS.

        Returns CCS signed by both parties or error code and description 
        """

        request_data = request.json
        ext_account_id = request_data.get('ext_account_id')
        transfer_amount = request_data.get('transfer_amount')
        ccs_request = request_data.get('ccs')
        nonce = ccs_request['nonce']
        total_paid_to_receiver = ccs_request['total_paid_to_receiver']
        sender_signature = ccs_request['sender_signature']

        print("post_ccs_call ext_account_id:{} , nonce:{} , total_paid_to_receiver:{} , transfer_amount:{} ".format(
            ext_account_id, nonce, total_paid_to_receiver, transfer_amount))

        account_from_db = Account.find_by_ext_account_id(ext_account_id)
        if account_from_db:
            address_sender = account_from_db.user_public_key
            token_address = account_from_db.token_address,
            if FLASK_DEBUG:
                pk_sender = account_from_db.pk_sender
                token_address = account_from_db.token_address
        else:
            print("wrong ext_account_id")
            return "wrong ext_account_id", 500
        if address_sender:
            channel_address_from_db = Channel.find_by_ext_account_id(ext_account_id)
            # improperly signed
            adp_channel = self.get_adp_channel(token_address, address_sender, channel_address_from_db.channel_address)

            total_paid_to_receiver_for_sign = BlockChainHelper().transfer_token_decimal_to_bc(token_address,
                                                                                              total_paid_to_receiver)
            sha3_message = BlockChainHelper().create_message_sha3(nonce, total_paid_to_receiver_for_sign)
            print('api post ccs-> create_message_sha3 nonce:{} amount_for_signature:{} sha3_message:{}'.format(nonce,
                                                                                                               total_paid_to_receiver_for_sign,
                                                                                                               sha3_message))

            if FLASK_DEBUG:
                sender_signature = BlockChainHelper().prepare_sender_signature_sha3(sha3_message,
                                                                                    pk_sender)
            if adp_channel:
                # signature to bytes
                b_sender_signature = BlockChainHelper().bytes_of_signature(sender_signature)
                sender_signature_verified = BlockChainHelper().verify_signature_sha3(adp_channel,
                                                                                     sha3_message,
                                                                                     b_sender_signature,
                                                                                     address_sender)
                print(
                    'api ccs sender_signature_verified:{} sha3_message:{} receiver_signature:{}'.format(
                        sender_signature_verified,
                        sha3_message,
                        b_sender_signature))

                if not sender_signature_verified:
                    print("wrong sender signature")
                    return "wrong sender signature", 500
                else:
                    receiver_signature, v, r, s, messageHash = BlockChainHelper().gen_signature(sha3_message, ITPS_SERVICE_PRIVATE_KEY)
                    receiver_signature = BlockChainHelper().hex_of_signature(receiver_signature)
                    b_receiver_signature = BlockChainHelper().bytes_of_signature(receiver_signature)
                    receiver_signature_verified = BlockChainHelper().verify_signature_sha3(adp_channel,
                                                                                           sha3_message,
                                                                                           b_receiver_signature,
                                                                                           ITPS_SERVICE_ADDRESS)
                    print('api ccs receiver_verified:{} sha3_message:{} receiver_signature:{}'.format(
                        receiver_signature_verified,
                        sha3_message,
                        receiver_signature))
                    prev_ccs = CurrentChannelState.find_by_ext_account_id(ext_account_id)
                    if not prev_ccs:
                        prev_ccs = CurrentChannelState(ext_account_id=ext_account_id,
                                                       nonce=0,
                                                       total_paid_to_receiver=0,
                                                       receiver_signature=receiver_signature,
                                                       sender_signature=sender_signature)
                    nonce_verified = self.verify_ccs_sequence(nonce, prev_ccs)
                    if not nonce_verified:
                        print("ccs sequence failed")
                        return "ccs sequence failed", 500
                    else:
                        # exceeds channel capacity : Capacity=Balance-CCS.TotalPaidToReceiver+TotalWithdrawedByReceiver-Sender Withdrawable
                        db_channel = Channel.find_by_ext_account_id(ext_account_id)
                        if not db_channel:
                            print("wrong ext_account_id")
                            return "wrong ext_account_id", 500
                        else:
                            balance = db_channel.channel_balance
                            # total_paid_to_receiver = prev_ccs.total_paid_to_receiver
                            total_withdrawed_by_receiver = db_channel.total_withdrawed_by_receiver
                            sender_withdrawable = db_channel.sender_withdrawable
                            capacity = balance - total_paid_to_receiver + total_withdrawed_by_receiver - sender_withdrawable
                            if total_paid_to_receiver > capacity:
                                print("channel capacity overload")
                                return "channel capacity overload", 500
                            else:
                                transfer_amount_verification = total_paid_to_receiver - prev_ccs.total_paid_to_receiver
                                if transfer_amount_verification != transfer_amount:
                                    print("transfer amount mismatch")
                                    return "transfer amount mismatch", 500
                                else:
                                    new_ccs = CurrentChannelState(ext_account_id=prev_ccs.ext_account_id,
                                                                  nonce=nonce,
                                                                  total_paid_to_receiver=total_paid_to_receiver,
                                                                  receiver_signature=receiver_signature,
                                                                  sender_signature=sender_signature)
                                    new_ccs.save_to_db()

                                    current_ccs = CurrentChannelState.find_by_ext_account_id(ext_account_id)

                                    return current_ccs, 200
            else:
                print("wrong ext_account_id")
                return "wrong ext_account_id", 500
        else:
            print("wrong ext_account_id")
            return "wrong ext_account_id", 500

    def verify_ccs_sequence(self, nonce, prev_ccs):
        # sequence failed: older than existing state - check nonce (bigger then previous)
        if prev_ccs.nonce > nonce:
            return False
        else:
            if nonce - prev_ccs.nonce != 1:
                print("wrong nonce sequence incrementation")
                return False
            else:
                return True

    def get_adp_channel(self, token_address, address_sender, channel_address=None):
        adp_channel_manager_path, adp_channel_path, token_abi_path = self.get_json_pathes()
        channel_manager_json = Utils.read_json(adp_channel_manager_path)
        channel_json = Utils.read_json(adp_channel_path)
        token_abi = Utils.read_json(token_abi_path)
        blockchain_service = BlockChainService(token_abi=token_abi,
                                               adp_channel_manager_address=ADPCHANNEL_MANAGER_ADDRESS,
                                               adp_channel_manager_abi=channel_manager_json["abi"],
                                               adp_channel_abi=channel_json["abi"])
        adp_channel_manager = blockchain_service.get_adp_channel_manager()
        adp_channel = blockchain_service.get_adp_channel(token_address, address_sender, channel_address)
        return adp_channel

    def get_json_pathes(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        token_abi_path = os.path.join(my_path, "../../../blockchain/common/ABI/{}".format(ERC20_TOKEN_JSON))
        adp_channel_manager_path = os.path.join(my_path,
                                                "../../../blockchain/common/ABI/{}".format(ADPCHANNEL_MANAGER_JSON))
        adp_channel_path = os.path.join(my_path, "../../../blockchain/common/ABI/{}".format(ADPCHANNEL_JSON))
        return adp_channel_manager_path, adp_channel_path, token_abi_path
