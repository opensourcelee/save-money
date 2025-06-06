from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date # date도 import 되어 있는지 확인

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(80), unique=True, nullable=False)

    allowances = db.relationship('Allowance', backref='user', lazy=True)
    spending_records = db.relationship('SpendingRecord', backref='spender', lazy=True)
    # User와 NoSpendingDay 간의 관계 설정 (이 부분이 추가되어야 합니다!)
    no_spending_days = db.relationship('NoSpendingDay', backref='tracker', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

class Allowance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    set_month = db.Column(db.String(7), nullable=False) # 예: "2024-07"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Allowance UserID:{self.user_id} - Month:{self.set_month} Amount:{self.amount}>"

class SpendingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today) # default는 폼에서 처리하는 것이 더 일반적
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<SpendingRecord ID:{self.id} UserID:{self.user_id} Date:{self.date} Category:{self.category} Amount:{self.amount}>"

# NoSpendingDay 모델 (이 클래스 전체가 추가되어야 합니다!)
class NoSpendingDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 특정 사용자의 특정 날짜는 유니크해야 함
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='_user_date_uc'),)

    def __repr__(self):
        return f"<NoSpendingDay UserID:{self.user_id} Date:{self.date}>"