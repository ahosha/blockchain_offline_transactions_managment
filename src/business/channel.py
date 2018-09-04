from src.database import db
from src.database.models.account_model import Account
from src.database.models.channel_model import Channel
from src.database.models.ccs_model import CurrentChannelState
from src.database.models.settlement_model import Settlement
from src.database.models.withdraw_model import Withdraw


def create_channel(user_public_key, ext_account_id, channel_address):
    channel_balance = 0.0
    channel_capacity = 0.0
    #ContractStatus{Ready, WaitingForSettlement}
    channel_status = '0'
    last_settled_nonce = 0
    total_withdrawed_by_receiver = 0.0
    sender_withdrawable = 0.0
    receiver_withdrawable = 0.0

    channel = Channel(ext_account_id,
                      user_public_key,
                      channel_balance,
                      channel_status,
                      total_withdrawed_by_receiver,
                      sender_withdrawable, receiver_withdrawable,
                      channel_address, channel_capacity, last_settled_nonce
                      )
    channel.save_to_db()
