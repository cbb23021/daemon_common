from flask import jsonify
from common.error_handler import ValidationError, ErrorCode


class ResponseHandler:

    @staticmethod
    def _validate_results(results):
        if results is False:
            raise ValidationError(error_code=ErrorCode.INVALID_OPERATION)
        if results is None:
            raise ValidationError(error_code=ErrorCode.DATA_MISSING)
        if not (isinstance(results, dict) or isinstance(results, list)):
            raise ValidationError(error_code=ErrorCode.DATA_ERROR)

    @staticmethod
    def _validate_pager(pager):
        if not (pager is None or isinstance(pager, dict)):
            raise ValidationError(error_code=ErrorCode.DATA_ERROR)

    @classmethod
    def jsonify(cls, results, pager=None, code=200):
        if results is True:
            return jsonify({'succeed': True}), code
        cls._validate_results(results=results)
        cls._validate_pager(pager=pager)
        data = {
            'pager': pager,
            'data': results,
        }
        return jsonify(data), code
