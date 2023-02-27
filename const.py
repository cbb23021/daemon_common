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
        OWNER = 11  # 系統擁有者
        MAINTAINER = 12  # 系統維護人員
        MERCHANT = 13  # 遊戲管理員

        MEMBER = 21  # 玩家

    class GroupType(RoleType):
        ADMIN = 1  # 管理員
        USER = 2  # 用戶

        # SYSTEM = 3  # 系統(未使用)

        @classmethod
        def get_roles(cls, type_):
            if type_ == cls.ADMIN:
                return {cls.OWNER, cls.MAINTAINER, cls.MERCHANT}
            if type_ == cls.USER:
                return {cls.MEMBER}
            raise ValueError(f'Invalid type of group: {type_}')

    class MethodType(_ConstBase):
        GET = 1
        POST = 2
        PUT = 3
        DELETE = 4

    class SettleType(_ConstBase):
        ORDINAL = 1
        PERCENTAGE = 2

    class OrderType(_ConstBase):
        PENDING = 11
        SUCCEED = 1
        CLOSED = 2
        CANCELED = 3

    class Transaction:
        FEE = 'MBFE'  # MemBer FEe 費用
        PRIZE = 'MBPZ'  # MemBer PriZe 獎金

    class ContestStatus:
        CREATED = 1
        ACTIVATED = 2
        CANCELED = 3
