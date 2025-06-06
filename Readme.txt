설치 및 실행 방법입니다

1. 사전 준비: Python 3을 설치합니다. (https://www.python.org/) (Python 설치 시 pip도 함께 설치됩니다.)

2. 프로젝트 준비: 제출된 소스코드 압축 파일 save_money_.zip을 원하는 곳에 압축 해제합니다.
터미널(명령 프롬프트 또는 PowerShell)을 열고, 압축 해제한 `save_money` 폴더로 이동합니다.
(예: `PS C:\Users\FORYOUCOM\Documents\카카오톡 받은 파일\save money (1)>)

3. 가상 환경 설정: 터미널에서 다음 명령어를 순서대로 입력해줍니다
        python -m venv venv
        Set-ExecutionPolicy Unrestricted -Scope Process
        .\venv\Scripts\Activate.ps1
터미널 프롬프트 앞에 `(venv)`가 보이면 됐습니다

4.  필요한 라이브러리 설치: 터미널에서 다음 명령어를 입력해줍니다
        pip install -r requirements.txt

5.  데이터베이스 초기화: 터미널에서 다음 명령어들을 순서대로 입력해줍니다
        set FLASK_APP=run.py
        flask db upgrade
 (이러면 site.db 데이터베이스 파일이 생성되고, 프로젝트에 포함된 migrations 폴더의 정보를 바탕으로 필요한 테이블들이 만들어집니다.)

6.  웹 애플리케이션 실행: 터미널에서 다음 명령어를 입력합니다:
        python run.py
터미널에 Running on http://127.0.0.1:5000 메시지가 나오면 성공입니다.

7.  웹 브라우저에서 접속: http://127.0.0.1:5000 이 메시지 눌러서 링크 따라가기 하거나 웹 브라우저를 열고 주소창에 해당 주소를 입력하면 됩니다.
