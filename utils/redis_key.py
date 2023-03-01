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

    # others
    @staticmethod
    def transaction(trans_no):
        return f'transaction:{trans_no}'

    @staticmethod
    def get_fantasyee_member_playing_experience_key(username):
        return f'playing_experience:{username}'

    @staticmethod
    def get_room_message_key(room_id):
        return f'room_message:{room_id}'

    @staticmethod
    def get_room_unread_amount_key(room_name):
        return f'unread:{room_name}'

    @staticmethod
    def get_expired_room_key():
        return 'expired:room'

    @staticmethod
    def get_member_auth_lock_key(phone):
        return f'member:{phone}:auth_lock'

    # """ PHONE """

    # @staticmethod
    # def get_phone_otp_key(phone):
    #     return f'phone:{phone}:otp'

    # @staticmethod
    # def get_phone_otp_request_attempt_key(phone):
    #     return f'phone:{phone}:otp:request-attempt'

    # @staticmethod
    # def get_verified_phone_key(phone):
    #     return f'verified:phone:{phone}'

    """ [PHONE] RESET PASSWORD """

    @staticmethod
    def get_verified_reset_password_phone_code_key(phone):
        return f'verified_reset_password_phone:{phone}'

    @staticmethod
    def get_reset_password_attempt_key(phone):
        return f'reset_password:attempt:{phone}'

    """ [LOCK] API REQUEST """

    @staticmethod
    def request_lock(role, user_id, request_method, request_path, request_args,
                     request_payload):
        key = (
            f'role:{role}:user:{user_id}:'
            f'request:{request_method}:{request_path}:{request_args}:{request_payload}:'
            f'lock')
        return key

    @staticmethod
    def transfer_lock(user_id):
        return f'user:{user_id}:transfer-lock'

    @staticmethod
    def return_lock(user_id):
        return f'user:{user_id}:return-lock'

    """ LOGIN RECORD """

    @staticmethod
    def get_member_login_record_key(date_):
        return f'member_login_record:date:{date_}'

    """ SMS CALLBACK STATUS """

    @staticmethod
    def get_twofactor_callback_sms_status_key(phone):
        return f'callback:twofactor:phone:{phone}:status'

    # ------------------------- [ Lock ] -------------------------- #

    @staticmethod
    def get_game_playing_lock_key(user_id):
        return f'game:playing:user:{user_id}:lock'

    # ------------------------- [ Exp ] -------------------------- #
    @staticmethod
    def month_member_exp(year_month, member_id):
        return f'year_month:{year_month}:member:{member_id}:exp'

    # ------------------------- [ Vip Upgrade Notification ] -------------------------- #
    @staticmethod
    def member_upgrade(member_id):
        return f'member:{member_id}:upgrade'

    # ------------------------- [ Reward Prize ] -------------------------- #
    @staticmethod
    def reward_prize_total(setting_id):
        return f'reward-prize-total:{setting_id}'

    # ------------------------- [ User List ] ------------------------------ #
    @staticmethod
    def export_user_list(role, keyword, sort_by, is_desc):
        return f'user_list:role:{role}:keyword:{keyword}:sort_by:{sort_by}:is_desc:{is_desc}'
