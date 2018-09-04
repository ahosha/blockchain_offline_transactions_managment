# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from src.database import db
from sqlalchemy.sql import func


class Settlement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ext_account_id_to_settle = db.Column(db.String(256))
    sender_withdrawal_amount = db.Column(db.Float)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, ext_account_id_to_settle, sender_withdrawal_amount):
        self.ext_account_id_to_settle = ext_account_id_to_settle
        self.sender_withdrawal_amount = sender_withdrawal_amount

    def __repr__(self):
        return '<Settlement: %r>' % self.ext_account_id

    @classmethod
    def find_by_ext_account_id(cls, ext_account_id):
        records = None
        try:
            records = cls.query.filter_by(ext_account_id_to_settle=ext_account_id). \
                order_by(Settlement.time_created).First()
        except:
            records = None
        return records

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
