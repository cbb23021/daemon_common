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
    INVALID_ACCESS_TOKEN = 3003  # 無效通行証
    INVALID_PHONE_NUMBER = 3004  # 無效手機號碼
    INVALID_EMAIL = 3005  # 無效手機號碼
    INVALID_USERNAME = 3006  # 無效手機號碼
    INVALID_PASSWORD = 3007  # 無效密碼
    INVALID_VERIFY_CODE = 3008  # 無效驗證代碼
    INVALID_KEYWORD_LENGTH = 3009  # 無效關鍵字長度
    INVALID_FILE_SIZE = 3010  # 無效檔案大小
    INVALID_IMAGE_FORMAT = 3011  # 無效圖片格式

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
    APP_VERSION_DETAIL_IS_MISSING = 3116  # 表頭未包含版本資訊
    APP_VERSION_IS_OUT_OF_DATE = 3117  # APP版本過時
    APP_VERSION_FORMAT_ERROR = 3118  # 錯誤的APP版本格式

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
    def to_dict(cls):
        result = dict()
        for k, v in cls.__dict__.items():
            if k.startswith('_') or type(v) in {classmethod, staticmethod}:
                continue
            tmp = {v: k.replace('_', ' ').title()}
            result.update(tmp)
        return result

    @classmethod
    def get_error_schema(cls, message, error_code):
        error_schema = {
            'message': message,
            'error_code': error_code,
            'error_key': cls._get_key(error_code),
            'error_msg': cls._get_msg(error_code),
        }
        return error_schema


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
