from flask_mail import Message

from app import app, config, mail
from common.error_handler import ErrorCode, ValidationError
from common.text.text_handler import TextHandler
from common.utils.data_cache import DataCache
from common.utils.encrypt_tool import KeyGenerator


class EmailHandler:
    _SENDER = (config['APP_NAME'], config['MAIL_USERNAME'])
    _APP_NAME = config['APP_NAME']

    _MAP = {
        TextHandler._TASK_REGESTER: TextHandler.get_verification_email,
        TextHandler._TASK_RESET_PASSWORD: TextHandler.get_reset_password,
    }

    @classmethod
    def _send(cls, email, title, content):
        if isinstance(email, str):
            recipients = [email]
        else:
            recipients = email
        message = Message(sender=cls._SENDER,
                          recipients=recipients,
                          subject=title,
                          html=content)
        mail.send(message)
        print(f'[{title}] to {email}')

    @classmethod
    def send_verification(cls, email, task):
        otp = KeyGenerator.get_random_code(number=5, has_digit=True)
        title, content = cls._MAP[task](otp=otp)
        DataCache.del_verify_email_otp(email=email)
        DataCache.set_verify_email_otp(email=email, otp=otp)
        with app.app_context():
            cls._send(email=email, title=title, content=content)

    @classmethod
    def verify_email(cls, email, otp):
        attempts = DataCache.get_verify_email_attempt(email=email)
        if not attempts:
            raise ValidationError(error_code=ErrorCode.EMAIL_NOT_VERIFIED,
                                  message='email is incorrect')
        valid_otp = DataCache.get_verify_email_otp(email=email)
        if not valid_otp:
            message = 'OTP is expired, please start over again'
            raise ValidationError(error_code=ErrorCode.OTP_IS_EXPIRED,
                                  message=message)
        if otp != valid_otp:
            message = f'OTP: {otp} is incorrect'
            raise ValidationError(error_code=ErrorCode.INVALID_OTP,
                                  message=message)

    @classmethod
    def verify_verified_email(cls, email, otp):
        attempts = DataCache.get_verify_email_attempt(email=email)
        if not attempts:
            raise ValidationError(error_code=ErrorCode.EMAIL_NOT_VERIFIED,
                                  message='email is incorrect')
        valid_otp = DataCache.get_verified_email(email=email)
        if not valid_otp:
            message = 'OTP is expired, please start over again'
            raise ValidationError(error_code=ErrorCode.OTP_IS_EXPIRED,
                                  message=message)
        if otp != valid_otp:
            message = f'OTP: {otp} is incorrect'
            raise ValidationError(error_code=ErrorCode.INVALID_OTP,
                                  message=message)
