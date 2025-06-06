from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField, TextAreaField # 필요한 모든 필드 타입을 한 번에 import
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from .models import User
from datetime import datetime, date # datetime 과 date 를 함께 import

class RegistrationForm(FlaskForm):
    # ... (RegistrationForm 내용은 그대로) ...
    nickname = StringField('닉네임',
                           validators=[DataRequired(message="닉네임을 입력해주세요."),
                                       Length(min=2, max=20, message="닉네임은 2자 이상 20자 이하로 입력해주세요.")])
    email = StringField('이메일',
                        validators=[DataRequired(message="이메일을 입력해주세요."),
                                    Email(message="올바른 이메일 형식이 아닙니다.")])
    password = PasswordField('비밀번호',
                             validators=[DataRequired(message="비밀번호를 입력해주세요."),
                                         Length(min=6, message="비밀번호는 최소 6자 이상이어야 합니다.")])
    confirm_password = PasswordField('비밀번호 확인',
                                     validators=[DataRequired(message="비밀번호 확인을 입력해주세요."),
                                                 EqualTo('password', message="비밀번호가 일치하지 않습니다.")])
    submit = SubmitField('가입하기')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user:
            raise ValidationError('이미 사용 중인 닉네임입니다. 다른 닉네임을 입력해주세요.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 가입된 이메일입니다. 다른 이메일을 입력해주세요.')

class LoginForm(FlaskForm):
    # ... (LoginForm 내용은 그대로) ...
    email = StringField('이메일',
                        validators=[DataRequired(message="이메일을 입력해주세요."),
                                    Email(message="올바른 이메일 형식이 아닙니다.")])
    password = PasswordField('비밀번호',
                             validators=[DataRequired(message="비밀번호를 입력해주세요.")])
    submit = SubmitField('로그인')

class AllowanceForm(FlaskForm): # <--- AllowanceForm 클래스 정의 시작
    # ... (AllowanceForm 내용은 그대로) ...
    amount = FloatField('월별 용돈 금액',
                        validators=[DataRequired(message="용돈 금액을 입력해주세요."),
                                    NumberRange(min=0, message="용돈 금액은 0 이상이어야 합니다.")])

    month_choices = []
    try:
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month
        for i in range(12):
            month_to_add = current_month + i
            year_to_add = current_year + (month_to_add - 1) // 12
            month_in_year = (month_to_add - 1) % 12 + 1
            month_str = f"{year_to_add}-{month_in_year:02d}"
            month_choices.append((month_str, month_str))
    except Exception as e:
        print(f"Error generating month_choices: {e}")
        month_choices = [('default', '월 선택 불가')]

    set_month = SelectField('용돈 적용 월',
                            choices=month_choices,
                            validators=[DataRequired(message="적용 월을 선택해주세요.")])
    submit = SubmitField('저장하기')
# AllowanceForm 클래스 정의 끝

# SpendingForm 클래스 정의 시작 (AllowanceForm 클래스와 같은 들여쓰기 레벨로!)
class SpendingForm(FlaskForm): # <--- 이 클래스가 AllowanceForm 바깥으로 나와야 합니다!
    date = DateField('지출 날짜',
                    default=date.today,
                    validators=[DataRequired(message="지출 날짜를 입력해주세요.")])
    category = StringField('지출 항목 (예: 식비, 교통비)',
                           validators=[DataRequired(message="지출 항목을 입력해주세요."),
                                       Length(max=100, message="지출 항목은 최대 100자까지 입력 가능합니다.")])
    amount = FloatField('지출 금액',
                        validators=[DataRequired(message="지출 금액을 입력해주세요."),
                                    NumberRange(min=0.01, message="지출 금액은 0보다 커야 합니다.")])
    description = TextAreaField('설명 (선택 사항)',
                                validators=[Length(max=200, message="설명은 최대 200자까지 입력 가능합니다.")])
    submit = SubmitField('저장하기')
    
class NoSpendingDayForm(FlaskForm):
    # 무지출일로 설정할 날짜 입력칸 (기본값은 오늘 날짜)
    date = DateField('무지출일로 설정할 날짜',
                    default=date.today, # 기본값을 오늘 날짜로 설정
                    validators=[DataRequired(message="날짜를 선택해주세요.")])

    # "설정하기" 또는 "해제하기" 버튼 (이 버튼은 라우트에서 동적으로 텍스트를 바꿀 수도 있습니다)
    # 여기서는 일단 하나의 "저장/변경" 버튼으로 만듭니다.
    submit = SubmitField('이 날짜로 설정/해제')