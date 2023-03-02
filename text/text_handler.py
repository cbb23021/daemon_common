from datetime import date
from string import Template

from app import config
from common.const import Const
from common.utils.toolkit import Toolkit


class TextHandler:
    """
    文本管理
    """
    _APP_NAME = config['APP_NAME']

    _FONT_FAMILIES = ','.join({
        'Whitney', 'Helvetica Neue', 'Helvetica', 'Arial', 'Lucida Grande',
        'sans-serif'
    })

    _TASK_REGESTER = 'register'
    _TASK_RESET_PASSWORD = 'reset_password'

    _TEMP_MAP = {
        _TASK_REGESTER: '',
        _TASK_RESET_PASSWORD: '',
    }
    """ EMAIL """

    @classmethod
    def _read(cls, task, path):
        if not cls._TEMP_MAP[task]:
            with open(path, 'r') as fr:
                cls._TEMP_MAP[task] = fr.read()
        return cls._TEMP_MAP[task]

    @classmethod
    def get_verification_email(cls, otp):
        template = cls._read(task=cls._TASK_REGESTER,
                             path='common/text/email_verification.html')
        expiration = Toolkit.convert_seconds(
            seconds=Const.VerificationSystem.EMAIL_OTP_EXPIRATION,
            unit='minutes')
        font_families = cls._FONT_FAMILIES
        content = Template(template).substitute(
            app_name=cls._APP_NAME,
            expiration=expiration,
            font_families=font_families,
            code=otp,
            current_year=date.today().year,
        )
        title = f'Welcome to {cls._APP_NAME}'
        return title, content

    @classmethod
    def get_reset_password(cls, otp):
        template = cls._read(task=cls._TASK_RESET_PASSWORD,
                             path='common/text/reset_password.html')
        font_families = cls._FONT_FAMILIES
        content = Template(template).substitute(
            app_name=cls._APP_NAME,
            font_families=font_families,
            code=otp,
            current_year=date.today().year,
        )
        title = f'Reset Password in {cls._APP_NAME}'
        return title, content
