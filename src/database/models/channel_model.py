# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from src.database import db
from sqlalchemy.sql import func
from sqlalchemy.orm.attributes import flag_modified


class Channel(db.Model):
    __tablename__ = 'channels'
    # Balance,	Sender Withdrawable,	Receiver Withdrawable,	TotalWithdrawedByReceiver,

    id = db.Column(db.Integer, primary_key=True)
    ext_account_id = db.Column(db.String(256))
    user_public_key = db.Column(db.String(66))
    channel_address = db.Column(db.String(66))
    channel_balance = db.Column(db.Float)
    channel_capacity = db.Column(db.Float)
    last_settled_nonce = db.Column(db.Integer)
    channel_status = db.Column(db.String(50))
    sender_withdrawable = db.Column(db.Float)
    receiver_withdrawable = db.Column(db.Float)
    total_withdrawed_by_receiver = db.Column(db.Float)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())


    def __init__(self, ext_account_id, user_public_key, channel_balance,
                 channel_status, total_withdrawed_by_receiver,
                 sender_withdrawable, receiver_withdrawable,
                 channel_address, channel_capacity, last_settled_nonce):
        self.ext_account_id = ext_account_id
        self.user_public_key = user_public_key
        self.channel_balance = channel_balance
        self.channel_status = channel_status
        self.total_withdrawed_by_receiver = total_withdrawed_by_receiver
        self.sender_withdrawable = sender_withdrawable
        self.receiver_withdrawable = receiver_withdrawable
        self.channel_address = channel_address
        self.channel_capacity = channel_capacity
        self.last_settled_nonce = last_settled_nonce
    def json(self):
        return {'ext_account_id': self.ext_account_id,
                'user_public_key': self.user_public_key,
                'channel_address': self.channel_address,
                'channel_balance': self.channel_balance,
                # 'channel_capacity': self.channel_capacity,
                'channel_status': self.channel_status,
                'total_withdrawed_by_receiver': self.total_withdrawed_by_receiver,
                'sender_withdrawable': self.sender_withdrawable,
                'receiver_withdrawable': self.receiver_withdrawable}

    def __repr__(self):
        return '<Channel: %r>' % self.id



    def channel_snapshot_json(self):
        return {'ext_account_id': self.ext_account_id,
                'channel_contract_ethereum_address': self.channel_contract_ethereum_address,
                'channel_address': self.channel_address,
                'channel_balance': self.channel_balance,
                'sender_withdrawable': self.sender_withdrawable,
                'receiver_withdrawable': self.receiver_withdrawable,
                'channel_status': self.channel_status,
                'total_withdrawed_by_receiver': self.total_withdrawed_by_receiver}

    @classmethod
    def find_by_user_public_key(cls, user_public_key):
        return cls.query.filter_by(user_public_key=user_public_key).all()

    @classmethod
    def find_by_ext_account_id(cls, ext_account_id):
        return cls.query.filter_by(ext_account_id=ext_account_id).first()

    @classmethod
    def find_by_channel_address(cls, channel_address):
        try:
            return cls.query.filter_by(channel_address=channel_address).one()
        except:
            return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.merge(self)
        db.session.flush()
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
