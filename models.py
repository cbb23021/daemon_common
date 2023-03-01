from sqlalchemy import text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from app import db
from common.models_template import ModelsTemplate

""" ADMIN 相關資料 """


class Admin(db.Model, ModelsTemplate):
    __tablename__ = 'admin'
    username = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='登入帳號')
    password = db.Column(db.String(100), nullable=False, comment='登入密碼')
    role = db.Column(db.Integer, nullable=False, comment='角色類型OWNER:11/MAINTAINER:12/OPERATOR:13/REPORTER:14/MARKETER:15')
    remark = db.Column(db.String(100), comment='備註')
    is_block = db.Column(db.Boolean, nullable=False, server_default=text('0'), comment='黑名單')
    latest_login_info = db.Column(db.JSON, nullable=False, comment='上次登入資訊')

    operations = db.relationship('AdminOperation', backref='admin', lazy='dynamic')


class AdminOperation(db.Model, ModelsTemplate):
    """ 操作記錄 管理員 """
    __tablename__ = 'admin_operation'
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, comment='管理員')
    method = db.Column(db.Integer, nullable=False, comment='操作類型')
    route = db.Column(db.String(100), nullable=False, comment='使用路由')
    args = db.Column(db.Text, comment='使用參數')
    payload = db.Column(db.Text, comment='使用資料')
    address = db.Column(db.String(30), comment='授權地址')
    platform = db.Column(db.String(30), comment='系統')
    browser = db.Column(db.String(30), comment='瀏覽器')
    language = db.Column(db.String(30), comment='語言')
    user_agent = db.Column(db.String(300), comment='使用者代理')


class Member(db.Model, ModelsTemplate):
    __tablename__ = 'member'
    username = db.Column(db.String(100), unique=True, index=True, comment='使用者帳號')
    nickname = db.Column(db.String(100), nullable=False, comment='用戶暱稱')
    phone = db.Column(db.String(30), unique=True, comment='電話')
    email = db.Column(db.String(100), unique=True, index=True, comment='登入帳號/信箱')
    role = db.Column(db.Integer, nullable=False, comment='角色類型', doc='member:21')
    latest_login_info = db.Column(db.JSON, nullable=False, comment='上次登入資訊')
    remark = db.Column(db.String(100), comment='備註')
    is_block = db.Column(db.Boolean, nullable=False, server_default=text('0'), comment='黑名單')
    password = db.Column(db.String(100), nullable=False, comment='登入密碼')

    cash = db.relationship('Cash', backref='member', uselist=False, lazy='select')
    ticket = db.relationship('Ticket', backref='member', uselist=False, lazy='select')

    operations = db.relationship('MemberOperation', backref='member', lazy='dynamic')


class MemberOperation(db.Model, ModelsTemplate):
    """ 操作記錄 用戶 """
    __tablename__ = 'member_operation'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, comment='用戶')
    method = db.Column(db.Integer, nullable=False, comment='操作類型')
    route = db.Column(db.String(100), nullable=False, comment='使用路由')
    args = db.Column(db.Text, comment='使用參數')
    payload = db.Column(db.Text, comment='使用資料')
    address = db.Column(db.String(30), comment='授權地址')
    platform = db.Column(db.String(30), comment='系統')
    browser = db.Column(db.String(30), comment='瀏覽器')
    language = db.Column(db.String(30), comment='語言')
    user_agent = db.Column(db.String(300), comment='使用者代理')


class Cash(db.Model, ModelsTemplate):
    """ 儲值金 """
    __tablename__ = 'cash'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, unique=True, index=True, comment='會員')
    amount = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='可用額度')
    freeze = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='不可操作')
    is_locked = db.Column(db.Boolean, nullable=False, server_default=text('0'), comment='是否上鎖')


class Ticket(db.Model, ModelsTemplate):
    """ 票夾 """
    __tablename__ = 'ticket'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, unique=True, index=True, comment='會員')
    amount = db.Column(db.JSON, nullable=False, comment='票券數量')  # {"daily_bonus": 1, ...}


""" 系統 相關資料 """

""" block setting """


class Whitelist(db.Model, ModelsTemplate):
    __tablename__ = 'whitelist'
    address = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='ip地址')
    remark = db.Column(db.String(30), index=True, comment='備註')


class Blacklist(db.Model, ModelsTemplate):
    __tablename__ = 'blacklist'
    address = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='ip地址')
    remark = db.Column(db.String(30), index=True, comment='備註')


""" Rewards """


