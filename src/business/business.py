from src.database import db
from src.database.models.account_model import Account
from src.database.models.channel_model import Channel
from src.database.models.ccs_model import CurrentChannelState
from src.database.models.settlement_model import Settlement
from src.database.models.withdraw_model import Withdraw


def create_ccs_on_db(ext_account_id, nonce, total_paid_to_receiver):

    # ext_account_id = data.get('ext_account_id')
    # transfer_amount = data.get('transfer_amount')
    #
    # ccs_request = data.get('ccs')
    # nonce = ccs_request['nonce']
    # total_paid_to_receiver = ccs_request['total_paid_to_receiver']

    # receiver_signature = ccs_request['receiver_signature']
    # sender_signature = ccs_request['sender_signature']
    # channel_status = ccs_request['channel_status']
    # last_settled_nonce = ccs_request['last_settled_nonce']
    # available_for_withdrawal_to_sender = ccs_request['available_for_withdrawal_to_sender']
    # available_for_withdrawal_to_receiver = ccs_request['available_for_withdrawal_to_receiver']
    # available_for_settlement_to_sender = ccs_request['available_for_settlement_to_sender']
    # available_for_settlement_to_receiver = ccs_request['available_for_settlement_to_receiver']

    # save ccs to db
    ccs = CurrentChannelState(ext_account_id,
                              total_paid_to_receiver,
                              nonce )
    ccs.save_to_db()


def create_settlement(ext_account_id_to_settle, sender_withdrawal_amount):
    settlement = Settlement(ext_account_id_to_settle, sender_withdrawal_amount)
    settlement.save_to_db()


def create_withdraw(ext_account_id):
    withdraw = Withdraw(ext_account_id)
    withdraw.save_to_db()
