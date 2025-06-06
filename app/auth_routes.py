from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from .models import User
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data, nickname=form.nickname.data)
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('회원가입이 완료되었습니다! 이제 로그인해주세요.', 'success')
            return redirect(url_for('auth_bp_instance.login')) # 수정!
        except Exception as e:
            db.session.rollback()
            flash(f'회원가입 중 오류가 발생했습니다: {e}', 'error')
    return render_template('auth/signup.html', title='회원가입', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp_instance.hello_world_page')) # 수정! (들여쓰기도 확인)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'{user.nickname}님, 환영합니다!', 'success')
            # next_page 로직을 사용하려면 request를 import해야 합니다. (이미 되어 있음)
            next_page = request.args.get('next')
            # next_page가 있으면 그곳으로, 없으면 홈페이지로 리다이렉트
            return redirect(next_page) if next_page else redirect(url_for('main_bp_instance.hello_world_page')) # 수정!
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'error')
    return render_template('auth/login.html', title='로그인', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('성공적으로 로그아웃되었습니다.', 'info')
    return redirect(url_for('main_bp_instance.hello_world_page')) 