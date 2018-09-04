from src.database import db
from src.database.models.base_model import BaseModel
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


class Account(BaseModel, db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    ext_account_id = db.Column(db.String(256))
    user_public_key = db.Column(db.String(66))
    pk_sender = db.Column(db.String(256))
    token_address = db.Column(db.String(256))
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, ext_account_id, user_public_key,
                 token_address,
                 pk_sender=None):
        self.ext_account_id = ext_account_id
        self.user_public_key = user_public_key
        self.token_address = token_address
        self.pk_sender = pk_sender

    @classmethod
    def find_by_ext_account_id(cls, ext_account_id):
        records = None
        try:
            records = cls.query.filter_by(ext_account_id=ext_account_id).one()
        except:
            records = None
        return records

    @classmethod
    def find_by_user_public_key(cls, user_public_key):
        return cls.query.filter_by(user_public_key=user_public_key).all()

    @classmethod
    def get_all_accounts(cls):
        try:
            return cls.query.order_by(Account.time_created).all()
        except:
            return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
