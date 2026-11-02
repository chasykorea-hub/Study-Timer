# 스터디 타이머

Python/FastAPI와 HTML/CSS/JavaScript로 만든 로컬 포모도로 스터디 타이머입니다. 사용자별로 집중 세션을 SQLite에 기록하고, 오늘 과목별 학습 시간과 최근 7일 통계를 보여줍니다.

## DevOps가 필요한 이유

개발 환경과 운영 환경에서 같은 방식으로 설치·실행할 수 있도록 의존성을 명시하고, 생성 데이터와 비밀정보가 소스 저장소에 섞이지 않도록 관리해야 합니다. 이 프로젝트는 `requirements.txt`, 실행 문서, `.gitignore`를 제공해 재현 가능한 설치와 안전한 GitHub 업로드를 돕습니다.

## 설치

macOS에서 Python 3.10 이상을 사용하세요.

```bash
cd /path/to/HW2_StudyTimer/upload
python3 -m pip install -r requirements.txt
```

## 실행

```bash
cd /path/to/HW2_StudyTimer/upload
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

브라우저에서 <http://127.0.0.1:8000>을 열고 이름과 과목을 입력합니다. 테스트할 때는 집중·휴식 시간을 짧게 설정할 수 있습니다. 실행 시 `study_timer.sqlite3`가 `upload` 폴더에 자동 생성됩니다.

## GitHub 업로드 전 확인

`study_timer.sqlite3`, Python 캐시, 로그, 환경변수 파일은 `.gitignore`로 제외됩니다. 인증정보나 개인정보는 소스에 넣지 마세요.
