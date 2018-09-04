# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from src.database import db
from sqlalchemy.sql import func


class BCMonitor(db.Model):
    __tablename__ = 'monitor'

    id = db.Column(db.Integer, primary_key=True)
    latest_block = db.Column(db.Integer)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, latest_block):
        self.latest_block = latest_block

    def __repr__(self):
        return '<bc monitor: %r>' % self.latest_block

    # @classmethod
    # def find_by_last_block_by_number(cls, latest_block):
    #     try:
    #         return cls.query.filter_by(latest_block=latest_block).first()
    #     except Exception as e:
    #         print('Failed to find_by_last_block: ' + str(e))
    #         db.session.rollback()

    @classmethod
    def find_by_last_block(cls):
        try:
            return cls.query.order_by(None).first()
        except Exception as e:
            print('Failed to find_by_last_block: ' + str(e))
            db.session.rollback()



    @classmethod
    def find_latest_block_by_number(cls, latest_block):
        try:
            return cls.query.filter_by(latest_block=latest_block).one()
        except:
            db.session.rollback()
            return None



    def update_db(self):
        db.session.merge(self)
        db.session.flush()
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


