import os
from datetime import datetime
from functools import wraps

from flask import request

from app import config, db
from common.const import Const
from common.error_handler import ErrorCode, ValidationError, NotAuthorizedError, ForbiddenError, NotFoundError
from common.models import Member, Admin
from common.utils.data_cache import DataCache
from common.utils.encrypt_tool import Encrypt, JWTCoder


class AuthTool:

    _SECRET_MAP = {
         'ADMINONLY': 'admin',
    }

    _VALID_SECRET_ENVIRONMENT = {
        'develop',
        'release',
    }
    _VALID_REMOTE_ADDR_ENVIRONMENT = {
        'develop',
    }
    _BYPASS_WHITELIST_ENVIRONMENT = {
        'develop',
    }
    _ENVIRONMENT = os.environ['ENVIRONMENT']
    _ADMIN_TYPES = Const.GroupType.get_roles(Const.GroupType.ADMIN)
    _MEMBER_TYPES = Const.GroupType.get_roles(Const.GroupType.USER)
    _AUTH_ATTEMPT_LIMIT = 5

    _FORCE_UPDATE_WHITELIST = config.get('ENABLE_FORCE_UPDATE_WHITELIST', False)
    _FORCE_UPDATE_BLACKLIST = config.get('ENABLE_FORCE_UPDATE_BLACKLIST', False)

    @staticmethod
    def _validate_identity(user, password):
        if not user:
            """ 使用者不存在 """
            raise ValidationError(error_code=ErrorCode.USERNAME_IS_NOT_EXIST_OR_PASSWORD_IS_WRONG)
        if not Encrypt.check_password(user.password, password):
            """ 密碼錯誤 """
            raise ValidationError(error_code=ErrorCode.USERNAME_IS_NOT_EXIST_OR_PASSWORD_IS_WRONG)
        if user.is_block:
            """ 帳戶遭禁用 """
            raise ForbiddenError(error_code=ErrorCode.USER_IS_BLOCKED, message='User Has Been Blocked')

    @classmethod
    def _get_identity(cls, phone, username, password, group):
        if group not in {Const.GroupType.ADMIN, Const.GroupType.USER}:
            raise ValidationError(error_code=ErrorCode.INVALID_OPERATION, message=f'Invalid Group Type: {group}')
        if group == Const.GroupType.ADMIN and username:
            user = Admin.query.filter_by(username=username).first()
        elif group == Const.GroupType.USER and phone:
            user = Member.query.filter_by(phone=phone).first()
        else:
            raise ValidationError(error_code=ErrorCode.INVALID_OPERATION, message=f'Required phone or username')
        cls._validate_identity(user=user, password=password)
        return user

    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def _update_user_login_detail(user):
        latest_login_info = {
            'login_address': request.environ.get('HTTP_X_REAL_IP'),
            'login_datetime': datetime.now().strftime("%F %X"),
            'platform': request.user_agent.platform,
            'browser': request.user_agent.browser,
            'is_app': bool(int(request.headers.get('is_app', 0))),
        }
        user.latest_login_info = latest_login_info

    @classmethod
    def _inspect_suspend_address(cls, update_address=None):
        force_update = cls._FORCE_UPDATE_BLACKLIST if update_address is None else update_address
        blacklist = DataCache.get_blacklist(force_update=force_update)
        address = request.environ.get('HTTP_X_REAL_IP')
        if not address and cls._ENVIRONMENT in cls._VALID_REMOTE_ADDR_ENVIRONMENT:
            """ 允許使用 request.remote_addr 作為預設值 """
            address = request.remote_addr
        if address in blacklist:
            """ 禁用 存在黑名單 """
            raise ForbiddenError(error_code=ErrorCode.INVALID_IP_ADDRESS)

    @classmethod
    def member_login(cls, phone, password):
        cls._inspect_suspend_address()
        attempt = DataCache.get_member_auth_lock(phone=phone)
        if attempt and int(attempt) > cls._AUTH_ATTEMPT_LIMIT:
            raise ValidationError(error_code=ErrorCode.INVALID_OPERATION, message=f'Request Login Repeatedly')
        user = cls._get_identity(
            phone=phone,
            username=None,
            password=password,
            group=Const.GroupType.USER,
        )
        data = {
            'id': user.id,
            'phone': user.phone,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        }
        result = {
            'phone': user.phone,
            'username': user.username,
            'email': user.email,
            'token': JWTCoder.get_access_token(**data),
            'refresh_token': JWTCoder.get_refresh_token(**data),
            'role': user.role,
        }
        cls._update_user_login_detail(user=user)
        cls._commit()
        DataCache.increase_member_auth_lock(phone=phone)
        return result

    @classmethod
    def _inspect_allow_address(cls, update_address=None):
        if cls._ENVIRONMENT in cls._BYPASS_WHITELIST_ENVIRONMENT:
            return None
        force_update = cls._FORCE_UPDATE_WHITELIST if update_address is None else update_address
        whitelist = DataCache.get_whitelist(force_update=force_update)
        address = request.environ.get('HTTP_X_REAL_IP')
        if address not in whitelist:
            """ 禁用 非白名單 """
            raise ForbiddenError(error_code=ErrorCode.INVALID_IP_ADDRESS)

    @classmethod
    def _validate_user(cls, user, update_address):
        if not user:
            """ 使用者不存在 """
            raise ValidationError(error_code=ErrorCode.USER_NOT_FOUND)
        if user.is_block:
            """ 帳戶遭禁用 """
            raise ForbiddenError(error_code=ErrorCode.USER_IS_BLOCKED, message='User Has Been Blocked')
        if user.role in cls._MEMBER_TYPES:
            """ 檢查會員地址是否可用 """
            cls._inspect_suspend_address(update_address=update_address)
        elif user.role in cls._ADMIN_TYPES:
            """ 檢查管理員地址是否可用 """
            cls._inspect_allow_address(update_address=update_address)
        else:
            raise NotFoundError(error_code=ErrorCode.DATA_ERROR, message=f'User role: {user.role} is not exist')

    @classmethod
    def member_refresh(cls, refresh_token, update_address=None):
        cls._inspect_suspend_address()
        data = JWTCoder.decode_refresh_token(token=refresh_token)
        id_ = data.get('id')
        role = data.get('role')
        phone = data.get('phone')
        attempt = DataCache.get_member_auth_lock(phone=phone)
        if attempt and int(attempt) > cls._AUTH_ATTEMPT_LIMIT:
            raise ValidationError(error_code=ErrorCode.INVALID_OPERATION, message=f'Request Login Repeatedly')
        if not (id_ and phone and role):
            raise ValidationError(error_code=ErrorCode.INVALID_REFRESH_TOKEN)
        user = Member.query.filter_by(id=id_, phone=phone, role=role).first()
        cls._validate_user(user=user, update_address=update_address)
        access_token = JWTCoder.get_access_token(
            id=user.id,
            phone=user.phone,
            username=user.username,
            email=user.email,
            role=user.role,
        )
        cls._update_user_login_detail(user=user)
        cls._commit()
        DataCache.increase_member_auth_lock(phone=phone)
        return {'token': access_token}

    # ----------------------------- Admin Auth ----------------------------- #
    @classmethod
    def admin_login(cls, username, password):
        cls._inspect_allow_address()
        admin = cls._get_identity(
            phone=None,
            username=username,
            password=password,
            group=Const.GroupType.ADMIN,
        )
        data = {
            'id': admin.id,
            'username': admin.username,
            'role': admin.role,
        }
        result = {
            'username': username,
            'token': JWTCoder.get_access_token(**data),
            'refresh_token': JWTCoder.get_refresh_token(**data),
            'role': admin.role
        }
        cls._update_user_login_detail(user=admin)
        cls._commit()
        return result

    @classmethod
    def admin_refresh(cls, refresh_token, update_address=None):
        cls._inspect_allow_address()
        refresh_token_content = JWTCoder.decode_refresh_token(token=refresh_token)
        id_ = refresh_token_content.get('id')
        username = refresh_token_content.get('username')
        role = refresh_token_content.get('role')
        if not (id_ and username and role):
            raise NotAuthorizedError(error_code=ErrorCode.INVALID_REFRESH_TOKEN)
        admin = Admin.query.filter_by(id=id_, username=username, role=role).first()
        cls._validate_user(user=admin, update_address=update_address)
        access_token = JWTCoder.get_access_token(
            id=admin.id,
            username=username,
            role=role,
        )
        cls._update_user_login_detail(user=admin)
        cls._commit()
        return {'token': access_token}

    @classmethod
    def _parse_secret(cls):
        secret = request.args.get('secret')
        if not secret:
            return None
        username = cls._SECRET_MAP.get(secret)
        if not username:
            return None
        model = Admin if secret.startswith(cls._ADMIN_PREFIX) else Member
        return model.query.filter_by(username=username).first()

    @classmethod
    def login_required(cls, *roles, update_address=None):
        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                # -------------------- Develop Secret Key --------------------- #
                secret = cls._parse_secret()
                if cls._ENVIRONMENT in cls._VALID_SECRET_ENVIRONMENT and secret:
                    return method(*args, **kwargs, user=secret)

                # ----------------------- Parse Token ------------------------ #
                token = request.headers.get('Authorization')
                if not token:
                    raise NotAuthorizedError(error_code=ErrorCode.ACCESS_TOKEN_MISSING)
                token_content = JWTCoder.decode_access_token(token=token)
                id_ = token_content.get('id')
                phone = token_content.get('phone')
                username = token_content.get('username')
                role = token_content.get('role')

                # -------------------- Check Permission --------------------- #
                authorized_roles = {Const.RoleType.OWNER}
                for constrain in roles:
                    """ 拓展群組下角色 """
                    if constrain in Const.GroupType.get_elements():
                        authorized_roles.update(Const.GroupType.get_roles(constrain))
                    else:
                        authorized_roles.add(constrain)
                if role not in authorized_roles:
                    """ 不隸屬授權角色 """
                    raise ForbiddenError(error_code=ErrorCode.INVALID_PERMISSION)

                # --------------------- Get User object --------------------- #
                if role in cls._ADMIN_TYPES and id_ and role and username:
                    """ Admin login by username """
                    user = Admin.query.filter_by(id=id_, username=username, role=role).first()
                elif role in cls._MEMBER_TYPES and id_ and role and phone:
                    """ Member login by phone """
                    user = Member.query.filter_by(id=id_, phone=phone, role=role).first()
                else:
                    raise NotAuthorizedError(error_code=ErrorCode.INVALID_ACCESS_TOKEN)
                cls._validate_user(user=user, update_address=update_address)
                return method(*args, **kwargs, user=user)

            return wrapper

        return real_decorator

    @classmethod
    def blacklist_inspect(cls, update_address=None):
        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                cls._inspect_suspend_address(update_address=update_address)
                return method(*args, **kwargs)

            return wrapper

        return real_decorator

    @classmethod
    def whitelist_inspect(cls, update_address=None):
        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                cls._inspect_allow_address(update_address=update_address)
                return method(*args, **kwargs)

            return wrapper

        return real_decorator

    @staticmethod
    def cache_custom_func(**kwargs):
        path = request.full_path
        if request.method == 'GET':
            params = dict(request.args)
        else:
            params = request.json or dict()
        param_str = '&'.join(f'{k}={v}' for k, v in sorted(params.items(), key=lambda x: x[0]))
        user = kwargs['user']
        key = f'{path}:{param_str}:{user.id}'
        return key
