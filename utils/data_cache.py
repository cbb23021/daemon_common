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

    # ------------------------- [ Address Control ] -------------------------- #

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

    # ------------------------- [ Email Verification ] -------------------------- #

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

    # """ Phone OTP """

    # @staticmethod
    # def set_phone_otp(phone, otp):
    #     expiration = Const.VerificationSystem.PHONE_OTP_EXPIRATION
    #     key = RedisKey.get_phone_otp_key(phone=phone)
    #     rs.set(key, value=otp, ex=expiration)

    # @staticmethod
    # def get_phone_otp(phone):
    #     key = RedisKey.get_phone_otp_key(phone=phone)
    #     return rs.get(key)

    # @staticmethod
    # def del_phone_otp(phone):
    #     key = RedisKey.get_phone_otp_key(phone=phone)
    #     rs.delete(key)

    # """ Phone OTP Request Attempt """

    # @staticmethod
    # def increase_phone_otp_request_attempt(phone):
    #     key = RedisKey.get_phone_otp_request_attempt_key(phone=phone)
    #     ttl = rs.ttl(key)
    #     expiration = ttl if ttl > 10 else Const.VerificationSystem.PHONE_OTP_RETRY_INTERVAL
    #     rs.incr(key, amount=1)
    #     rs.expire(key, time=expiration)

    # @staticmethod
    # def get_phone_otp_request_attempt(phone):
    #     key = RedisKey.get_phone_otp_request_attempt_key(phone=phone)
    #     value = rs.get(key)
    #     return int(value) if value else None

    # """ Phone Verification """

    # @staticmethod
    # def set_verified_phone(phone, otp):
    #     expiration = Const.VerificationSystem.VERIFIED_PHONE_EXPIRATION
    #     key = RedisKey.get_verified_phone_key(phone=phone)
    #     rs.set(key, value=otp, ex=expiration)

    # @staticmethod
    # def get_verified_phone(phone):
    #     key = RedisKey.get_verified_phone_key(phone=phone)
    #     return rs.get(key)

    # @staticmethod
    # def del_verified_phone(phone):
    #     key = RedisKey.get_verified_phone_key(phone=phone)
    #     rs.delete(key)

    """ TRANSACTION """

    @classmethod
    def flush_transaction(cls):
        """ 於 entry point 呼叫 重置 transaction Lock """
        for key in rs.scan_iter(f'*transaction*'):
            cls.del_key(key=key)

    """ FANTASYEE PLAYING EXPERIENCE """

    @staticmethod
    def set_fantasyee_member_playing_experience(username, data):
        expiration = Const.FantasyeeData.PLAYING_EXPERIENCE_EXPIRATION
        key = RedisKey.get_fantasyee_member_playing_experience_key(
            username=username)
        rs.set(key, value=data, ex=expiration)

    @staticmethod
    def get_fantasyee_member_playing_experience(username):
        key = RedisKey.get_fantasyee_member_playing_experience_key(
            username=username)
        return rs.get(key)

    """ CHAT """

    @staticmethod
    def set_unread_amount(room_name, amount):
        key = RedisKey.get_room_unread_amount_key(room_name=room_name)
        rs.set(key, value=amount, ex=60 * 60 * 24 * 3)

    @staticmethod
    def get_unread_amount(room_name):
        key = RedisKey.get_room_unread_amount_key(room_name=room_name)
        return rs.get(key)

    @staticmethod
    def increase_unread_amount(room_name):
        key = RedisKey.get_room_unread_amount_key(room_name=room_name)
        rs.incr(key)

    @staticmethod
    def decrease_unread_amount(room_name):
        key = RedisKey.get_room_unread_amount_key(room_name=room_name)
        rs.decr(key)

    @staticmethod
    def pop_expired_room():
        key = RedisKey.get_expired_room_key()
        return rs.lpop(key)

    @staticmethod
    def push_expired_room(room_id):
        key = RedisKey.get_expired_room_key()
        rs.rpush(key, room_id)

    @staticmethod
    def get_all_expired_room():
        key = 'expired:room'
        rooms = rs.lrange(key, 0, -1)
        return rooms

    """ AUTH LOCK """

    @classmethod
    def increase_member_auth_lock(cls, phone):
        key = RedisKey.get_member_auth_lock_key(phone=phone)
        rs.incr(key, amount=1)
        ttl = rs.ttl(key)
        expiration = ttl if ttl > 0 else cls._EXPIRATION_MEMBER_AUTH_INTERVAL
        rs.expire(key, time=expiration)

    @staticmethod
    def get_member_auth_lock(phone):
        """
        to block the member who try to
        login or refresh over 5 times in 5 seconds
        """
        key = RedisKey.get_member_auth_lock_key(phone=phone)
        return rs.get(key)

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

    @classmethod
    def set_player_transfer_lock(cls, user_id):
        key = RedisKey.transfer_lock(user_id=user_id)
        value = str(datetime.now())
        rs.set(key, value=value, ex=cls._TRANSFER_LOCK_INTERVAL)

    @staticmethod
    def get_player_transfer_lock(user_id):
        key = RedisKey.transfer_lock(user_id=user_id)
        return rs.get(key)

    @staticmethod
    def del_player_transfer_lock(user_id):
        key = RedisKey.transfer_lock(user_id=user_id)
        rs.delete(key)

    @classmethod
    def set_player_return_lock(cls, user_id):
        key = RedisKey.return_lock(user_id=user_id)
        value = str(datetime.now())
        rs.set(key, value=value, ex=cls._RETURN_LOCK_INTERVAL)

    @staticmethod
    def get_player_return_lock(user_id):
        key = RedisKey.return_lock(user_id=user_id)
        return rs.get(key)

    @staticmethod
    def del_player_return_lock(user_id):
        key = RedisKey.return_lock(user_id=user_id)
        rs.delete(key)

    """ MEMBER ACTIVITY """

    @classmethod
    def set_member_login_activity(cls, user_id, login_datetime, ex=None):
        """
            key: 印度日期
            value: 台灣時間
        """
        datetime_ = datetime.strptime(
            login_datetime, '%Y-%m-%d %H:%M:%S').astimezone(cls._IST_TIMEZONE)
        date_str = datetime_.date().strftime('%Y-%m-%d')
        name = RedisKey.get_member_login_record_key(date_=date_str)
        key = user_id
        value = login_datetime
        rs.hset(name=name, key=key, value=value)
        if rs.ttl(name) < 0:
            """ without expiration(first time) """
            ex = ex if ex is not None else cls._EXPIRATION_MEMBER_LOGIN_RECORD
            rs.expire(name, time=ex)

    @staticmethod
    def get_member_login_activity(date_, user_id):
        date_ = date_.strftime('%Y-%m-%d')
        name = RedisKey.get_member_login_record_key(date_=date_)
        key = user_id
        data = rs.hget(name=name, key=key)
        return datetime.strptime(data, '%Y-%m-%d %H:%M:%S') if data else None

    @staticmethod
    def get_all_member_login_activity(date_):
        date_ = date_.strftime('%Y-%m-%d')
        name = RedisKey.get_member_login_record_key(date_=date_)
        data = rs.hgetall(name=name)
        return {
            k: datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            for k, v in data.items()
        }

    @staticmethod
    def get_length_member_login_activity(date_):
        date_ = date_.strftime('%Y-%m-%d')
        name = RedisKey.get_member_login_record_key(date_=date_)
        return rs.hlen(name)

    """ SMS CALLBACK STATUS (PHONE) """

    @classmethod
    def set_twofactor_callback_sms_status(cls, phone, status):
        expiration = cls._EXPIRATION_TWOFACTOR_CALLBACK_STATUS
        key = RedisKey.get_twofactor_callback_sms_status_key(phone=phone)
        rs.set(key, value=status, ex=expiration)

    @staticmethod
    def get_twofactor_callback_sms_status(phone):
        key = RedisKey.get_twofactor_callback_sms_status_key(phone=phone)
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

    """ Exp """

    @classmethod
    def increase_member_month_exp(cls, year_month, member_id, exp, ex=None):
        ex = ex if ex is not None else cls._EXPIRATION_MEMBER_MONTH_EXP
        key = RedisKey.month_member_exp(
            year_month=year_month,
            member_id=member_id,
        )
        rs.incr(key, amount=exp)
        rs.expire(key, time=ex)

    @classmethod
    def get_member_month_exp(cls, year_month, member_id):
        """ need init by ExperienceTool.init_and_get_member_month_exp """
        key = RedisKey.month_member_exp(
            year_month=year_month,
            member_id=member_id,
        )
        return rs.get(key) if rs.get(key) else 0

    """ Vip Upgrade Notification """

    @classmethod
    def set_member_upgrade_notification(cls, member_id, new_level):
        key = RedisKey.member_upgrade(member_id=member_id)
        rs.set(key, value=new_level)

    @staticmethod
    def get_member_upgrade_notification(member_id):
        key = RedisKey.member_upgrade(member_id=member_id)
        return rs.get(key)

    @staticmethod
    def del_member_upgrade_notification(member_id):
        key = RedisKey.member_upgrade(member_id=member_id)
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

    """ User List """

    @staticmethod
    def get_export_user_list(role, keyword, sort_by, is_desc):
        key = RedisKey.export_user_list(role=role,
                                        keyword=keyword,
                                        sort_by=sort_by,
                                        is_desc=is_desc)
        return rs_f_decode.get(key) or None

    @classmethod
    def set_export_user_list(cls, value, role, keyword, sort_by, is_desc):
        key = RedisKey.export_user_list(role=role,
                                        keyword=keyword,
                                        sort_by=sort_by,
                                        is_desc=is_desc)
        rs.set(key, value=value, ex=cls._USER_REPORT_PERIOD)