class RewardSetting(db.Model, ModelsTemplate):
    """ Reward 設定 """
    __tablename__ = 'reward_setting'
    category = db.Column(db.Integer, nullable=False, comment='1:遊戲/')
    name = db.Column(db.String(100), nullable=False, comment='活動名稱')
    start_datetime = db.Column(db.DateTime, nullable=False, comment='生效開始時間')
    end_datetime = db.Column(db.DateTime, comment='生效結束時間')
    type = db.Column(db.Integer, comment='1:cash/2:ticket')
    fixed_amount = db.Column(db.Integer, comment='固定獎金/金額')
    min_amount = db.Column(db.Integer, comment='隨機獎金/最低金額')
    max_amount = db.Column(db.Integer, comment='隨機獎金/最高金額')
    amount_limit = db.Column(db.Integer, comment='頒發總獎金上限')
    detail = db.Column(MEDIUMTEXT, comment='細節說明')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, comment='管理員')
    delete_datetime = db.Column(db.DateTime, comment='刪除時間')


""" 訂單 相關資料 """

""" System Order """


class Order(db.Model, ModelsTemplate):
    """ Order 總表 """
    __tablename__ = 'order'
    id = db.Column(db.String(30), primary_key=True, autoincrement=False, comment='項目order no')
    type = db.Column(db.Integer, nullable=False, comment='Const.Order.Type')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='會員')


""" Task """


class TaskOrder(db.Model, ModelsTemplate):
    """ 任務 訂單 """
    __tablename__ = 'task_order'
    no = db.Column(db.String(30), db.ForeignKey('order.id'), nullable=False, unique=True, index=True, comment='系統order單號')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='會員')
    type = db.Column(db.Integer, nullable=False, comment='Const.Task.Type')
    remark = db.Column(db.String(100), comment='備註')
    delete_datetime = db.Column(db.DateTime, comment='刪除時間')

    prize = db.relationship('TaskPrizeTransaction', backref='task_order', uselist=False, lazy='select')


""" Reward """


class RewardOrder(db.Model, ModelsTemplate):
    """ 模組獎勵 訂單 """
    __tablename__ = 'reward_order'
    no = db.Column(db.String(30), db.ForeignKey('order.id'), nullable=False, unique=True, index=True, comment='系統order單號')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='會員')
    reward_setting_id = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.Integer)
    remark = db.Column(db.String(100), comment='備註')
    delete_datetime = db.Column(db.DateTime, comment='刪除時間')

    prize = db.relationship('RewardPrizeTransaction', backref='reward_order', uselist=False, lazy='select')


""" 交易 相關資料 """

""" Transaction log """


class TransactionLog(db.Model, ModelsTemplate):
    """ Sql trigger 交易紀錄 """
    __tablename__ = 'transaction_log'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), index=True, comment='會員')
    no = db.Column(db.String(30), nullable=False, index=True, comment='交易單號')
    cash = db.Column(db.Integer, comment='儲值金額度')
    ticket = db.Column(db.JSON, comment='票券')
    cash_balance = db.Column(db.Integer, nullable=False, comment='cash更新後餘額')
    ticket_balance = db.Column(db.JSON, nullable=False, comment='ticket更新後餘額')


""" Task """


class TaskPrizeTransaction(db.Model, ModelsTemplate):
    """ 任務 派獎單 """
    __tablename__ = 'task_prize_transaction'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='會員')
    order_id = db.Column(db.Integer, db.ForeignKey('task_order.id'), nullable=False, index=True, comment='訂單號')
    no = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='交易單號')
    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金額度')
    winnings = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='彩金額度')
    coin = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='平台幣額度')
    ticket = db.Column(db.JSON, comment='票券')
    exp = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='經驗值')
    remark = db.Column(db.String(100), comment='備註')
    delete_datetime = db.Column(db.DateTime, comment='刪除時間')


class RewardPrizeTransaction(db.Model, ModelsTemplate):
    """ 模組獎勵 派獎單 """
    __tablename__ = 'reward_prize_transaction'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False, index=True, comment='會員')
    order_id = db.Column(db.Integer, db.ForeignKey('reward_order.id'), nullable=False, index=True, comment='訂單號')
    no = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='交易單號')
    cash = db.Column(db.Integer, nullable=False, server_default=text('0'), comment='儲值金額度')
    ticket = db.Column(db.JSON, comment='票券')
    remark = db.Column(db.String(100), comment='備註')
    delete_datetime = db.Column(db.DateTime, comment='刪除時間')
