from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .forms import NoSpendingDayForm # 우리가 만든 무지출일 설정 폼
from .models import NoSpendingDay # NoSpendingDay 모델
from . import db # 데이터베이스 객체
from datetime import date # 날짜 비교 등을 위해

nsd_bp = Blueprint('no_spending_day', __name__) # 'nsd'는 No Spending Day의 약자

@nsd_bp.route('/toggle', methods=['GET', 'POST']) # URL은 /no_spending_day/toggle
@login_required # 로그인한 사용자만 접근 가능
def toggle_no_spending_day():
    form = NoSpendingDayForm()

    if form.validate_on_submit(): # 폼이 제출되었고 유효성 검사를 통과했다면
        selected_date = form.date.data

        # 현재 사용자의 해당 날짜에 이미 무지출일로 설정되어 있는지 확인
        existing_nsd = NoSpendingDay.query.filter_by(user_id=current_user.id, date=selected_date).first()

        try:
            if existing_nsd:
                # 이미 설정되어 있다면 삭제 (해제)
                db.session.delete(existing_nsd)
                db.session.commit()
                flash(f'{selected_date.strftime("%Y년 %m월 %d일")} 무지출일 설정이 해제되었습니다.', 'info')
            else:
                # 설정되어 있지 않다면 새로 추가 (설정)
                new_nsd = NoSpendingDay(date=selected_date, user_id=current_user.id)
                db.session.add(new_nsd)
                db.session.commit()
                flash(f'{selected_date.strftime("%Y년 %m월 %d일")}이(가) 무지출일로 설정되었습니다.', 'success')

            # 성공 후, 같은 페이지로 리다이렉트하여 목록을 갱신합니다.
            return redirect(url_for('no_spending_day_bp_instance.toggle_no_spending_day')) # 블루프린트 등록 이름 사용!

        except Exception as e:
            db.session.rollback()
            flash(f'무지출일 설정/해제 중 오류가 발생했습니다: {e}', 'error')

    # GET 요청이거나 폼 유효성 검사 실패 시
    # 현재 사용자의 모든 무지출일 목록을 가져와서 날짜순으로 정렬
    user_no_spending_days_objects = NoSpendingDay.query.filter_by(user_id=current_user.id).order_by(NoSpendingDay.date.asc()).all()
    # HTML 템플릿에는 날짜 객체 자체를 전달하는 것이 아니라, 날짜 객체 리스트를 전달합니다.
    # 템플릿에서 strftime을 사용해서 표시합니다.
    user_no_spending_dates = [nsd.date for nsd in user_no_spending_days_objects]


    return render_template(
        'no_spending_day_form.html',
        title='무지출일 설정',
        form=form,
        no_spending_days=user_no_spending_dates # 날짜 객체의 리스트를 전달
    )