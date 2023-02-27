import random
import re
import string

import jwt
import secrets

from datetime import datetime, timedelta

from app import bcrypt
from config import Config
from common.error_handler import ErrorCode, NotAuthorizedError


class Encrypt:

    @staticmethod
    def encrypt_password(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def check_password(db_password, input_password):
        return bcrypt.check_password_hash(db_password, input_password)


class JWTCoder:

    @staticmethod
    def _get_token(expire_time, salt, **kwargs):
        payload = {
            **kwargs,
            'exp': expire_time
        }
        return jwt.encode(payload=payload, key=salt, algorithm='HS256').decode('utf-8')

    @staticmethod
    def _decode(token, salt):
        try:
            return jwt.decode(jwt=token, key=salt, algorithm='HS256')
        except jwt.DecodeError:
            raise NotAuthorizedError(error_code=ErrorCode.INVALID_ACCESS_TOKEN)
        except jwt.ExpiredSignatureError:
            raise NotAuthorizedError(error_code=ErrorCode.ACCESS_TOKEN_IS_EXPIRED)

    @classmethod
    def get_access_token(cls, **kwargs):
        time_offset = timedelta(seconds=Config.ACCESS_TOKEN_EXPIRE_TIME)
        expire_time = datetime.utcnow() + time_offset
        return cls._get_token(expire_time=expire_time, salt=Config.SALT, **kwargs)

    @classmethod
    def get_refresh_token(cls, **kwargs):
        time_offset = timedelta(seconds=Config.REFRESH_TOKEN_EXPIRE_TIME)
        expire_time = datetime.utcnow() + time_offset
        return cls._get_token(expire_time=expire_time, salt=Config.SALT, **kwargs)

    @classmethod
    def decode_access_token(cls, token):
        return cls._decode(token=token, salt=Config.SALT)

    @classmethod
    def decode_refresh_token(cls, token):
        return cls._decode(token=token, salt=Config.SALT)


class KeyGenerator:

    @classmethod
    def get_sdk_secret_key(cls):
        """
        1 nbytes approximately 1.3 characters
        math.ceil(15 * 1.3) == 20
        故，長度為 20
        """
        return secrets.token_urlsafe(nbytes=15)

    @staticmethod
    def get_random_code(number, has_digit=True, has_lower=False, has_upper=False, has_punctuation=False):
        if not isinstance(number, int) or number < 1:
            raise ValueError('number required int and it should be great than zero')
        if not any([has_digit, has_lower, has_upper, has_punctuation]):
            raise ValueError('one or more pattern is required')
        pattern = str()
        if has_digit:
            pattern = f'{pattern}{string.digits}'
        if has_lower:
            pattern = f'{pattern}{string.ascii_lowercase}'
        if has_upper:
            pattern = f'{pattern}{re.sub(f"[OI]", "", string.ascii_uppercase)}'
        if has_punctuation:
            pattern = f'{pattern}{string.punctuation}'
        return ''.join(random.choice(pattern) for _ in range(number))
