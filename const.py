class _ConstBase:
    """
    Proceed Constants
        - get_name: get the name of constant by type_, replaced "_" as " " and format by str().title()
        - get_type: format name by str().upper() and replaced " " as "_" to get the type of constant.

    e.g.
        class CONTINENT(_ConstBase):
            AFRICA = 1
            ASIA = 2
            EUROPE = 3
            NORTH_AMERICA = 4
            OCEANIA = 5
            SOUTH_AMERICA = 6

        continent = CONTINENT.get_name(CONTINENT.NORTH_AMERICA)
        print(continent)  ## North America

        continent_id = CONTINENT.get_type('nOrTh AMERICA')
        print(continent_id)  ## 4
    """

    _INVALID_TYPE = {classmethod, staticmethod}
    _STR_FORMAT_TYPE = {'title', 'upper', 'lower'}

    @classmethod
    def get_name(cls, type_, format_=None, blank_replacement=None):
        blank_replacement = blank_replacement or ' '
        if not isinstance(blank_replacement, str):
            raise ValueError(f'Invalid replacement {blank_replacement}')
        format_ = format_ or 'title'
        if format_.lower() not in cls._STR_FORMAT_TYPE:
            raise ValueError(f'Invalid format type {format_}')
        for k, v in cls.__dict__.items():
            if k.startswith('_') or type(v) in cls._INVALID_TYPE:
                continue
            if v == type_:
                return getattr(k.replace('_', blank_replacement),
                               format_.lower())()

    @classmethod
    def get_type(cls, name):
        for k, v in cls.__dict__.items():
            if k.startswith('_') or type(v) in cls._INVALID_TYPE:
                continue
            if isinstance(name, str) and k == name.replace(' ', '_').upper():
                return v

    @classmethod
    def validate_type(cls, type_):
        for k, v in cls.__dict__.items():
            if k.startswith('_') or type(v) in cls._INVALID_TYPE:
                continue
            if v == type_:
                return True
        raise ValueError(f'Invalid type of {cls.__name__}: {type_}')

    @classmethod
    def validate_name(cls, name):
        if not isinstance(name, str):
            raise TypeError(f'name must be str, not {type(name)}')
        if name.replace(' ', '_').upper() not in cls.__dict__:
            raise ValueError(f'Invalid type of {cls.__name__}: {name}')
        return True

    @classmethod
    def to_dict(cls, reverse=False, format_=None, blank_replacement=None):
        """
            class MatchStatus(_ConstBase):
                NOT_STARTED = 1
                STARTED = 2
                COMPLETED = 3

        to_dict()
            # {'Not Started': 1, 'Started': 2, 'Completed': 3}

        to_dict(reverse=True)
            # {1: 'Not Started', 2: 'Started', 3: 'Completed'}

        to_dict(format_='lower') or upper
            # {'not started': 1, 'started': 2, 'completed': 3}

        to_dict(blank_replacement='_')
            # {'Not_Started': 1, 'Started': 2, 'Completed': 3, 'Expired': 4, 'Unknown': 5}
        """
        blank_replacement = blank_replacement or ' '
        if not isinstance(blank_replacement, str):
            raise ValueError(f'Invalid replacement {blank_replacement}')
        format_ = format_ or 'title'
        if format_.lower() not in cls._STR_FORMAT_TYPE:
            raise ValueError(f'Invalid format type {format_}')
        result = dict()
        for k, v in cls.__dict__.items():
            if k.startswith('_') or type(v) in cls._INVALID_TYPE:
                continue
            k_formatted = getattr(k.replace('_', blank_replacement),
                                  format_.lower())()
            tmp = {v: k_formatted} if reverse else {k_formatted: v}
            result.update(tmp)
        return result


