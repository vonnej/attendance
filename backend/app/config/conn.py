from backend.app.config.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db  # DB 연결 성공한 경우, DB 세션 시작
    finally:
        db.close()  # DB 세션이 시작된 후, API 호출이 마무리되면 DB 세션을 닫아준다.


