import threading
from datetime import datetime
from functools import wraps

from flask import request

from app import db
from common.const import Const
from common.error_handler import ErrorCode, ValidationError
from common.orm.fantasyee_models import (
    Admin, AdminOperation,
    Member, MemberOperation,
)


class OperationRecorder:
    """
        To handle route operations with login_required decorator,
        You can easily get user from login_required or set user manually.

        OperationRecorder.set(operator=user, debug=True)
    """

    _DEFAULT_PER_PAGE = 10

    _MODEL_MAPS = {
        Admin: AdminOperation,
        Member: MemberOperation,
    }

    @classmethod
    def _get_operation_model(cls, operator):
        operation_model = cls._MODEL_MAPS.get(type(operator))
        if operation_model:
            return operation_model
        raise ValueError(f'Invalid table_name: {operator.__table__.name}')

    @staticmethod
    def _insert_model(model, **data):
        try:
            obj = model(**data)
            db.session.add(obj)
            db.session.flush()
            obj_id = getattr(obj, 'id', None)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise ValidationError(ErrorCode.BASE_ERROR)
        return obj_id

    @staticmethod
    def _get_payload():
        data = request.get_json(silent=True)
        return data or None

    @classmethod
    def set(cls, operator, debug=False):
        """
        手動添加紀錄點
        """
        data = {
            'model': cls._get_operation_model(operator=operator),
            'operator_id': operator.id,
            'route': request.path,
            'method': Const.MethodType.get_type(request.method),
            'payload': cls._get_payload(),
        }
        if debug:
            print(data)
        thread = threading.Thread(target=cls._insert_model, kwargs=data)
        thread.start()

    @staticmethod
    def _stream(tag, message):
        now = datetime.now().strftime('%F %X,%f')[:-3]
        print(f'[{now}] [{tag.upper():8}] [ * {message}]')

    @classmethod
    def log(cls, debug=False):
        """
        透過裝飾器自動記錄, 置於 @AuthTool.login_required 之後
        API
        - user 傳接 所有角色

        SDK(member 會經由 merchant 代理部分操作行為)
        - merchant 傳接 商戶(重複紀錄若代理member操作)
        - member 傳接 使用者(重複紀錄若經由merchant操作)
        """

        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                user = kwargs.get('user')
                merchant = kwargs.get('merchant')
                member = kwargs.get('member')
                result = method(*args, **kwargs)
                if user:
                    cls.set(operator=user, debug=debug)
                if merchant:
                    cls.set(operator=merchant, debug=debug)
                if member:
                    cls.set(operator=member, debug=debug)
                if not any({user, merchant, member}):
                    message = f'{cls.__name__}.log Skipped! Cannot Find any([User, Member, Merchant]) in kwargs'
                    cls._stream(tag='warning', message=message)
                return result

            return wrapper

        return real_decorator

    @staticmethod
    def _serialize(operation):
        data = {
            'id': operation.id,
            'operator': {
                'id': operation.operator.id,
                'username': operation.operator.username,
                'remark': operation.operator.remark,
            },
            'method': operation.method,
            'route': operation.route,
            'payload': operation.payload or None,
            'datetime': operation.create_datetime.strftime('%F %X'),
        }
        return data

    @classmethod
    def get(cls, model, operator_id=None, page=None, per_page=None):
        """
        return operations records order by descending
        """
        page = page or 1
        per_page = per_page or cls._DEFAULT_PER_PAGE
        conditions = list()
        if operator_id:
            conditions.append(model.operator_id == operator_id)

        objs = model.query.filter(*conditions).order_by(
            model.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        operations = objs.items
        results = [cls._serialize(_) for _ in operations]
        pager = {
            'page': page,
            'per_page': per_page,
            'total': objs.total,
            'pages': objs.pages,
        }
        return results, pager
