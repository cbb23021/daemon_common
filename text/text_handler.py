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

    _EMAIL_VERIFICATION_TEMPLATE = None
    """ EMAIL """

    @classmethod
    def _get_email_verification_template(cls):
        if cls._EMAIL_VERIFICATION_TEMPLATE is None:
            with open('common/text/email_verification.html', 'r') as fr:
                cls._EMAIL_VERIFICATION_TEMPLATE = fr.read()
        return cls._EMAIL_VERIFICATION_TEMPLATE

    @classmethod
    def get_verification_email(cls, otp):
        template = cls._get_email_verification_template()
        expiration = Toolkit.convert_seconds(
            seconds=Const.VerificationSystem.EMAIL_OTP_EXPIRATION, unit='hours')
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
