from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from backend.app.config.auth import AuthHandler
from backend.app.config.conn import get_db
from backend.app.models.model_admin import Model_admin

router = APIRouter()
auth_handler = AuthHandler()

@router.post("/register")   # 관리자 계정 생성
def register(username: str, password: str, db: Session = Depends(get_db)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).all()
    if user_db:
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(password)
    admin_db = Model_admin(username = username,
                           password = hashed_password)
    db.add(admin_db)
    db.commit()

@router.post('/login/')  # 관리자 로그인
def login(username: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).first()
    # user_db = get_user_by_username(username=username)
    user = None
    if user_db:
        user = username
    if (user is None) or (not auth_handler.verify_password(password, user_db.password)):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = auth_handler.encode_token(user_db.username)
    # token = auth_handler.encode_token(username)
    context = {}
    context['authorization'] = token
    # 관리자 페이지 렌더링 리턴할때 context도 같이 전달
    # return templates.TemplateResponse("item.html", context)

    return {'token': token}
