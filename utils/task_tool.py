from common.const import Const
from common.error_handler import ErrorCode, ValidationError
from common.models import TaskOrder, db
from common.utils.order_tool import OrderTool
from common.utils.orm_tool import ORMTool
from common.utils.transaction_tool import TransactionTool


class TaskTool:

    # COIN AMOUNT
    _CASH_REWARD = 100

    # Ticket AMOUNT
    _REGISTER = 10

    @classmethod
    def _issue_ticket_reward(cls, user, type_, amount):
        """
            REGISTER
        """
        ORMTool.flush()
        task_order = TaskOrder.query.filter(
            TaskOrder.member_id == user.id,
            TaskOrder.type == type_,
        ).first()

        # 產生訂單
        if task_order:
            if task_order.prize:
                return
            order = task_order
        else:
            order = OrderTool.create_task_order(member_id=user.id, type_=type_)
        ORMTool.flush()

        user.ticket.amount['game'] += amount
        flag_modified(user.ticket, 'amount')
        ORMTool.flush()

        # 獎勵交易單
        transaction = TransactionTool.get_member_trans(
            trans_type=Const.Transaction.Type.TASK_PRIZE,
            member_id=user.id,
            order_id=order.id,
            ticket=amount,
        )
        db.session.add(transaction)

    @classmethod
    def issue_task_reward(cls, user, type_):
        if type_ not in Const.Task.Type.to_dict(reverse=True):
            raise ValidationError(error_code=ErrorCode.INVALID_OPERATION,
                                  message='Invalid task type')

        if type_ == Const.Task.Type.REGISTER:
            cls._issue_ticket_reward(user=user,
                                     type_=type_,
                                     amount=cls._REGISTER)
        elif type_ == Const.Task.Type.GAME:
            cls._issue_cash_reward(user=user,
                                   type_=type_,
                                   amount=cls._CASH_REWARD)
