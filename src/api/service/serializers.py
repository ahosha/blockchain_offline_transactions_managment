from flask_restplus import fields
from src.api.restplus import api
from src.common.consts import *

account = api.model(ACCOUNT_FIELD_DESCRIPTION, {
    'ext_account_id': fields.String(required=True, description=EXT_ACCOUMT_ID_FIELD_DESCRIPTION),
    'user_public_key': fields.String(required=True, description=USER_PUBLIC_KEY_FIELD_DESCRIPTION),
    'token_address': fields.String(required=True, description=TOKEN_ADDRESS_FIELD_DESCRIPTION),
})


list_of_accounts = api.inherit(ACCOUNTS_FIELD_DESCRIPTION, {
    'accounts:': fields.List(fields.Nested(account))
})

channel_snapshot = api.model(CHANNEL_FIELD_DESCRIPTION, {
    'ext_account_id': fields.String(required=True, description=EXT_ACCOUMT_ID_FIELD_DESCRIPTION),
    'user_public_key': fields.String(required=True, description=USER_PUBLIC_KEY_FIELD_DESCRIPTION),
    'channel_address': fields.String(required=True, description=CHANNEL_ADDRESS_FIELD_DESCRIPTION),
    'channel_balance': fields.Float(required=True, description=CHANNEL_BALANCE_FIELD_DESCRIPTION),
    'channel_capacity': fields.Float(required=True, description=CHANNEL_CAPACITY_FIELD_DESCRIPTION),
    'channel_status': fields.String(required=True, description=CHANNEL_STATUS_FIELD_DESCRIPTION),
    'last_settled_nonce': fields.Integer(required=True, description=LAST_SETTLED_NONCE_FIELD_DESCRIPTION),
    'available_for_settlement_to_sender': fields.Float
    (required=True,
     description=AMOUNT_AVAILABLE_FOR_SETTLEMENT_TO_SENDER_FIELD_DESCRIPTION),
    'available_for_settlement_to_receiver': fields.Float
    (required=True,
     description=AMOUNT_AVAILABLE_FOR_SETTLEMENT_TO_RECEIVER_FIELD_DESCRIPTION),
})

current_channel_state = api.model(CCS_FIELD_DESCRIPTION, {
    'nonce': fields.Integer(required=True, description=NONCE_FIELD_DESCRIPTION),
    'total_paid_to_receiver': fields.Float(required=True, description=TOTAL_PAID_TO_RECEIVER_FIELD_DESCRIPTION),
    'receiver_signature': fields.String(required=True, description=RECEIVER_SIGNATURE_FIELD_DESCRIPTION),
    'sender_signature': fields.String(required=True, description=SENDER_SIGNATURE_FIELD_DESCRIPTION),
    'channel_status': fields.String(required=True, description=CHANNEL_STATUS_FIELD_DESCRIPTION),
    'last_settled_nonce': fields.Integer(required=True, description=LAST_SETTLED_NONCE_FIELD_DESCRIPTION),
    'available_for_withdrawal_to_sender': fields.Float(
        required=True,
        description=AMOUNT_AVAILABLE_FOR_WITHDRAWAL_TO_SENDER_FIELD_DESCRIPTION),
    'available_for_withdrawal_to_receiver': fields.Float(required=True,
                                                         description=AMOUNT_AVAILABLE_FOR_WITHDRAWAL_TO_RECEIVER_FIELD_DESCRIPTION),

    'available_for_settlement_to_sender': fields.Float(
        required=True,
        description=AMOUNT_AVAILABLE_FOR_SETTLEMENT_TO_SENDER_FIELD_DESCRIPTION),
    'available_for_settlement_to_receiver': fields.Float(
        required=True,
        description=AMOUNT_AVAILABLE_FOR_SETTLEMENT_TO_RECEIVER_FIELD_DESCRIPTION),
})

post_ccs_data = api.model(POST_CCS_FIELD_DESCRIPTION, {
    'ext_account_id': fields.String(required=True, description=EXT_ACCOUMT_ID_FIELD_DESCRIPTION),
    'transfer_amount': fields.Float(required=True, description=TRANSFER_AMOUNT_KEY_FIELD_DESCRIPTION),
})

post_current_channel_state = api.inherit('post ccs data ', post_ccs_data, {
    'ccs': fields.Nested(current_channel_state)
})

settlement_data = api.model(SETLEMENT_DATA_FIELD_DESCRIPTION, {
    'ext_account_id_to_settle': fields.String(required=True, description=EXT_ACCOUMT_ID_SETTLEMENT_FIELD_DESCRIPTION),
    'sender_withdrawal_amount': fields.Float(required=True, description=SETTLEMENT_ACCOUMT_ID_FIELD_DESCRIPTION)
})

post_settlement_data = api.inherit(POST_SETTLEMENT_FIELD_DESCRIPTION, settlement_data, {
    'ccs': fields.Nested(current_channel_state)
})
