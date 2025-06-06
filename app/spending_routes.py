from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .forms import SpendingForm # 우리가 만든 지출 입력 폼
from .models import SpendingRecord # SpendingRecord 모델 (User 모델은 여기서 직접 사용하지 않지만, SpendingRecord.spender를 통해 접근 가능)
from . import db # 데이터베이스 객체
from datetime import datetime # 날짜 비교 등을 위해 필요할 수 있음 (필터링 시)

spending_bp = Blueprint('spending', __name__)

@spending_bp.route('/add_spending', methods=['GET', 'POST'])
@login_required # 로그인한 사용자만 접근 가능
def add_spending():
    form = SpendingForm()

    if form.validate_on_submit(): # 폼이 제출되었고 유효성 검사를 통과했다면
        new_spending = SpendingRecord(
            date=form.date.data,
            category=form.category.data,
            amount=form.amount.data,
            description=form.description.data,
            user_id=current_user.id
        )
        try:
            db.session.add(new_spending)
            db.session.commit()
            flash(f'{form.date.data} 지출 내역 ({form.category.data}: {form.amount.data:,.0f}원)이 성공적으로 저장되었습니다.', 'success')
            return redirect(url_for('spending_bp_instance.add_spending'))
        except Exception as e:
            db.session.rollback()
            flash(f'지출 내역 저장 중 오류가 발생했습니다: {e}', 'error')

    return render_template('spending_form.html', title='오늘 지출 입력', form=form)

# 지출 내역 보기 라우트 및 함수 (주석 해제 및 내용 추가)
@spending_bp.route('/history')
@login_required
def spending_history():
    # 현재 로그인한 사용자의 모든 지출 내역을 가져옵니다.
    # 날짜 기준으로 내림차순(최신순)으로 정렬합니다.
    # .all()을 호출하여 실제 레코드 리스트를 가져옵니다.
    user_spendings = SpendingRecord.query.filter_by(user_id=current_user.id).order_by(SpendingRecord.date.desc()).all()

    # (선택 사항) 기간 필터링 로직 (GET 파라미터 사용)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = SpendingRecord.query.filter_by(user_id=current_user.id) # 기본 쿼리

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(SpendingRecord.date >= start_date)
        except ValueError:
            flash('시작일 날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)', 'error')
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(SpendingRecord.date <= end_date)
        except ValueError:
            flash('종료일 날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)', 'error')

    user_spendings_filtered = query.order_by(SpendingRecord.date.desc()).all()

    # (선택 사항) 필터링된 내역의 총 지출액 계산
    # total_spending_filtered = sum(record.amount for record in user_spendings_filtered) if user_spendings_filtered else 0

    return render_template(
        'spending_history.html',
        title='지출 내역 보기',
        spending_records=user_spendings_filtered, # 필터링된 결과를 전달
        # total_spending=total_spending_filtered, # (선택 사항)
        # 필터 유지를 위해 현재 선택된 날짜도 전달 (HTML 폼의 value에 사용)
        start_date_val=start_date_str if start_date_str else '',
        end_date_val=end_date_str if end_date_str else ''
    )