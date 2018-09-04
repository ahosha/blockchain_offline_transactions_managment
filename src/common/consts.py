# Swagger descriptions

EXT_ACCOUMT_ID_FIELD_DESCRIPTION = 'External Account Id, must be unique '
EXT_ACCOUMT_ID_SETTLEMENT_FIELD_DESCRIPTION = 'External Account Id of a channel to settle '
USER_PUBLIC_KEY_FIELD_DESCRIPTION = 'Public address of existing Ethereum account of a User'
TOKEN_ADDRESS_FIELD_DESCRIPTION = 'Token address supported for this account'
TRANSFER_AMOUNT_KEY_FIELD_DESCRIPTION = "Transfer amount. Receive it to check that CCS is correct " \
                                        "(calc from CCS : newccsammount - lastccsamount)"
CCS_USER_FIELD_DESCRIPTION = 'current channel state - signed by User'
WITHDRAW_ACCOUMT_ID_FIELD_DESCRIPTION = "Amount to withdraw . This parameter will be ignored for the receiver, " \
                                        "since receiver is getting all funds available for settlement. "
SETTLEMENT_ACCOUMT_ID_FIELD_DESCRIPTION = "Set sender_withdrawal_amount to zero to indicate Client System - initiated settlement"
CCS_BOTH_FIELD_DESCRIPTION = 'current channel state - signed by both User and Client System.'
CHANNEL_BALANCE_FIELD_DESCRIPTION = 'Channel balance'
CHANNEL_ADDRESS_FIELD_DESCRIPTION = 'Channel address'
CHANNEL_CAPACITY_FIELD_DESCRIPTION = 'Channel capacity'
CHANNEL_STATUS_FIELD_DESCRIPTION = 'Channel status (0 = Ready, 1 = WaitingForSettlement).'
LAST_SETTLED_NONCE_FIELD_DESCRIPTION = 'Last_settled_nonce'
AMOUNT_AVAILABLE_FOR_SETTLEMENT_TO_SENDER_FIELD_DESCRIPTION = 'Amount available for settlement to sender'
AMOUNT_AVAILABLE_FOR_SETTLEMENT_TO_RECEIVER_FIELD_DESCRIPTION = 'Amount available for settlement to receiver'
AMOUNT_AVAILABLE_FOR_WITHDRAWAL_TO_SENDER_FIELD_DESCRIPTION = 'Amount available for withdrawal to sender'
AMOUNT_AVAILABLE_FOR_WITHDRAWAL_TO_RECEIVER_FIELD_DESCRIPTION = 'Amount available for withdrawal to receiver'
NONCE_FIELD_DESCRIPTION = 'Nonce'
TOTAL_PAID_TO_RECEIVER_FIELD_DESCRIPTION = 'Total amount paid to receiver'
RECEIVER_SIGNATURE_FIELD_DESCRIPTION = "Receiver's signature"
SENDER_SIGNATURE_FIELD_DESCRIPTION = "Sender's signature"

SETLEMENT_DATA_FIELD_DESCRIPTION = 'ITPS settlement_data'
ACCOUNT_FIELD_DESCRIPTION = 'ITPS Account'
ACCOUNTS_FIELD_DESCRIPTION = 'List of accounts'
CHANNEL_FIELD_DESCRIPTION = 'ITPS Channel'
CCS_FIELD_DESCRIPTION = 'ITPS current channel state'
POST_CCS_FIELD_DESCRIPTION = 'ITPS current channel state data to post'
POST_SETTLEMENT_FIELD_DESCRIPTION = 'settlement data to post'

BC_MONITOR_SUB = 'BC_SUB'
DB_MONITOR_SUB = 'DB_SUB'

# BASE_URL = TEST_API_BASE_URL
POST_ACCOUNT_PART = 'api/accounts/'
POST_CCS_PART = 'api/ccs/'
GET_CHANNEL_PART = 'api/channels/'
POST_SETTLEMENT_PART = 'api/settlement/'
POST_WITHDRAW_PART = 'api/withdraw/'
API_PROTOCOL = 'http'
