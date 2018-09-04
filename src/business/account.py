from src.database import db
from src.database.models.account_model import Account
from src.business.channel import *
from src.business.token import *


def create_account(ext_account_id, user_public_key, token_name, pk_sender=None):
    account = Account(ext_account_id, user_public_key, token_name, pk_sender)
    account.save_to_db()

def create_account_channel_on_db(channel_address, external_account_id, token_address,
                                 pk_sender, sender_address, token_decimal):
    # create contract on input_token_address, get decimal ,save
    create_token(token_address, token_decimal)
    create_account(external_account_id, sender_address, token_address, pk_sender)
    # save channel to DB
    create_channel(sender_address, external_account_id, channel_address)
    return sender_address
