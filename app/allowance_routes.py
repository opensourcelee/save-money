from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .forms import AllowanceForm # 우리가 만든 용돈 설정 폼
from .models import Allowance, User # Allowance 모델과 User 모델
from . import db # 데이터베이스 객체

allowance_bp = Blueprint('allowance', __name__)

@allowance_bp.route('/set_allowance', methods=['GET', 'POST'])
@login_required # 로그인한 사용자만 접근 가능
def set_allowance():
    form = AllowanceForm()

    # 현재 사용자의 해당 월에 이미 설정된 용돈이 있는지 확인
    # 폼이 제출되기 전에도, 그리고 폼을 다시 보여줄 때도 필요할 수 있으므로 여기서 조회
    # (더 좋은 방법은 폼을 통해 월을 선택하면 해당 월의 데이터를 보여주는 방식)
    # 지금은 사용자가 폼에서 선택한 월을 기준으로 처리합니다.
    existing_allowance = None
    if request.method == 'GET' and form.set_month.data: # 페이지 처음 로드 시 또는 월 변경 시
         existing_allowance = Allowance.query.filter_by(user_id=current_user.id, set_month=form.set_month.data).first()
    elif form.is_submitted() and form.set_month.data: # 폼 제출 시
         existing_allowance = Allowance.query.filter_by(user_id=current_user.id, set_month=form.set_month.data).first()


    if form.validate_on_submit(): # 폼이 제출되었고 유효성 검사를 통과했다면
        selected_month = form.set_month.data
        amount = form.amount.data

        # 이미 해당 월에 용돈이 설정되어 있다면 업데이트, 없다면 새로 생성
        if existing_allowance:
            existing_allowance.amount = amount
            flash(f'{selected_month} 용돈이 {amount:,.0f}원으로 업데이트되었습니다.', 'success')
        else:
            new_allowance = Allowance(amount=amount, set_month=selected_month, user_id=current_user.id)
            db.session.add(new_allowance)
            flash(f'{selected_month} 용돈이 {amount:,.0f}원으로 새로 설정되었습니다.', 'success')

        try:
            db.session.commit()
            # 성공 후 대시보드로 이동하거나, 현재 페이지에 머무르며 메시지 표시
            return redirect(url_for('allowance_bp_instance.set_allowance')) # 현재 페이지로 리다이렉트하여 새 정보 반영
        except Exception as e:
            db.session.rollback()
            flash(f'용돈 설정 중 오류가 발생했습니다: {e}', 'error')

    # GET 요청이거나 폼 유효성 검사 실패 시
    # 만약 existing_allowance 가 있는데 폼 제출이 아니라면, 폼의 기본값으로 채워줄 수 있음
    # (이 부분은 좀 더 복잡해지므로, 일단은 폼 제출 시에만 기존 데이터 수정으로 처리)
    if request.method == 'GET' and existing_allowance:
         form.amount.data = existing_allowance.amount # 기존 금액을 폼에 표시


    # allowance_form.html 을 렌더링하고, 폼 객체와 현재 설정된 용돈 정보(있다면)를 전달
    return render_template('allowance_form.html', title='월별 용돈 설정', form=form, current_allowance=existing_allowance)