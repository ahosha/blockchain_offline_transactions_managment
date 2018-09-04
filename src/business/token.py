from src.database import db
from src.database.models.token_model import Token


def create_token(token_address,token_decimal):
    if not Token.find_by_token_address(token_address):
        token_to_save = Token(token_address, token_decimal)
        token_to_save.save_to_db()



