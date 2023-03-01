from common.const import Const
from common.models import Order, RewardOrder, TaskOrder, db
from common.utils.encrypt_tool import KeyGenerator


class OrderTool:
    _ATTEMPT_LIMIT = 100

    @classmethod
    def _generate_order_no(cls):
        for _ in range(cls._ATTEMPT_LIMIT):
            order_no = KeyGenerator.get_random_code(number=7,
                                                    has_digit=True,
                                                    has_upper=True)
            if Order.query.filter_by(id=order_no).first():
                continue
            return order_no
        raise Exception(
            f'Reached Generate Order No Attempt Limit: {cls._ATTEMPT_LIMIT}')

    @classmethod
    def _create_system_order(cls, _type, member_id):
        no = cls._generate_order_no()
        data = {
            'id': no,
            'type': _type,
            'member_id': member_id,
        }
        system_order = Order(**data)
        db.session.add(system_order)
        db.session.flush()
        return system_order

    @classmethod
    def create_task_order(cls, member_id, type_):
        system_order = cls._create_system_order(_type=Const.Order.Type.TASK,
                                                member_id=member_id)
        data = {
            'no': system_order.id,
            'member_id': member_id,
            'type': type_,
        }
        order = TaskOrder(**data)
        db.session.add(order)
        return order

    @classmethod
    def create_reward_order(cls, member_id, reward_setting_id, condition=None):
        system_order = cls._create_system_order(_type=Const.Order.Type.REWARD,
                                                member_id=member_id)
        data = {
            'no': system_order.id,
            'member_id': member_id,
            'reward_setting_id': reward_setting_id,
            'condition': condition,
        }
        order = RewardOrder(**data)
        db.session.add(order)
        return order
