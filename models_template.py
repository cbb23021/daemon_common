from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr

from app import db, config

BIND_KEY = config['DB_NAME']


class ModelsTemplate(object):
    __bind_key__ = BIND_KEY

    @declared_attr
    def id(self):
        column = db.Column(db.Integer, primary_key=True)
        column._creation_order = 0
        return column

    @declared_attr
    def update_datetime(self):
        return db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新時間')

    @declared_attr
    def create_datetime(self):
        return db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='建立時間')
