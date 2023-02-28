"""
- 自訂&改寫 flask API 錯誤模板(回傳自訂錯誤代碼, 格式化為JSON 結構)
- 透過 DebugTool 將錯誤寫入日誌
"""
from app import app
from flask import jsonify
from schema import SchemaError, SchemaUnexpectedTypeError, SchemaMissingKeyError
from werkzeug.exceptions import (
    HTTPException,
    NotFound,
    RequestEntityTooLarge,
    ServiceUnavailable,
    MethodNotAllowed,
)
from common.error_handler import (
    ErrorCode,
    ValidationError,
    NotAuthorizedError,
    ForbiddenError,
    NotFoundError,
    ImageError,
)
from common.utils.debugtool import DebugTool

""" 自訂 Exceptions """


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    DebugTool.error(e)
    return jsonify(e.error_schema), e.code


@app.errorhandler(NotAuthorizedError)
def handle_not_auth_error(e):
    DebugTool.error(e)
    return jsonify(e.error_schema), e.code


@app.errorhandler(NotFoundError)
def handle_not_found_error(e):
    DebugTool.error(e)
    return jsonify(e.error_schema), e.code


@app.errorhandler(ImageError)
def handle_image_error(e):
    DebugTool.error(e)
    return jsonify(e.error_schema), e.code


@app.errorhandler(ForbiddenError)
def handle_forbidden_error(e):
    DebugTool.error(e)
    return jsonify(e.error_schema), e.code


""" Flask Exceptions """


@app.errorhandler(NotFound)
def handle_404_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Endpoint Not Found',
        error_code=ErrorCode.INVALID_OPERATION,
    )
    return jsonify(error_schema), 404


@app.errorhandler(MethodNotAllowed)
def handle_405_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Method Not Allowed',
        error_code=ErrorCode.INVALID_OPERATION,
    )
    return jsonify(error_schema), 405


@app.errorhandler(SchemaMissingKeyError)
def handle_406_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Payload Missing Key',
        error_code=ErrorCode.PAYLOAD_MISSING_KEY,
    )
    return jsonify(error_schema), 406


@app.errorhandler(SchemaUnexpectedTypeError)
def handle_407_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Payload Unexpected Type Error',
        error_code=ErrorCode.PAYLOAD_UNEXPECTED_TYPE,
    )
    return jsonify(error_schema), 407


@app.errorhandler(SchemaError)
def handle_408_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Payload Error',
        error_code=ErrorCode.PAYLOAD_ERROR,
    )
    return jsonify(error_schema), 408


@app.errorhandler(RequestEntityTooLarge)
def handle_413_error(e):
    DebugTool.warning(e)
    error_schema = ErrorCode.get_error_schema(
        message='File Too Large',
        error_code=ErrorCode.INVALID_FILE_SIZE,
    )
    return jsonify(error_schema), 413


@app.errorhandler(HTTPException)
def handle_http_error(e):
    DebugTool.error(e)
    message = getattr(e, 'description', 'Bad Request')
    http_code = getattr(e, 'code', 400)
    error_schema = ErrorCode.get_error_schema(
        message=message,
        error_code=ErrorCode.INVALID_OPERATION,
    )
    return jsonify(error_schema), http_code


@app.errorhandler(ServiceUnavailable)
def handle_503_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Service Unavailable',
        error_code=ErrorCode.BASE_ERROR,
    )
    return jsonify(error_schema), 503


@app.errorhandler(Exception)
def handle_500_error(e):
    DebugTool.error(e)
    error_schema = ErrorCode.get_error_schema(
        message='Internal Server Error',
        error_code=ErrorCode.BASE_ERROR,
    )
    return jsonify(error_schema), 500
