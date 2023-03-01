"""
- 錯誤代碼定義
- 錯誤類別 & 錯誤類別基底
"""


class ErrorCode:
    """
    1. 系統錯誤
    """
    BASE_ERROR = 1001  # 基本錯誤
    UNKNOWN_ERROR = 1002  # 未知錯誤

    """
    2. 資料錯誤
    """
    # SERVER(20-)
    DATA_ERROR = 2001  # 資料錯誤
    DATA_MISSING = 2002  # 資料遺漏
    DATA_REQUIRED = 2004  # 必須提供的資料
    DATA_IMMUTABLE = 2005  # 不可變動

    # CLIENT(21-)
    PAYLOAD_ERROR = 2101  # 酬載錯誤
    PAYLOAD_MISSING_KEY = 2102  # 缺少必要鍵
    PAYLOAD_UNEXPECTED_TYPE = 2103  # 型別錯誤
    JSON_DECODE_ERROR = 2104  # JSON 格式錯誤

    """
    3. 操作錯誤
        - 授權錯誤
        - 操作錯誤
        - 驗證錯誤
        - 檢查錯誤
    """

    # 簡述(30-)
    INVALID_OPERATION = 3001  # 無效的操作
    INVALID_PERMISSION = 3002  # 權限不足
    INVALID_ACCESS_TOKEN = 3003  # 無效通行証書
    INVALID_REFRESH_TOKEN = 3004  # 無效重置証書
    INVALID_PHONE_NUMBER = 3005  # 無效手機號碼
    INVALID_EMAIL = 3006  # 無效信箱
    INVALID_USERNAME = 3007  # 無效使用者名稱
    INVALID_PASSWORD = 3008  # 無效密碼
    INVALID_VERIFY_CODE = 3009  # 無效驗證代碼
    INVALID_KEYWORD_LENGTH = 3010  # 無效關鍵字長度
    INVALID_FILE_SIZE = 3011  # 無效檔案大小
    INVALID_IMAGE_FORMAT = 3012  # 無效圖片格式
    INVALID_BIRTHDAY_FORMAT = 3013  # 無效生日格式
    INVALID_IP_ADDRESS = 3014  # 無效遠端IP地址

    # 細述(31-)
    ACCESS_TOKEN_MISSING = 3101  # 未包含通行証
    ACCESS_TOKEN_IS_EXPIRED = 3102  # 通行証過期
    CONTAIN_FORBIDDEN_CHARACTER = 3103  # 含有非法字元
    EMAIL_IS_EXIST = 3104  # 重複的電子郵件
    REACHED_MAXIMUM_RETRY_ATTEMPTS = 3105  # 觸及最大嘗試次數
    USERNAME_IS_EXIST = 3106  # 重複的使用者名稱
    USERNAME_IS_NOT_EXIST_OR_PASSWORD_IS_WRONG = 3107  # 使用者不存在或密碼錯誤
    USER_IS_LOCKED = 3108  # 使用者被鎖定
    USER_IS_BLOCKED = 3109  # 使用者被凍結
    USER_NOT_FOUND = 3110  # 使用者不存在
    VERIFY_OPERATION_REPEATEDLY = 3111  # 短時間重複操作驗證
    SIGNATURE_ERROR = 3112  # 簽名錯誤
    AMOUNT_INSUFFICIENT = 3113  # 餘額不足
    AMOUNT_INVALID = 3114  # 金額條件不符
    FILE_NOT_EXIST = 3115  # 檔案不存在
    REACHED_RESET_PASSWORD_MAXIMUM = 3116  # 觸及密碼重設最大額度
    REFERRAL_CODE_NOT_EXIST = 3117  # 邀請碼不存在
    APP_VERSION_DETAIL_IS_MISSING = 3118  # 表頭未包含版本資訊
    APP_VERSION_IS_OUT_OF_DATE = 3119  # APP版本過時
    APP_VERSION_FORMAT_ERROR = 3120  # 錯誤的APP版本格式
    MESSAGE_ROOM_IS_NOT_EXIST = 3121  # 聊天室不存在
    SESSION_IS_NOT_EXIST = 3122  # 連線id不存在
    PHONE_IS_EXIST = 3123  # 重複的手機號碼
    PHONE_IS_NOT_EXIST = 3124  # 手機不存在
    OTP_IS_EXPIRED = 3125  # OTP 過期
    INVALID_OTP = 3126  # OTP 錯誤

    """
    9.  專案用錯誤

    e.g.
    SUPERIOR_IS_LOCKED = 9001  # 上層用戶鎖定
    PROVIDER_NOT_FOUND = 9002  # 遊戲商被刪除或不存在
    PROVIDER_IS_BLOCKED = 9003  # 遊戲商凍結
    PREFIX_NOT_FOUND = 9004  # 子用戶所用前綴不存在
    GAME_IS_BLOCKED = 9005  # 遊戲凍結
    GAME_NOT_FOUND = 9006  # 遊戲被刪除或不存在
    REACHED_RESET_PASSWORD_MAXIMUM = 9007  # 觸及密碼重設最大額度
    """
    API_CONNECTION_ERROR = 9001  # 請求第三方API失敗
    INVALID_PAN_DETAILS = 9002  # PAN 驗證失敗
    INVALID_PAN_NUMBER = 9003  # PAN NUMBER 格式錯誤
    INVALID_BANK_ACCOUNT = 9004  # 銀行帳戶不合法
    BANK_NAME_INCORRECT = 9005  # 銀行名稱不正確
    BRANCH_NAME_INCORRECT = 9006  # 分行名稱不正確
    BANK_ACCOUNT_NOT_FOUND = 9007  # 銀行帳戶不存在
    PHONE_NOT_BOUND = 9008  # 手機號碼未綁定
    PHONE_NOT_VERIFIED = 9009  # 手機號碼未驗證
    PHONE_HAS_BEEN_VERIFIED = 9010  # 手機已驗證過
    EMAIL_NOT_VERIFIED = 9011  # 信箱未驗證過
    EMAIL_HAS_BEEN_VERIFIED = 9012  # 信箱已驗證過

    # ===== deposit ===== #
    TICKET_NUMBER_IS_EXIST = 9200  # 商戶單號已經存在
    TICKET_NOT_IN_PROCESSING = 9201  # 訂單非正確狀態
    TICKET_NOT_EXIST = 9202  # 三方單不存在
    DEPOSIT_CHANNEL_NOT_EXIST = 9203  # 渠道不存在
    DEPOSIT_CHANNEL_SETTING_NOT_EXIST = 9204  # 設定不存在
    DEPOSIT_TICKET_NOT_FOUND = 9205  # 訂單不存在
    REQUEST_UPSTREAM_FAILED = 9206  # 請求上游失敗
    LINK_EXPIRED = 9207  # payment link 過期
    SERIAL_NUMBER_MISSING = 9208  # 找不到單號
    TICKET_AMOUNT_NOT_MATCH = 9209  # 回調金額與單子不匹配

    # ===== payment ===== #
    CHANNEL_NOT_EXIST = 9400  # 支付渠道不存在
    CHANNEL_ALREADY_EXIST = 9401  # 支付渠道已存在
    CALLBACK_STATUS_WRONG = 9415  # callback狀態錯誤
    PAYMENT_FEE_SETTING_NOT_FOUND = 9416  # 手續費設定不存在

    # ===== GAME ===== #
    UNDER_MAINTENANCE = 9601  # 維護中
    REFRESH_REQUIRED = 9602  # 請求重整
    VERSION_OUT_OF_DATE = 9603  # 版本過時

    @classmethod
    def _get_key(cls, error_code):
        for key, value in cls.__dict__.items():
            if key.startswith('_'):
                continue
            if value == error_code:
                return key
        return None

    @classmethod
    def _get_msg(cls, error_code):
        for key, value in cls.__dict__.items():
            if key.startswith('_'):
                continue
            if value == error_code:
                return key.replace('_', ' ').title()
        return None

    @classmethod
    def get_error_schema(cls, message, error_code):
        error_schema = {
            'message': message,
            'error_code': error_code,
            'error_key': cls._get_key(error_code),
            'error_msg': cls._get_msg(error_code),
        }
        return error_schema

    @classmethod
    def to_dict(cls):
        result = dict()
        for k, v in cls.__dict__.items():
            if k.startswith('_') or type(v) in {classmethod, staticmethod}:
                continue
            tmp = {v: k.replace('_', ' ').title()}
            result.update(tmp)
        return result


