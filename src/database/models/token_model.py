# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from src.database import db
from sqlalchemy.sql import func


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(256))
    token_decimal = db.Column(db.Integer)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, token_address, token_decimal):
        self.token_address = token_address
        self.token_decimal = token_decimal

    def __repr__(self):
        return '<bc monitor: %r>' % self.latest_block

    @classmethod
    def find_by_token_address(cls, token_address):
        try:

            return cls.query.filter_by(token_address=token_address).one()
        except:
            return None

    @classmethod
    def get_all_tokens(cls):
        try:
            return cls.query.order_by(Token.time_created).all()
        except:
            return None

    def update_db(self):
        db.session.no_autoflush()
        db.session.merge(self)
        db.session.flush()
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


