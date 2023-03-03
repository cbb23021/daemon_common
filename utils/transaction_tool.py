from datetime import datetime

from common.const import Const
from common.models import (
    TaskPrizeTransaction,
    RewardPrizeTransaction,
    LottoFeeTransaction,
)
from common.utils.encrypt_tool import KeyGenerator


class TransactionTool:
    _ATTEMPT_LIMIT = 100
    _TRANSACTION_MODEL = {
        Const.Transaction.Type.TASK_PRIZE: TaskPrizeTransaction,
        Const.Transaction.Type.REWARD_PRIZE: RewardPrizeTransaction,
        Const.Transaction.Type.LOTTO_FEE: LottoFeeTransaction,
    }

    @classmethod
    def _get_trans_model(cls, trans_type):
        model = cls._TRANSACTION_MODEL.get(trans_type)
        if model:
            return model
        raise Exception('Transaction Type Not Found')

    @classmethod
    def _generate_no(cls, trans_type):
        today = datetime.now().strftime('%Y%m%d')
        for _ in range(cls._ATTEMPT_LIMIT):
            code = KeyGenerator.get_random_code(number=10, has_digit=True, has_upper=True)
            trans_no = f'{trans_type}{today}{code}'
            trans_model = cls._get_trans_model(trans_type=trans_type)
            if trans_model.query.filter_by(no=trans_no).first():
                continue
            return trans_no
        raise Exception(f'Reached Generate Transaction No Attempt Limit: {cls._ATTEMPT_LIMIT}')

    @classmethod
    def get_member_trans(cls, trans_type, member_id, order_id, cash=None, ticket=None, remark=None):
        """ 取得 member transaction orm 物件 """
        model = cls._get_trans_model(trans_type=trans_type)
        data = {
            'no': cls._generate_no(trans_type=trans_type),
            'member_id': member_id,
            'order_id': order_id,
        }
        if cash is not None:
            data.update({'cash': cash})
        if ticket is not None:
            data.update({'ticket': ticket})
        if remark is not None:
            data.update({'remark': remark})

        trans_obj = model(**data)
        return trans_obj