class _BaseError(Exception):
    """
        錯誤基底
    """

    def __init__(self, error_code=None, message=None, code=404, debug_message=None):
        super(_BaseError, self).__init__()
        self.error_code = error_code or ErrorCode.BASE_ERROR
        self.message = message
        self.code = code
        self.debug_message = debug_message
        self.error_schema = ErrorCode.get_error_schema(
            message=self.message,
            error_code=self.error_code
        )

    def __str__(self):
        return self.__class__.__name__


class ValidationError(_BaseError):
    """
    - 操作錯誤
    - 驗證錯誤
    - 檢查錯誤
    """

    def __init__(self, error_code=None, message=None, debug_message=None):
        super(ValidationError, self).__init__(
            code=400,
            message=message,
            error_code=error_code,
            debug_message=debug_message
        )


class NotAuthorizedError(_BaseError):
    """
    - 授權錯誤
    """

    def __init__(self, error_code=None, message=None, debug_message=None):
        super(NotAuthorizedError, self).__init__(
            code=401,
            message=message,
            error_code=error_code,
            debug_message=debug_message
        )


class ForbiddenError(_BaseError):
    """
    - 禁用錯誤
    """

    def __init__(self, error_code=None, message=None, debug_message=None):
        super(ForbiddenError, self).__init__(
            code=403,
            message=message,
            error_code=error_code,
            debug_message=debug_message
        )


class NotFoundError(_BaseError):
    """
    - 資料錯誤
    """

    def __init__(self, error_code=None, message=None, debug_message=None):
        super(NotFoundError, self).__init__(
            code=204,
            message=message,
            error_code=error_code,
            debug_message=debug_message
        )


class ImageError(_BaseError):
    """
    - 圖片錯誤
    """

    def __init__(self, error_code=None, message=None, debug_message=None):
        super(ImageError, self).__init__(
            code=405,
            message=message,
            error_code=error_code,
            debug_message=debug_message
        )


class TransactionError(_BaseError):
    """
    - 交易錯誤
    """

    def __init__(self, error_code=None, message=None, debug_message=None):
        super(TransactionError, self).__init__(
            code=400,
            message=message,
            error_code=error_code,
            debug_message=debug_message
        )
