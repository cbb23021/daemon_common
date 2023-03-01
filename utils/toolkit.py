import re
from datetime import date, datetime
from distutils import version
from functools import wraps

from flask import request

from app import config
from common.error_handler import ErrorCode, ValidationError
from common.utils.data_cache import DataCache


class Toolkit:
    _VERSION_TAG_LENGTH = 2

    _TIME_CONVERT_SETTING = {
        'minutes': 60,
        'hours': 3600,
        'days': 86400,
    }

    _REGEX_DATE = re.compile(
        r'^(\d{4})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$')

    @classmethod
    def convert_seconds(cls, seconds, unit='hours'):
        """
        :param seconds:
        :type seconds: int
        :param unit: {'days', 'hours', 'minutes'}
        :type unit: str
        """
        if not isinstance(seconds, int):
            raise TypeError('Invalid Type of param seconds')
        if not isinstance(unit, str):
            raise TypeError('Invalid Type of param unit')
        if unit not in cls._TIME_CONVERT_SETTING:
            raise ValueError('Invalid Value of param unit')
        return seconds // cls._TIME_CONVERT_SETTING.get(unit)

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
        if version.StrictVersion(constrain) > version.StrictVersion(
                client_version):
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

    @classmethod
    def _get_request_payload(cls, payload, has_payload):
        if not (has_payload and payload):
            return str()
        return cls._sort_key(data=payload)

    @staticmethod
    def _sort_key(data):
        return '|'.join(f'{key}={data[key]}' for key in sorted(data))

    @classmethod
    def _get_request_args(cls, has_args):
        if not has_args:
            return str()
        return cls._sort_key(data=request.args)

    @staticmethod
    def _get_request_user(data):
        user = data.get('user')
        if user:
            return user
        raise ValidationError(error_code=ErrorCode.DATA_ERROR,
                              message='User Is Required')

    @classmethod
    def request_lock(cls,
                     ex=None,
                     has_args=False,
                     has_payload=False,
                     has_user=True):

        def real_decorator(method, **kwargs):

            @wraps(method)
            def wrapper(*args, **kwargs):
                user = None
                if has_user:
                    user = cls._get_request_user(data=kwargs)
                request_method = request.method
                request_path = request.path
                request_args = cls._get_request_args(has_args=has_args, )
                request_payload = cls._get_request_payload(
                    payload=request.get_json(),
                    has_payload=has_payload,
                )
                request_lock = DataCache.get_request_lock(
                    user_id=user.id if user else str(),
                    role=user.role if user else str(),
                    request_method=request_method,
                    request_path=request_path,
                    request_args=request_args,
                    request_payload=request_payload,
                )
                if request_lock:
                    message = 'Request Frequency Too High'
                    raise ValidationError(
                        error_code=ErrorCode.INVALID_OPERATION,
                        message=message)
                DataCache.set_request_lock(
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
    def validate_date_format(cls, date_):
        if not isinstance(date_, str):
            message = f'Type required str, not {type(date_)}'
            raise ValidationError(error_code=ErrorCode.DATA_ERROR,
                                  message=message)
        if not cls._REGEX_DATE.match(date_):
            message = f'Format required YYYY-MM-DD, not {date_}'
            raise ValidationError(error_code=ErrorCode.DATA_ERROR,
                                  message=message)

    @staticmethod
    def format_datetime(datetime_, format_=None):
        return datetime_.strftime(format_ or '%F %X')

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
            raise ValidationError(error_code=ErrorCode.DATA_ERROR,
                                  message=message)
        return datetime.strptime(date_, format_).date()

    @classmethod
    def get_payload(cls):
        # 解析 post 的 request data
        def real_decorator(method, **kwargs):

            @wraps(method)
            def wrapper(*args, **kwargs):
                payload = request.form
                if not payload:
                    payload = request.get_json(force=True)
                else:
                    payload = dict(payload)
                return method(*args, **kwargs, payload=payload)

            return wrapper

        return real_decorator
