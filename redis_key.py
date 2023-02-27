class RedisKey:

    @staticmethod
    def member_login(member_id):
        return f'{member_id}:player_login'

    @staticmethod
    def transaction(trans_no):
        return f'transaction:{trans_no}'

    # ------------------- [LOCK] ------------------- #

    @staticmethod
    def sdk_deposit_lock(member_id):
        return f'{member_id}:sdk_deposit_lock'

    @staticmethod
    def request_lock(role, user_id, request_method, request_path, request_args,
                     request_payload):
        key = (
            f'role:{role}:user:{user_id}:'
            f'request:{request_method}:{request_path}:{request_args}:{request_payload}:'
            f'lock')
        return key

    # ------------------- [Order] ------------------- #

    @staticmethod
    def wait_order_ids(contest_id):
        return f'{contest_id}-WAIT'

    @staticmethod
    def used_order_data(contest_id):
        return f'{contest_id}-USED'

    # ------------------- [Daemon] ------------------- #
    @staticmethod
    def active_contest_ids():
        return f'active_contest_ids'

    @staticmethod
    def cancel_contest_ids():
        return f'cancel_contest_ids'
