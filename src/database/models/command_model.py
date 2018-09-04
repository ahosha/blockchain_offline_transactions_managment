from src.database import db
from src.database.models.base_model import BaseModel
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


class Command(db.Model):
    __tablename__ = 'commands'

    id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String(100))
    user_public_key = db.Column(db.String(66))
    command_args = db.Column(db.JSON)
    # 1 - to do , 2 - ready, 3- failed , 4 - in process
    command_status = db.Column(db.Integer)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, command_name, user_public_key, command_status, command_args):
        self.command_name = command_name
        self.command_args = command_args
        self.command_status = command_status
        self.user_public_key = user_public_key

    @classmethod
    def find_by_command_status(cls, command_status):
        return cls.query.filter_by(command_status=command_status).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.merge(self)
        db.session.flush()
        db.session.commit()
