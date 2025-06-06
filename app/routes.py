from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Allowance, SpendingRecord, NoSpendingDay # 모델들을 가져옵니다. (상대 경로 확인!)
from . import db # db 객체를 가져옵니다. (상대 경로 확인!)
from datetime import datetime, date, timedelta # 날짜/시간 관련 모듈
import calendar # 달력 관련 모듈

# "메인 길 안내 지도 묶음" 만들기
main_routes_for_website = Blueprint('main', __name__)

# 사용자가 웹사이트 기본 주소로 접속했을 때 (홈페이지)
@main_routes_for_website.route('/')
@main_routes_for_website.route('/home')
def hello_world_page():
    return render_template('hello.html', title='Save Money 홈')

# 사용자 대시보드 페이지 라우트
@main_routes_for_website.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    current_month_str = today.strftime("%Y-%m") # "YYYY-MM" 형식

    # 1. 현재 월의 설정된 용돈 가져오기
    allowance_obj = Allowance.query.filter_by(user_id=current_user.id, set_month=current_month_str).first()
    monthly_allowance = allowance_obj.amount if allowance_obj else 0

    # 2. 현재 월의 총 지출액 계산하기
    first_day_of_month = today.replace(day=1)
    # last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    # 위 방법 대신, 다음 달 1일에서 하루를 빼는 방법도 많이 사용합니다.
    if today.month == 12:
        last_day_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)


    total_spending_this_month = db.session.query(db.func.sum(SpendingRecord.amount)).filter(
        SpendingRecord.user_id == current_user.id,
        SpendingRecord.date >= first_day_of_month, # date 객체로 비교
        SpendingRecord.date <= last_day_of_month  # date 객체로 비교
    ).scalar() or 0

    # 3. 현재 월의 남은 일수 계산하기 (오늘 포함)
    remaining_days_this_month = (last_day_of_month - today).days + 1

    # 4. 현재 월의 남은 기간 중 무지출일 수 계산하기 (오늘부터 월말까지)
    future_no_spending_days_count = NoSpendingDay.query.filter(
        NoSpendingDay.user_id == current_user.id,
        NoSpendingDay.date >= today,
        NoSpendingDay.date <= last_day_of_month
    ).count()

    # 5. 실제로 돈을 쓸 수 있는 남은 날짜 수 계산
    spendable_remaining_days = remaining_days_this_month - future_no_spending_days_count
    if spendable_remaining_days < 0: # 오늘이 무지출일이고 남은날이 오늘뿐인 경우 등
        spendable_remaining_days = 0


    # 6. 남은 용돈 계산
    remaining_allowance = monthly_allowance - total_spending_this_month

    # 7. 하루 사용 가능 금액 계산
    daily_spend_recommendation = 0
    if spendable_remaining_days > 0: # 돈 쓸 날이 남아있다면
        daily_spend_recommendation = remaining_allowance / spendable_remaining_days
    elif remaining_allowance > 0 and remaining_days_this_month > 0 : # 돈 쓸 날은 없는데(모두 무지출일), 돈과 날짜는 남았다면
        # 이 경우, 무지출일을 지키지 않으면 남은 돈을 남은 일수로 나눈 금액이 비상금처럼 될 수 있습니다.
        # 또는 "모든 남은 날 무지출 목표!" 같은 메시지를 표시할 수 있습니다.
        # 여기서는 일단 0으로 표시합니다.
        daily_spend_recommendation = 0 # 또는 특별한 메시지 전달
    # 돈 쓸 날도 없고, 돈도 없다면 (또는 이미 초과) daily_spend_recommendation은 0 유지


    return render_template(
        'dashboard.html',
        title='대시보드',
        today_date=today, # 오늘 날짜 객체 전달 (템플릿에서 월 표시 등에 사용)
        monthly_allowance=monthly_allowance,
        total_spending_this_month=total_spending_this_month,
        remaining_allowance=remaining_allowance,
        remaining_days_this_month=remaining_days_this_month,
        future_no_spending_days_count=future_no_spending_days_count,
        spendable_remaining_days=spendable_remaining_days,
        daily_spend_recommendation=daily_spend_recommendation
    )