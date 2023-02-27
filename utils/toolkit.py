import base64
import hashlib
import hmac
import re
from datetime import datetime, date, timedelta
from distutils import version
from functools import wraps

import pytz
from flask import request

from app import config
from common.const import Const
from common.data_cache.fantasyee import FantasyeeDataCache
from common.error_handler import ErrorCode, ValidationError


class Toolkit:
    _VERSION_TAG_LENGTH = 2

    _SDK_STRICT_METHODS = {
        Const.SdkType.DEPOSIT,
        Const.SdkType.WITHDRAW,
        Const.SdkType.MEMBER_LOGIN,
        Const.SdkType.UPDATE_MEMBER,
        Const.SdkType.GAME_RECORD,
    }

    # agent + username = unique user
    _SDK_PAYLOAD_KEYS = {
        'method',
        'agent',
        'username',
    }

    _REGEX_DATE = re.compile(r'^(\d{4})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$')

    # IST: India Standard Timezone
    _IST_TIMEZONE_NAME = 'Asia/Kolkata'
    IST_TIMEZONE = pytz.timezone(_IST_TIMEZONE_NAME)

    _TIME_DIFF = timedelta(hours=2, minutes=30)

    @staticmethod
    def make_signature(payload, secret_key):
        """
        依照 key 做排序並且加密
        :param payload:
        :param secret_key:
        :return:
        """
        un_hashed_str = str()
        for key, value in sorted(payload.items(), key=lambda x: x[0]):
            if value is None:
                continue
            un_hashed_str = f'{un_hashed_str}{value}'
        hashed_value = hmac.new(
            secret_key.encode('utf-8'),
            un_hashed_str.encode('utf-8'),
            hashlib.sha1
        ).digest()
        hashed_str = base64.b64encode(hashed_value).decode('utf-8')
        return hashed_str

    @classmethod
    def _validate_version(cls, client_version):
        """
        version format f'\d+\.\d+'
        client's version must greater equal than constrain
        """
        constrain = config['CONSTRAIN_VERSION']
        if not client_version:
            raise ValidationError(ErrorCode.APP_VERSION_DETAIL_IS_MISSING)
        client_tags = client_version.split('.')
        if len(client_tags) != cls._VERSION_TAG_LENGTH:
            raise ValidationError(ErrorCode.APP_VERSION_FORMAT_ERROR)
        for tag in client_tags:
            if tag.isdigit():
                continue
            raise ValidationError(ErrorCode.APP_VERSION_FORMAT_ERROR)
        if version.StrictVersion(constrain) > version.StrictVersion(client_version):
            error_code = ErrorCode.APP_VERSION_IS_OUT_OF_DATE
            message = f'App Version: {client_version} Current Version: {constrain}'
            raise ValidationError(error_code=error_code, message=message)

    @classmethod
    def inspect_version(cls):
        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                # ================== 測試環境使用 ================== #
                if config['ENVIRONMENT'] in ['develop', 'release']:
                    dev_ver = request.args.get('ver', type=str, default=None)
                else:
                    dev_ver = None
                # ================== 測試環境使用 ================== #
                client_version = request.headers.get('version', dev_ver)
                cls._validate_version(client_version=client_version)
                return method(*args, **kwargs)

            return wrapper

        return real_decorator

    @staticmethod
    def parse_pager(paginate):
        pager = {
            'page': paginate.page,
            'pages': paginate.pages,
            'per_page': paginate.per_page,
            'total': paginate.total,
        }
        return pager

    @staticmethod
    def _get_request_user(data, is_sdk):
        if is_sdk:
            user = data.get('member')
        else:
            user = data.get('user')
        if user:
            return user
        raise ValidationError(error_code=ErrorCode.DATA_ERROR, message='User Is Required')

    @staticmethod
    def _sort_key(data):
        return '|'.join(f'{key}={data[key]}' for key in sorted(data))

    @classmethod
    def _get_request_args(cls, data, has_args):
        if not has_args:
            return str()
        return cls._sort_key(data=request.args)

    @classmethod
    def _get_request_payload(cls, payload, is_sdk, has_payload):
        if not (has_payload or is_sdk):
            return str()
        if not payload:
            return str()
        sdk_method = payload.get('method')
        if is_sdk and sdk_method in cls._SDK_STRICT_METHODS:
            data = {k: payload.get(k) for k in cls._SDK_PAYLOAD_KEYS}
            return cls._sort_key(data=data)
        return cls._sort_key(data=payload)

    @classmethod
    def request_lock(cls, ex=None, is_sdk=False, has_args=False, has_payload=False, has_user=True):
        def real_decorator(method, **kwargs):
            @wraps(method)
            def wrapper(*args, **kwargs):
                user = None
                if has_user:
                    user = cls._get_request_user(data=kwargs, is_sdk=is_sdk)
                request_method = request.method
                request_path = request.path
                request_args = cls._get_request_args(
                    data=request.args,
                    has_args=has_args,
                )
                request_payload = cls._get_request_payload(
                    payload=request.get_json(),
                    is_sdk=is_sdk,
                    has_payload=has_payload,
                )
                request_lock = FantasyeeDataCache.get_request_lock(
                    user_id=user.id if user else str(),
                    role=user.role if user else str(),
                    request_method=request_method,
                    request_path=request_path,
                    request_args=request_args,
                    request_payload=request_payload,
                )
                if request_lock:
                    message = 'Request Frequency Too High'
                    raise ValidationError(error_code=ErrorCode.INVALID_OPERATION, message=message)
                FantasyeeDataCache.set_request_lock(
                    role=user.role if user else str(),
                    user_id=user.id if user else str(),
                    request_method=request_method,
                    request_path=request_path,
                    request_args=request_args,
                    request_payload=request_payload,
                    ex=ex,
                )
                return method(*args, **kwargs)

            return wrapper

        return real_decorator

    @classmethod
    def _parse_timezone(cls, timezone):
        if not timezone:
            return cls.IST_TIMEZONE
        try:
            return pytz.timezone(timezone)
        except Exception as e:
            raise ValidationError(error_code=ErrorCode.DATA_ERROR, message=f'Invalid TZ info: {timezone}')

    @staticmethod
    def _format_to_date(date_):
        if isinstance(date_, date):
            return date_
        elif isinstance(date_, str):
            return datetime.strptime(date_, '%Y-%m-%d').date()
        elif isinstance(date_, datetime):
            return date_.date()
        else:
            raise TypeError(f'Invalid type of date_ {type(date_)}')

    @classmethod
    def to_timezone_interval(cls, date_a, date_b=None, timezone=None):
        """
        Convert CST+5:30(IST) DATE to GMT+8:00(Asia/Taipei) DATETIME to filter out data from GMT+8 database
        if date_b is None return default one day interval
        e.g.
            _to_ist_interval(date_a='2022-01-01'))
            return 2021-12-31 21:30:00, 2022-01-01 21:29:59

            _to_ist_interval(date_a='2022-01-01', date_b='2022-01-05'))
            return 2021-12-31 21:30:00, 2021-01-01 21:29:59.999999

        :param date_a: parse date
        :type date_a: [str, datetime, date]
        :param date_b: second parse date
        :type date_b: [str, datetime, date]
        :param timezone: timezone
        :type timezone: str
        :rtype: datetime.datetime, datetime.datetime
        :return: start_point, end_point
        """
        date_b = date_b or date_a
        timezone = cls._parse_timezone(timezone=timezone)
        start_date = cls._format_to_date(date_=date_a)
        end_date = cls._format_to_date(date_=date_b)
        if start_date > end_date:
            """ reverse if the order went wrong """
            start_date, end_date = end_date, start_date
        start = datetime.combine(
            start_date, datetime.min.time()
        ).astimezone(timezone)
        end = datetime.combine(
            end_date, datetime.max.time()
        ).astimezone(timezone)
        return start, end

    @classmethod
    def parse_date(cls, date_, default=None, format_=None):
        """
            1. Get date return date
            2. Get datetime convert to date
            3. Get None return default or today
            4. Get string parse as date object
        """
        if not date_:
            return default or date.today()
        format_ = format_ or '%Y-%m-%d'
        if isinstance(date_, date):
            return date_
        if isinstance(date_, datetime):
            return date_.date()
        if not isinstance(date_, str):
            message = f'Invalid type of date_ {type(date_)}'
            raise Exception(message)
        if not cls._REGEX_DATE.match(date_):
            message = f'Format required {format_}, not {date_}'
            raise ValidationError(error_code=ErrorCode.DATA_ERROR, message=message)
        return datetime.strptime(date_, format_).date()

    @classmethod
    def from_ist_to_tst_timezone(cls, datetime_):
        """ IST(INDIA) to TST(TAIWAN) """
        if not isinstance(datetime_, datetime):
            if isinstance(datetime_, str):
                datetime_ = datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S')
            else:
                raise TypeError(f'Invalid type of datetime_ {type(datetime_)}')
        tst_datetime = datetime_ + cls._TIME_DIFF
        return tst_datetime