class Const:

    class RoleType(_ConstBase):
        OWNER = 11  # 超級管理員(所有權限)
        MAINTAINER = 12  # 管理員(除創建管理員外 所有權限)
        OPERATOR = 13  # 操作員(運營/審核/封控 權限)
        REPORTER = 14  # 客服員(僅有GET權限+客服)
        MARKETER = 15  # 營銷員(僅有GET權限)

        MEMBER = 21  # 常規玩家(前台註冊)
        SPECIAL_MEMBER = 22  # 特殊會員(後台建立)
        PROMOTE_MEMBER = 23  # 推廣會員(不可遊玩)

    class GroupType(RoleType):
        ADMIN = 1  # 管理員
        USER = 2  # 用戶

        @classmethod
        def get_roles(cls, type_):
            if type_ == cls.ADMIN:
                return {
                    cls.OWNER, cls.MAINTAINER, cls.OPERATOR, cls.REPORTER,
                    cls.MARKETER
                }
            if type_ == cls.USER:
                return {cls.MEMBER, cls.SPECIAL_MEMBER, cls.PROMOTE_MEMBER}
            raise ValueError(f'Invalid type of group: {type_}')

    class AssetType(_ConstBase):
        CASH = 1
        TICKET = 2

    class WalletType(_ConstBase):
        CASH = 1
        TICKET = 2

    class VerificationSystem:
        # 需要在5分鐘內輸入OTP
        EMAIL_OTP_EXPIRATION = 5 * 60
        # 在10分鐘內，最多嘗試5次驗證
        EMAIL_OTP_RETRY_INTERVAL = 10 * 60
        EMAIL_OTP_ATTEMPT_MAXIMUM = 5
        # 需要在驗證通過後10分鐘內完成註冊
        VERIFIED_EMAIL_EXPIRATION = 10 * 60

        RESET_PASSWORD_RETRY_INTERVAL = 3 * 60
        RESET_PASSWORD_ATTEMPT_MAXIMUM = 1

    class Task:

        class Type(_ConstBase):
            REGISTER = 1
            GAME = 2

    class Transaction:
        NUMBER_LENGTH = '11'  # 交易單號 數字部分位數

        class Category(_ConstBase):
            EARNED = 'earned'
            USED = 'used'

        class Type(_ConstBase):
            # TASK
            TASK_PRIZE = 'TAPR'  # TAsk PRize

            # REWARD
            REWARD_PRIZE = 'RWPR'  # ReWard PRize

    class SystemInfoType(_ConstBase):
        ABOUT_US = 1
        FAIR_PLAY_VIOLATION = 2
        LEGALITIES = 3
        TERMS_AND_CONDITIONS = 4
        PRIVACY_POLICY = 5
        REFUND_POLICY = 6
        CONTACT_US = 7
        FAQ = 8

    class State(_ConstBase):
        ANDHRA_PRADESH = 1
        ARUNACHAL_PRADESH = 2
        BIHAR = 3
        CHHATTISGARH = 4
        GOA = 5
        GUJARAT = 6
        HARYANA = 7
        HIMACHAL_PRADESH = 8
        JHARKHAND = 9
        KARNATAKA = 10
        KERALA = 11
        MADHYA_PRADESH = 12
        MAHARASHTRA = 13
        MANIPUR = 14
        MEGHALAYA = 15
        MIZORAM = 16
        PUNJAB = 17
        RAJASTHAN = 18
        SIKKIM = 19
        TAMIL_NADU = 20
        TRIPURA = 21
        UTTAR_PRADESH = 22
        UTTARAKHAND = 23
        WEST_BENGAL = 24
        JAMMU = 25
        KASHMIR = 26

    class Order:

        class Type(_ConstBase):
            TASK = 1
            REWARD = 2

    class MethodType(_ConstBase):
        GET = 1
        POST = 2
        PUT = 3
        DELETE = 4

    class AddressType(_ConstBase):
        WHITELIST = 1
        BLACKLIST = 2

    class RewardType(_ConstBase):
        REGISTER = 1
        FIRST_DEPOSIT = 2
        DEPOSIT = 3
        JOIN_CONTEST = 4
        CUSTOM = 5
