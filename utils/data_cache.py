import json
from datetime import datetime

import pytz

from app import rs, rs_f_decode
from common.const import Const
from common.models import Blacklist, Whitelist
from common.utils.redis_key import RedisKey


class DataCache:
    _WHITELIST_UPDATE_PERIOD = 60 * 5
    _BLACKLIST_UPDATE_PERIOD = 60 * 10

    _EXPIRATION_MEMBER_LOGIN_GAME_INTERVAL = 10
    _EXPIRATION_MEMBER_LOGIN_RECORD = 60 * 60 * 24 * 7
    _EXPIRATION_MEMBER_AUTH_INTERVAL = 5

    _EXPIRATION_TWOFACTOR_CALLBACK_STATUS = 10

    _REQUEST_LOCK_INTERVAL = 1
    _GAME_PLAYING_LOCK_INTERVAL = 60 * 3

    _TRANSFER_LOCK_INTERVAL = 10
    _RETURN_LOCK_INTERVAL = 10

    _EXPIRATION_MEMBER_MONTH_EXP = 60 * 60 * 24 * 35

    _USER_REPORT_PERIOD = 60 * 10

    @staticmethod
    def del_key(key):
        rs.delete(key)

    # ------------------------ [ Address Control ] -------------------------- #

    @classmethod
    def get_whitelist(cls, force_update=False):
        key = RedisKey.get_whitelist_key()
        value = rs.get(key)
        if force_update or not value:
            data = [_.address for _ in Whitelist.query.all()]
            rs.set(name=key,
                   value=json.dumps(data),
                   ex=cls._WHITELIST_UPDATE_PERIOD)
            return data
        return json.loads(value)

    @classmethod
    def get_blacklist(cls, force_update=False):
        key = RedisKey.get_blacklist_key()
        value = rs.get(key)
        if force_update or not value:
            data = [_.address for _ in Blacklist.query.all()]
            rs.set(name=key,
                   value=json.dumps(data),
                   ex=cls._BLACKLIST_UPDATE_PERIOD)
            return data
        return json.loads(value)

    # --------------------- [ Email Verification ] -------------------------- #

    # email otp
    @staticmethod
    def set_verify_email_otp(email, otp):
        expiration = Const.VerificationSystem.EMAIL_OTP_EXPIRATION
        key = RedisKey.get_verify_email_otp_key(email=email)
        rs.set(key, value=otp, ex=expiration)

    @staticmethod
    def get_verify_email_otp(email):
        key = RedisKey.get_verify_email_otp_key(email=email)
        return rs.get(key)

    @staticmethod
    def del_verify_email_otp(email):
        key = RedisKey.get_verify_email_otp_key(email=email)
        rs.delete(key)

    # email attempt
    @staticmethod
    def increase_verify_email_attempt(email):
        expiration = Const.VerificationSystem.EMAIL_OTP_RETRY_INTERVAL
        key = RedisKey.get_verify_email_attempt_key(email=email)
        rs.incr(key, amount=1)
        rs.expire(key, time=expiration)

    @staticmethod
    def get_verify_email_attempt(email):
        key = RedisKey.get_verify_email_attempt_key(email=email)
        value = rs.get(key)
        return int(value) if value else None

    # email Verification
    @staticmethod
    def set_verified_email(email, otp):
        expiration = Const.VerificationSystem.EMAIL_OTP_EXPIRATION
        key = RedisKey.get_verified_email_key(email=email)
        rs.set(key, value=otp, ex=expiration)

    @staticmethod
    def get_verified_email(email):
        key = RedisKey.get_verified_email_key(email=email)
        return rs.get(key)

    @staticmethod
    def del_verified_email(email):
        key = RedisKey.get_verified_email_key(email=email)
        rs.delete(key)

    """ AUTH LOCK """

    @classmethod
    def increase_member_auth_lock(cls, email):
        key = RedisKey.get_member_auth_lock_key(email=email)
        rs.incr(key, amount=1)
        ttl = rs.ttl(key)
        expiration = ttl if ttl > 0 else cls._EXPIRATION_MEMBER_AUTH_INTERVAL
        rs.expire(key, time=expiration)

    @staticmethod
    def get_member_auth_lock(email):
        """
        to block the member who try to
        login or refresh over 5 times in 5 seconds
        """
        key = RedisKey.get_member_auth_lock_key(email=email)
        return rs.get(key)

    # ====== lotto order ====

    # join 用
    @staticmethod
    def get_spare_order_id(draw_id):
        key = RedisKey.wait_order_ids(draw_id=draw_id)
        return rs.rpop(key)

    @staticmethod
    def push_order_data_to_used(draw_id, order_id, member_id, cash, ticket, number, join_dt, remark):
        key = RedisKey.used_order_data(draw_id=draw_id)
        value = f'{order_id}:{member_id}:{cash}:{ticket}:{number}:{join_dt}:{remark}'
        rs.lpush(key, value)

    # daemon 用
    @staticmethod
    def push_order_data_to_wait(draw_id, value):
        key = RedisKey.wait_order_ids(draw_id)
        return rs.rpush(key, *value)

    @staticmethod
    def get_used_order_data(draw_id, wait_time=10):
        key = RedisKey.used_order_data(draw_id)
        return rs.blpop(key, wait_time)

    # active ids
    @staticmethod
    def get_active_draw_id(wait_time=10):
        key = RedisKey.active_draw_ids()
        return rs.blpop(key, wait_time)

    @staticmethod
    def push_active_draw_ids(draw_ids):
        key = RedisKey.active_draw_ids()
        return rs.lpush(key, *draw_ids)

    """ TRANSACTION """

    @classmethod
    def flush_transaction(cls):
        """ 於 entry point 呼叫 重置 transaction Lock """
        for key in rs.scan_iter('*transaction*'):
            cls.del_key(key=key)

    """ REQUEST LOCK """

    @classmethod
    def set_request_lock(cls,
                         role,
                         user_id,
                         request_method,
                         request_path,
                         request_args,
                         request_payload,
                         ex=None):
        key = RedisKey.request_lock(
            role=role,
            user_id=user_id,
            request_method=request_method,
            request_path=request_path,
            request_args=request_args,
            request_payload=request_payload,
        )
        value = str(datetime.now())
        ex = ex if ex is not None else cls._REQUEST_LOCK_INTERVAL
        rs.set(key, value=value, ex=ex)

    @staticmethod
    def get_request_lock(user_id, role, request_method, request_path,
                         request_args, request_payload):
        key = RedisKey.request_lock(
            role=role,
            user_id=user_id,
            request_method=request_method,
            request_path=request_path,
            request_args=request_args,
            request_payload=request_payload,
        )
        return rs.get(key)

    """ Lock """

    @classmethod
    def set_game_playing_lock(cls, user_id):
        key = RedisKey.get_game_playing_lock_key(user_id=user_id)
        ex = cls._GAME_PLAYING_LOCK_INTERVAL
        rs.set(key, value='lock', ex=ex)

    @staticmethod
    def get_game_playing_lock(user_id):
        key = RedisKey.get_game_playing_lock_key(user_id=user_id)
        return rs.get(key)

    @staticmethod
    def del_game_playing_lock(user_id):
        key = RedisKey.get_game_playing_lock_key(user_id=user_id)
        rs.delete(key)

    """ Reward Prize Total """

    @staticmethod
    def get_reward_prize_total(setting_id):
        key = RedisKey.reward_prize_total(setting_id=setting_id)
        return rs.get(key) if rs.get(key) else 0

    @staticmethod
    def increase_reward_prize_total(setting_id, amount):
        key = RedisKey.reward_prize_total(setting_id=setting_id)
        rs.incr(key, amount=amount)
