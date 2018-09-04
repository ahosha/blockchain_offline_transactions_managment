# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from src.database import db
from sqlalchemy.sql import func


class CurrentChannelState(db.Model):
    # CCS.TotalPaidToReceiver	CCS.Nonce
    __tablename__ = 'ccs'

    id = db.Column(db.Integer, primary_key=True)
    ext_account_id = db.Column(db.String(256))
    total_paid_to_receiver = db.Column(db.Float)
    nonce = db.Column(db.Integer)
    receiver_signature = db.Column(db.String(256))
    sender_signature = db.Column(db.String(256))
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, ext_account_id,
                 nonce, total_paid_to_receiver,
                 receiver_signature, sender_signature):
        self.ext_account_id = ext_account_id
        self.nonce = nonce
        self.total_paid_to_receiver = total_paid_to_receiver
        self.receiver_signature = receiver_signature
        self.sender_signature = sender_signature

    def __repr__(self):
        return '<ccs: %r>' % self.ext_account_id

    @classmethod
    def find_by_ext_account_id(cls, ext_account_id):
        records = None
        try:
            records = cls.query.filter_by(ext_account_id=ext_account_id).order_by(
                CurrentChannelState.time_created.desc()).first()
        except:
            records = None
        return records

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
