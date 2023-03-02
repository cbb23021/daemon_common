class RedisKey:
    # ------------------------- [ Address Control ] -------------------------- #
    """ Whitelist """

    @staticmethod
    def get_whitelist_key():
        return 'whitelist'

    """ Blacklist """

    @staticmethod
    def get_blacklist_key():
        return 'blacklist'

    # ------------------------- [ Email Verification ] -------------------------- #

    @staticmethod
    def get_verify_email_otp_key(email):
        return f'verify_email:otp:{email}'

    @staticmethod
    def get_verify_email_attempt_key(email):
        return f'verify_email:attempt:{email}'

    @staticmethod
    def get_verified_email_key(email):
        return f'verify_email:verified:{email}'

    # ------------------------- [ auth ] -------------------------- #

    @staticmethod
    def get_member_auth_lock_key(email):
        return f'member:{email}:auth_lock'

    """ [email] RESET PASSWORD """

    @staticmethod
    def get_verified_reset_password_email_code_key(email):
        return f'verified_reset_password_email:{email}'

    @staticmethod
    def get_reset_password_attempt_key(email):
        return f'reset_password:attempt:{email}'

    # others
    @staticmethod
    def transaction(trans_no):
        return f'transaction:{trans_no}'

    """ [LOCK] API REQUEST """

    @staticmethod
    def request_lock(role, user_id, request_method, request_path, request_args,
                     request_payload):
        key = (
            f'role:{role}:user:{user_id}:'
            f'request:{request_method}:{request_path}:{request_args}:{request_payload}:'
            f'lock')
        return key

    """ LOGIN RECORD """

    @staticmethod
    def get_member_login_record_key(date_):
        return f'member_login_record:date:{date_}'

    # ------------------------- [ Lock ] -------------------------- #

    @staticmethod
    def get_game_playing_lock_key(user_id):
        return f'game:playing:user:{user_id}:lock'

    # ------------------------- [ Reward Prize ] -------------------------- #
    @staticmethod
    def reward_prize_total(setting_id):
        return f'reward-prize-total:{setting_id}'

    # ------------------------- [ User List ] ------------------------------ #
    @staticmethod
    def export_user_list(role, keyword, sort_by, is_desc):
        return f'user_list:role:{role}:keyword:{keyword}:sort_by:{sort_by}:is_desc:{is_desc}'
