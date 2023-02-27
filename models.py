from sqlalchemy import func, text
from sqlalchemy.schema import UniqueConstraint

from app import db, config

BIND_KEY = config['DB_NAME']

"""
- 使用者
    Admin
    Member

- 操作記錄
    AdminOperation
    MemberOperation

- 賽池
    Category
    Criterion
    Contest
    Order
    Lineup

- 交易記錄
    MemberDepositTransaction
    MemberFeeTransaction
    MemberPrizeTransaction

    TransactionLog
"""


class Admin(db.Model):
    """
        後台使用者
        - 擁有者 11
        - 維護人員: 12

        - 娛樂城管理員: 13
    """
    __bind_key__ = BIND_KEY
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='登入帳號')
    nickname = db.Column(db.String(30), nullable=False, index=True, comment='用戶暱稱')
    password = db.Column(db.String(100), nullable=False, comment='登入密碼')
    role = db.Column(db.Integer, nullable=False, comment='角色類型')
    phone = db.Column(db.String(30), comment='電話')
    email = db.Column(db.String(100), comment='信箱')
    remark = db.Column(db.String(100), comment='備註')
    secret_key = db.Column(db.String(30), unique=True, comment='SDK金鑰', doc='系統產生，用於識別玩家歸屬')
    is_active = db.Column(db.Boolean, nullable=False, server_default=text('1'), comment='是否可用', doc='控制器')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())  # 更新時間
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())  # 建立時間

    members = db.relationship('Member', backref='admin', lazy='dynamic')
    system_logs = db.relationship('SystemSettingLog', backref='admin', lazy='dynamic')


class AdminOperation(db.Model):
    """ 操作記錄 管理員 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'admin_operation'
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, comment='管理員')
    method = db.Column(db.Integer, nullable=False, comment='操作類型')
    route = db.Column(db.String(100), nullable=False, comment='使用路由')
    payload = db.Column(db.JSON, comment='使用資料')
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())  # 建立時間

    operator = db.relationship('Admin', foreign_keys=[operator_id], lazy='joined')


class Member(db.Model):
    """
        用戶
        - 登入玩家: 21
    """
    __bind_key__ = BIND_KEY
    __tablename__ = 'member'
    __table_args__ = (
        db.UniqueConstraint( 'agent', 'username', name='unique_username'),
    )
    id = db.Column(db.Integer, primary_key=True)
    agent = db.Column(db.String(30), index=True, comment='代理')
    username = db.Column(db.String(30), nullable=False, index=True, comment='登入帳號')
    nickname = db.Column(db.String(30), nullable=False, index=True, comment='用戶暱稱')
    password = db.Column(db.String(100), nullable=False, comment='登入密碼')
    role = db.Column(db.Integer, nullable=False, comment='角色類型')
    avatar = db.Column(db.Integer, nullable=False, server_default=text('1'), comment='頭像類型')
    remark = db.Column(db.String(100), comment='備註')
    is_active = db.Column(db.Boolean, nullable=False, server_default=text('1'), comment='是否可用', doc='控制器')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())  # 更新時間
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())  # 建立時間

    wallet = db.relationship('Wallet', backref='member', uselist=False, lazy='select')  # 唯一

    orders = db.relationship('Order', backref='member', lazy='dynamic')
    deposits = db.relationship('MemberDepositTransaction', backref='member', lazy='dynamic')
    fees = db.relationship('MemberFeeTransaction', backref='member', lazy='dynamic')
    prizes = db.relationship('MemberPrizeTransaction', backref='member', lazy='dynamic')
    balance_logs = db.relationship('TransactionLog', backref='member', lazy='dynamic')


class MemberOperation(db.Model):
    """ 操作記錄 用戶 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'member_operation'
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, comment='用戶')
    method = db.Column(db.Integer, nullable=False, comment='操作類型')
    route = db.Column(db.String(100), nullable=False, comment='使用路由')
    payload = db.Column(db.JSON, comment='使用資料')
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())  # 建立時間

    operator = db.relationship('Member', foreign_keys=[operator_id], lazy='joined')


class Wallet(db.Model):
    """ 用戶 結餘 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, unique=True, index=True, comment='用戶')

    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金')
    ticket = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='金券')

    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())  # 更新時間
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())  # 建立時間


class Contest(db.Model):
    __bind_key__ = BIND_KEY
    __tablename__ = 'contest'
    id = db.Column(db.Integer, primary_key=True)
    is_archive = db.Column(db.Boolean, nullable=False, server_default=text('0'), comment='是否封存')
    status = db.Column(db.Integer, nullable=False, server_default=text('1'), comment='CREATED:1/ACTIVATED:2/CANCELED:3')

    open_datetime = db.Column(db.DateTime, comment='開賽時間')
    settle_datetime = db.Column(db.DateTime, comment='結算時間')
    delete_datetime = db.Column(db.DateTime, comment='刪除時間')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())

    orders = db.relationship('Order', backref='contest', lazy='dynamic')


class Order(db.Model):
    __bind_key__ = BIND_KEY
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), nullable=False, comment='賽池')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), index=True, comment='用戶')
    lineup_id = db.Column(db.Integer, db.ForeignKey('lineup.id'), comment='陣容id')
    status = db.Column(db.Integer, nullable=False, comment='訂單狀態', doc='11:空白注單/1:成功/2:結算/3:取消')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())

    fee = db.relationship('MemberFeeTransaction', backref='order', uselist=False, lazy='select')  # 唯一
    prize = db.relationship('MemberPrizeTransaction', backref='order', uselist=False, lazy='select')  # 唯一


class MemberDepositTransaction(db.Model):
    """ 用戶 上分 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'member_deposit_transaction'
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='交易單號')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='用戶')

    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金')
    ticket = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='金票')

    remark = db.Column(db.String(100), comment='備註')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())


class MemberFeeTransaction(db.Model):
    """ 用戶 費用 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'member_fee_transaction'
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='交易單號')
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True, comment='參賽訂單')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='用戶')

    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金')
    ticket = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='金票')

    remark = db.Column(db.String(100), comment='備註')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())


class MemberPrizeTransaction(db.Model):
    """ 用戶 獎金 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'member_prize_transaction'
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='交易單號')
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True, comment='參賽訂單')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='用戶')

    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金')
    ticket = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='金票')

    remark = db.Column(db.String(100), comment='備註')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())


class TransactionLog(db.Model):
    """ SQL Trigger 交易紀錄 """
    __bind_key__ = BIND_KEY
    __tablename__ = 'transaction_log'
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.String(30), nullable=False, index=True, comment='交易單號')
    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金')
    ticket = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='金票')

    cash_balance = db.Column(db.Integer, comment='cash更新後餘額')
    ticket_balance = db.Column(db.Integer, comment='ticket更新後餘額')

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), index=True, comment='用戶')
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), index=True, comment='賽池')
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now())


""" System Setting """


class SystemSetting(db.Model):
    __bind_key__ = BIND_KEY
    __tablename__ = 'system_setting'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, unique=True)
    value = db.Column(db.String(200), nullable=False)
    remark = db.Column(db.String(100), comment='備註')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='建立時間')


class SystemSettingLog(db.Model):
    __bind_key__ = BIND_KEY
    __tablename__ = 'system_setting_log'
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, comment='操作者')
    type = db.Column(db.Integer, nullable=False)
    value = db.Column(db.String(200), nullable=False)
    remark = db.Column(db.String(100), comment='備註')
    update_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    create_datetime = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='建立時間')
