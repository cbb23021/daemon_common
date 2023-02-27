import os
from functools import wraps
from secrets import token_hex

from flask import request

from app import db
from common.const import Const
from common.data_cache.fantasyee import FantasyeeDataCache
from common.error_handler import ErrorCode, ValidationError, NotAuthorizedError, NotFoundError
from common.orm.fantasyee_models import Admin, Member
from common.utils.encrypt_tool import Encrypt, JWTCoder
from common.utils.sdk_handler import SdkHandler
from common.utils.toolkit import Toolkit


class AuthTool:
    _MODEL_MAPS = {
        Const.RoleType.OWNER: Admin,
        Const.RoleType.MAINTAINER: Admin,
        Const.RoleType.MERCHANT: Admin,

        Const.RoleType.MEMBER: Member,
        Const.RoleType.ROBOT: Member,
    }

    _SECRET_MAP = {
        'ADMINONLY': {
            'model': Admin,
            'username': 'mc',
        },
    }
    _VALID_SECRET_ENVIRONMENT = {
        'develop',
        'release',
    }
    _ENVIRONMENT = os.environ['ENVIRONMENT']

    @classmethod
    def _get_identity(cls, model, username, password, superior_id=None, agent=None):
        if model is Admin:
            conditions = [
                model.username == username,
            ]
        elif model is Member and agent is None:
            conditions = [
                model.agent.is_(None),
                model.username == username,
            ]
        else:
            conditions = [
                model.agent == agent,
                model.username == username,
            ]
        user = model.query.filter(*conditions).first()
        if not user:
            """ 使用者不存在 """
            raise ValidationError(error_code=ErrorCode.USERNAME_IS_NOT_EXIST_OR_PASSWORD_IS_WRONG)
        if not user.is_active:
            """ 帳戶遭禁用 """
            raise NotAuthorizedError(error_code=ErrorCode.USER_IS_BLOCKED, message='User Has Been Blocked')
        if not Encrypt.check_password(user.password, password):
            """ 密碼錯誤 """
            raise ValidationError(error_code=ErrorCode.USERNAME_IS_NOT_EXIST_OR_PASSWORD_IS_WRONG)
        return user

    @classmethod
    def admin_login(cls, username, password):
        admin = cls._get_identity(model=Admin, username=username, password=password)
        role = admin.role
        is_active = admin.is_active
        email = admin.email
        phone = admin.phone
        access_token = JWTCoder.get_access_token(
            id=admin.id,
            username=username,
            role=role,
            is_active=is_active,
        )
        refresh_token = JWTCoder.get_refresh_token(
            id=admin.id,
            username=username,
            role=role,
        )
        result = {
            'username': username,
            'role': role,
            'email': email,
            'phone': phone,
            'token': access_token,
            'refresh_token': refresh_token,
        }
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return result

    @classmethod
    def login(cls, username, password, agent):
        user = cls._get_identity(
            model=Member,
            username=username,
            password=password,
            agent=agent,
        )
        access_token = JWTCoder.get_access_token(
            id=user.id,
            agent=user.agent,
            username=username,
            role=user.role,
            is_active=user.is_active,
        )
        refresh_token = JWTCoder.get_refresh_token(
            id=user.id,
            username=username,
            role=user.role,
        )
        result = {
            'username': user.username,
            'agent': user.agent,
            'role': user.role,
            'token': access_token,
            'refresh_token': refresh_token,
        }
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return result

    @classmethod
    def refresh_token(cls, refresh_token):
        refresh_token_content = JWTCoder.decode_refresh_token(token=refresh_token)
        id_ = refresh_token_content.get('id')
        username = refresh_token_content.get('username')
        role = refresh_token_content.get('role')
        if not (id_ and role and username):
            raise NotAuthorizedError(error_code=ErrorCode.DATA_MISSING)
        model = cls._MODEL_MAPS.get(role)
        if not model:
            """ 無法從資料庫取得該角色table """
            raise ValidationError(error_code=ErrorCode.INVALID_ACCESS_TOKEN, message='Role Not Found')
        user = model.query.filter_by(id=id_, role=role, username=username).first()
        if not user:
            raise NotFoundError(error_code=ErrorCode.USER_NOT_FOUND)
        is_active = user.is_active
        if not user.is_active:
            """ 帳戶遭禁用 """
            raise NotAuthorizedError(error_code=ErrorCode.USER_IS_BLOCKED, message='User Has Been Blocked')

        if role in {Const.RoleType.MEMBER, Const.RoleType.ROBOT}:
            access_token = JWTCoder.get_access_token(
                id=id_,
                username=username,
                role=role,
                is_active=is_active,
                agent=user.agent
            )
        else:
            access_token = JWTCoder.get_access_token(
                id=id_,
                username=username,
                role=role,
                is_active=is_active,
            )
        result = {
            'token': access_token
        }
        return result

    @classmethod
    def _parse_secret(cls):
        secret = request.args.get('secret')
        if not secret:
            return None
        dev_user = cls._SECRET_MAP.get(secret)
        if not dev_user:
            return None
        model = dev_user['model']
        username = dev_user['username']
        agent = dev_user.get('agent')
        if model is Admin:
            conditions = [
                model.username == username,
            ]
        elif model is Member and agent is None:
            conditions = [
                model.agent.is_(None),
                model.username == username,
            ]
        else:
            conditions = [
                model.agent == agent,
                model.username == username,
            ]
        return model.query.filter(*conditions).first()

    @classmethod
    def login_required(cls, *roles, update_address=None):
        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                # cls._inspect_allow_address(update_address=update_address) # TODO
                # -------------------- Develop Secret Key --------------------- #
                secret = cls._parse_secret()
                if cls._ENVIRONMENT in cls._VALID_SECRET_ENVIRONMENT and secret:
                    return method(*args, **kwargs, user=secret)
                # -------------------------------------------------------------- #

                token = request.headers.get('Authorization')
                if not token:
                    """ 表頭未包含AuthToken """
                    raise NotAuthorizedError(error_code=ErrorCode.ACCESS_TOKEN_MISSING)
                token_content = JWTCoder.decode_access_token(token=token)
                id_ = token_content.get('id')
                role = token_content.get('role')
                if not (id_ and role):
                    """ 未包含必要資訊 """
                    raise NotAuthorizedError(error_code=ErrorCode.INVALID_ACCESS_TOKEN)
                authorized_roles = {Const.RoleType.OWNER}
                for group in roles:
                    """ 拓展群組下角色 """
                    if group in Const.GroupType.get_elements():
                        authorized_roles.update(Const.GroupType.get_roles(group))
                    else:
                        authorized_roles.add(group)
                if role not in authorized_roles:
                    """ 不隸屬授權角色 """
                    raise NotAuthorizedError(error_code=ErrorCode.INVALID_PERMISSION)
                model = cls._MODEL_MAPS.get(role)
                if not model:
                    """ 無法從資料庫取得該角色table """
                    raise ValidationError(error_code=ErrorCode.INVALID_ACCESS_TOKEN, message='Role Not Found')
                user = model.query.filter_by(id=id_, role=role).first()
                if not user:
                    """ 使用者不存在 """
                    raise NotFoundError(error_code=ErrorCode.USER_NOT_FOUND)
                if not user.is_active:
                    """ 帳戶遭禁用 """
                    raise NotAuthorizedError(error_code=ErrorCode.USER_IS_BLOCKED, message='User Has Been Blocked')
                return method(*args, **kwargs, user=user)

            return wrapper

        return real_decorator

    # @staticmethod
    # def identify_sdk(method, **kwargs):
    #     """
    #     置於 @PayloadUtils.inspect_schema 之後,
    #     驗證 sdk 使用者身份
    #     """

    #     def _valid_signature(payload, secret_key):
    #         signature = payload['signature']
    #         del payload['signature']
    #         valid_signature = Toolkit.make_signature(payload=payload, secret_key=secret_key)
    #         if signature != valid_signature:
    #             raise NotAuthorizedError(error_code=ErrorCode.SIGNATURE_ERROR)

    #     def _valid_merchant(payload):
    #         merchant = Admin.query.filter_by(username=payload['merchant'],
    #                                          role=Const.RoleType.MERCHANT).first()
    #         if not merchant:
    #             """ 商戶不存在 """
    #             message = 'Merchant Not Found'
    #             raise NotAuthorizedError(error_code=ErrorCode.USER_NOT_FOUND, message=message)

    #         sdk_info_paths = {
    #             '/sdk/member-info',
    #             '/sdk/match-info',
    #             '/sdk/game-record',
    #             '/sdk/transaction-info',
    #             '/sdk/playing-experience',
    #             '/sdk/v3/member-exp-today',
    #             '/sdk/v3/tds-transaction',
    #         }
    #         if not merchant.is_active and request.path not in sdk_info_paths:
    #             """ 商戶遭禁用 """
    #             message = 'Merchant Has Been Block'
    #             raise NotAuthorizedError(error_code=ErrorCode.USER_IS_BLOCKED, message=message)
    #         return merchant

    #     def _get_member(merchant_id, agent, username):
    #         conditions = [
    #             Member.superior_id == merchant_id,
    #             Member.username == username,
    #         ]
    #         if agent is None:
    #             conditions.append(Member.agent.is_(None))
    #         else:
    #             conditions.append(Member.agent == agent)
    #         return Member.query.filter(*conditions).first()

    #     def _is_bot(merchant_id):
    #         mybot11 = Admin.query.filter_by(id=merchant_id, username='mybot11').first()
    #         return True if mybot11 else False

    #     def _upsert_member(payload, merchant_id):
    #         username = payload['username']
    #         agent = payload['agent']
    #         nickname = payload.get('nickname', username)
    #         member = _get_member(
    #             merchant_id=merchant_id,
    #             agent=agent,
    #             username=username,
    #         )
    #         if not member:
    #             member = SdkHandler.create_member(
    #                 merchant_id=merchant_id,
    #                 agent=agent,
    #                 username=username,
    #                 nickname=nickname,
    #                 is_bot=_is_bot(merchant_id=merchant_id),
    #             )
    #         access_token = JWTCoder.get_access_token(
    #             id=member.id,
    #             agent=member.agent,
    #             username=username,
    #             role=member.role,
    #             is_active=member.is_active,
    #         )
    #         refresh_token = JWTCoder.get_refresh_token(
    #             id=member.id,
    #             username=username,
    #             role=member.role,
    #         )
    #         result = {
    #             'member': member,
    #             'access_token': access_token,
    #             'refresh_token': refresh_token,
    #             'login_token': token_hex(16),
    #         }
    #         return result

    #     def _valid_member(payload, merchant_id):
    #         username = payload['username']
    #         agent = payload['agent']
    #         member = _get_member(
    #             merchant_id=merchant_id,
    #             agent=agent,
    #             username=username,
    #         )
    #         if not member:
    #             raise NotAuthorizedError(error_code=ErrorCode.USER_NOT_FOUND)
    #         return member

    #     @wraps(method)
    #     def wrapper(*args, **kwargs):
    #         member_free_sdk = {
    #             Const.SdkType.MATCH_INFO,
    #             Const.SdkType.TRANSACTION_INFO,
    #             Const.SdkType.TDS_TRANSACTION,
    #         }
    #         payload = kwargs['payload']
    #         sdk_method = payload['method']
    #         merchant = _valid_merchant(payload=payload)
    #         _valid_signature(payload=payload, secret_key=merchant.secret_key)
    #         kwargs.update({'merchant': merchant})
    #         if sdk_method in member_free_sdk:
    #             """ 不需驗證回傳 member """
    #             return method(*args, **kwargs)

    #         if sdk_method == Const.SdkType.MEMBER_LOGIN:
    #             """ 驗證回傳 member 不存在則建立使用者 """
    #             member_info = _upsert_member(payload=payload, merchant_id=merchant.id)
    #             FantasyeeDataCache.set_member_login(member_info=member_info)
    #             kwargs.update({
    #                 'member': member_info['member'],
    #                 'login_token': member_info['login_token'],
    #             })
    #         else:
    #             """ 驗證回傳 member """
    #             member = _valid_member(payload=payload, merchant_id=merchant.id)
    #             kwargs.update({'member': member})
    #         return method(*args, **kwargs)

    #     return wrapper

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
