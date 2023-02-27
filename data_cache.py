import json
from datetime import datetime

from app import rs, config
from common.orm.fantasyee_models import Team, League, Squad, Match
from common.redis_key.fantasyee import FantasyeeRedisKey


class FantasyeeDataCache:
    _EXPIRATION_LONG_TERM = 60 * 60 * 24 * 3
    _EXPIRATION_MID_TERM = 60 * 60 * 24
    _EXPIRATION_SHORT_TERM = 60 * 5

    _EXPIRATION_MATCH = 60 * 60 * 24 * 10

    _EXPIRATION_POINT = 60 * 5
    _EXPIRATION_SDK_LOGIN = 60 * 60 * 24

    _EXPIRATION_MEMBER_TODAY_WIN_LOSS = 60 * 30

    _MEMBER_TRANSFER_INTERVAL = 10
    _MEMBER_JOIN_INTERVAL = 1
    _REQUEST_LOCK_INTERVAL = 1

    _EXPIRATION_DAILY_MEMBER_EXP = 60 * 60 * 24 * 31
    _INIT_DAILY_MEMBER_EXP = 0

    _STATIC_HOST = config.get('STATIC_HOST')
    _ENVIRONMENT = config['ENVIRONMENT']
    _APP_NAME = config['APP_NAME'].lower()
    _DEV_ENVIRONMENT = {
        'develop',
        'release',
    }

    @staticmethod
    def del_key(key):
        rs.delete(key)

    @classmethod
    def set_member_login(cls, member_info):
        member = member_info['member']
        key = FantasyeeRedisKey.member_login(member_id=member.id)
        player_info = {
            'id': member.id,
            'username': member.username,
            'nickname': member.nickname,
            'role': member.role,
            'is_active': member.is_active,
            'remark': member.remark,
            'coin': member.wallet.coin,
            'cash': member.wallet.cash,
            'login_token': member_info['login_token'],
            'access_token': member_info['access_token'],
            'refresh_token': member_info['refresh_token'],
            'avatar': member.avatar,
        }
        rs.set(key, value=json.dumps(player_info), ex=cls._EXPIRATION_SDK_LOGIN)

    @classmethod
    def update_member_login(cls, member_id, member_info):
        key = FantasyeeRedisKey.member_login(member_id=member_id)
        rs.set(key, value=json.dumps(member_info), ex=cls._EXPIRATION_SDK_LOGIN)

    @staticmethod
    def get_member_login(member_id):
        key = FantasyeeRedisKey.member_login(member_id=member_id)
        value = rs.get(key)
        return json.loads(value) if value else None

    @classmethod
    def flush_transaction(cls):
        """ 於 entry point 呼叫 重置 transaction Lock """
        for key in rs.scan_iter(f'*transaction*'):
            cls.del_key(key=key)

    # ----------------------------- [lock] ----------------------------- #

    @classmethod
    def set_sdk_deposit_lock(cls, member_id):
        key = FantasyeeRedisKey.sdk_deposit_lock(member_id=member_id)
        value = str(datetime.now())
        rs.set(key, value=value, ex=cls._MEMBER_TRANSFER_INTERVAL)

    @staticmethod
    def get_sdk_deposit_lock(member_id):
        key = FantasyeeRedisKey.sdk_deposit_lock(member_id=member_id)
        return rs.get(key)

    @classmethod
    def set_request_lock(cls, role, user_id, request_method, request_path, request_args, request_payload, ex=None):
        key = FantasyeeRedisKey.request_lock(
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
    def get_request_lock(user_id, role, request_method, request_path, request_args, request_payload):
        key = FantasyeeRedisKey.request_lock(
            role=role,
            user_id=user_id,
            request_method=request_method,
            request_path=request_path,
            request_args=request_args,
            request_payload=request_payload,
        )
        return rs.get(key)

    # ----------------------------- [order] ----------------------------- #
    @staticmethod
    def get_spare_order_id(contest_id):
        key = FantasyeeRedisKey.wait_order_ids(contest_id=contest_id)
        return rs.rpop(key)

    @staticmethod
    def push_order_data_to_wait(contest_id, value):
        key = FantasyeeRedisKey.wait_order_ids(contest_id)
        return rs.rpush(key, *value)

    @staticmethod
    def get_used_order_data(contest_id, wait_time=10):
        key = FantasyeeRedisKey.used_order_data(contest_id)
        return rs.blpop(key, wait_time)

    @staticmethod
    def push_order_data_to_used(contest_id, order_id, member_id, lineup_id, cash, coin, winnings, ticket, bet_datetime):
        key = FantasyeeRedisKey.used_order_data(contest_id=contest_id)
        value = f'{order_id}:{member_id}:{lineup_id}:{cash}:{coin}:{winnings}:{ticket}:{bet_datetime}'
        rs.lpush(key, value)

    # --------------------------------- active contest signal to daemon ---------------------------------- #

    @staticmethod
    def get_active_contest_id(wait_time=10):
        key = FantasyeeRedisKey.active_contest_ids()
        return rs.blpop(key, wait_time)

    @staticmethod
    def push_active_contest_ids(contest_ids):
        key = FantasyeeRedisKey.active_contest_ids()
        return rs.lpush(key, *contest_ids)

    # --------------------------------- cancel contest signal to daemon ---------------------------------- #
    @staticmethod
    def set_cancel_contest_signal(contest_id):
        key = FantasyeeRedisKey.cancel_contest_ids()
        rs.sadd(key, contest_id)

    @staticmethod
    def get_cancel_contest_signal():
        key = FantasyeeRedisKey.cancel_contest_ids()
        ids = rs.smembers(key)
        return ids or set()

    @staticmethod
    def del_cancel_contest_signal(contest_id):
        key = FantasyeeRedisKey.cancel_contest_ids()
        rs.srem(key, contest_id)
