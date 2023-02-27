import time

from sqlalchemy import func

from app import db
from common.error_handler import ValidationError, ErrorCode


class ORMTool:
    """
    Database special query
        - To find unique
        - To count numbers

    Database operation(if something went wrong, auto rollback)
        - To flush session,
        - To commit session, if something went wrong rollback
        - To insert to database, if something went wrong rollback
        - To update to database, if something went wrong rollback
    """

    @staticmethod
    def is_unique(model, **kwargs):
        if model.query.filter_by(**kwargs).first():
            key = '-'.join(v for k, v in kwargs.items())
            # --------------------- 測試 --------------------- #
            print(f'=========== Found Duplicate Key: {key} ===========')
            # --------------------- 測試 --------------------- #
            return False
        return True

    @staticmethod
    def count(model, conditions=None):
        """ 計算數量 """
        conditions = conditions or list()
        amount = db.session.query(
            func.count(model.id)
        ).filter(
            *conditions
        ).scalar()
        return amount

    @staticmethod
    def flush():
        """ 資料庫 佔位 """
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            raise ValidationError(error_code=ErrorCode.BASE_ERROR)

    @staticmethod
    def commit():
        """ 資料庫 寫入 """
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValidationError(error_code=ErrorCode.BASE_ERROR)

    @staticmethod
    def expunge(obj=None):
        """ 切斷實例物件與資料庫關聯 """
        try:
            if obj:
                db.session.expunge(obj)
            else:
                db.session.expunge_all()
        except Exception as e:
            db.session.rollback()
            raise ValidationError(error_code=ErrorCode.BASE_ERROR)

    @classmethod
    def insert(cls, model, is_flush=False, **data):
        """ 單筆資料庫 寫入 """
        obj = model(**data)
        db.session.add(obj)
        if is_flush:
            cls.flush()
        else:
            cls.commit()
        return obj

    @classmethod
    def update(cls, obj, is_flush=False, **data):
        """ 單筆資料庫 更新 """
        for key, value in data.items():
            setattr(obj, key, value)
        if is_flush:
            cls.flush()
        else:
            cls.commit()
        return obj

    @classmethod
    def rollback(cls):
        """ 資料庫回滾 """  # 排除 sqlalchemy 斷線後 池裡有尚未完成的 transaction
        try:
            db.session.rollback()
        except Exception as e:
            time.sleep(2)
            db.session.rollback()
        time.sleep(2)
