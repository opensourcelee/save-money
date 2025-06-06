from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime # current_year를 위해 추가 (선택 사항)

# 데이터베이스 객체 만들기 (아직 앱이랑 연결은 안 함)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth_bp_instance.login' # 블루프린트 name을 사용하도록 수정
login_manager.login_message_category = 'info'
login_manager.login_message = "로그인이 필요한 페이지입니다."

def create_app():
    my_website = Flask(__name__)
    my_website.config['SECRET_KEY'] = '아무도모르는나만의비밀키' # 실제 운영시에는 복잡한 키로 변경

    import os
    project_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__))) # 프로젝트 루트 디렉토리
    my_website.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(project_dir, 'site.db')
    my_website.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SQLAlchemy 이벤트 처리 안 함 (성능 향상)

    db.init_app(my_website)
    migrate.init_app(my_website, db)
    login_manager.init_app(my_website)

    from .models import User # User 모델은 여기서 import 하는 것이 일반적입니다.

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 현재 연도를 모든 템플릿에서 사용할 수 있도록 등록 (선택 사항)
    @my_website.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().year}

    # --- 블루프린트 등록 ---
    # 기존 블루프린트 등록 (홈페이지 등)
    from .routes import main_routes_for_website
    my_website.register_blueprint(main_routes_for_website, name='main_bp_instance')

    # 인증(회원가입, 로그인) 관련 블루프린트 등록
    from .auth_routes import auth_bp
    my_website.register_blueprint(auth_bp, url_prefix='/auth', name='auth_bp_instance')

    # 용돈 설정 관련 블루프린트 등록
    from .allowance_routes import allowance_bp
    my_website.register_blueprint(allowance_bp, url_prefix='/allowance', name='allowance_bp_instance')

    # 지출 입력 관련 블루프린트 등록
    from .spending_routes import spending_bp
    my_website.register_blueprint(spending_bp, url_prefix='/spending', name='spending_bp_instance')

    # 무지출일 설정 관련 블루프린트 등록 (새로 추가!)
    from .no_spending_day_routes import nsd_bp # 파일 이름과 변수 이름 확인!
    my_website.register_blueprint(nsd_bp, url_prefix='/no_spending_day', name='no_spending_day_bp_instance')

    return my_website