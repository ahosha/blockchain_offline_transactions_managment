from src.common.settings import *
from src.blockchain.common.bc_helper import BlockChainHelper
from sqlalchemy.orm.attributes import flag_modified


def build_sign_trx(txn, nonce, web3, private_key):
    txn.buildTransaction({'gas': GAS_LIMIT_WITHDRAW,
                          'gasPrice': GAS_PRICE,
                          'nonce': nonce})
    web3.eth.enable_unaudited_features()
    signed_txn = web3.eth.account.signTransaction(txn, private_key=private_key)
    return signed_txn


def update_channel_on_db(channel_from_db, adp_channel_from_bc, token_address):
    if channel_from_db and adp_channel_from_bc:
        channel_balance = BlockChainHelper().transfer_token_decimal_from_bc(token_address,
                                                                            adp_channel_from_bc[0])
        channel_capacity = BlockChainHelper().transfer_token_decimal_from_bc(token_address,
                                                                             adp_channel_from_bc[1])
        sender_withdrawable = BlockChainHelper().transfer_token_decimal_from_bc(token_address,
                                                                                adp_channel_from_bc[2])
        receiver_withdrawable = BlockChainHelper().transfer_token_decimal_from_bc(token_address,
                                                                                  adp_channel_from_bc[3])
        total_withdrawed_by_receiver1 = BlockChainHelper().transfer_token_decimal_from_bc(token_address,
                                                                                          adp_channel_from_bc[5])
        total_withdrawed_by_receiver = channel_from_db.receiver_withdrawable

        channel_from_db.total_withdrawed_by_receiver = total_withdrawed_by_receiver
        channel_from_db.channel_balance = channel_balance
        channel_from_db.channel_capacity = channel_capacity
        channel_from_db.sender_withdrawable = sender_withdrawable
        channel_from_db.receiver_withdrawable = receiver_withdrawable
        channel_from_db.last_settled_nonce = adp_channel_from_bc[4]
        channel_from_db.total_withdrawed_by_receiver = total_withdrawed_by_receiver1
        channel_from_db.channel_status = adp_channel_from_bc[6]
        flag_modified(channel_from_db, "total_withdrawed_by_receiver")
        flag_modified(channel_from_db, "receiver_withdrawable")
        flag_modified(channel_from_db, "channel_balance")
        flag_modified(channel_from_db, "channel_capacity")
        flag_modified(channel_from_db, "sender_withdrawable")
        flag_modified(channel_from_db, "receiver_withdrawable")
        flag_modified(channel_from_db, "last_settled_nonce")
        flag_modified(channel_from_db, "total_withdrawed_by_receiver")
        flag_modified(channel_from_db, "channel_status")
        channel_from_db.update_db()

    return



