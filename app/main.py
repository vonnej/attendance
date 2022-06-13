import uvicorn
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.config.auth import AuthHandler
from app.config.conn import get_db
from app.models.model_admin import Model_admin
from app.routes import crud
from app.config.auth_wrapper import AuthWrapperClass

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = AuthWrapperClass()

auth_handler = AuthHandler()

templates = Jinja2Templates(directory="app/templates")
app.include_router(crud.router)
# app.include_router(security.router)


@app.get("/", response_class=HTMLResponse)
def get_main_page(request: Request):    # 메인화면
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/protected/index_admin", response_class=HTMLResponse)
def get_main_admin(request: Request, token: str = Depends(oauth2_scheme)):   # 관리자 메인화면
    return templates.TemplateResponse("index_admin.html", context={"request": request})


@app.get("/attendees_today/", response_class=HTMLResponse)
def get_attendance_table_page(request: Request):   # 학부모들이 출석 완료 후 보여지는 화면
    return templates.TemplateResponse("attendees_today.html", context={"request": request})


@app.get("/create_duplicate/", response_class=HTMLResponse)
def get_create_duplicate_page(request: Request):   # 학부모 출석시 중복된 이름이 있을 경우
    return templates.TemplateResponse("create_duplicate.html", context={"request": request})


@app.get("/create_duplicate_admin/", response_class=HTMLResponse)
def get_create_duplicate_admin_page(request: Request):   # 관리자 페이지에서 참석자 생성 시 중복된 이름이 있을 경우
    return templates.TemplateResponse("create_duplicate_admin.html", context={"request": request})


@app.get("/delete_failure/", response_class=HTMLResponse)
def get_delete_failure_page(request: Request):   # 참석자 삭제 실패시 뜨는 화면
    return templates.TemplateResponse("delete_failure.html", context={"request": request})


@app.get("/login_failure/", response_class=HTMLResponse)
def get_login_failure_page(request: Request):   # 로그인 실패시 뜨는 화면
    return templates.TemplateResponse("login_failure.html", context={"request": request})


@app.get("/update_failure/", response_class=HTMLResponse)
def get_update_failure_page(request: Request):   # 수정 실패시 뜨는 화면
    return templates.TemplateResponse("update_failure.html", context={"request": request})


@app.get("/attend_success", response_class=HTMLResponse)
def get_attend_success(request: Request):   # 출석 완료창
    return templates.TemplateResponse("attend_success.html", context={"request": request})


@app.get("/protected/attendance_table", response_class=HTMLResponse)
def get_attendance_table_page(request: Request, token: str = Depends(oauth2_scheme)):   # 관리자 출석부 테이블
    return templates.TemplateResponse("attendance_table_admin.html", context={"request": request})


@app.get("/login_page/", response_class=HTMLResponse)
def get_login_page(request: Request):   # 로그인화면
    return templates.TemplateResponse("login.html", context={"request": request})


@app.get("/attend/", response_class=HTMLResponse)
def get_attend_input_page(request: Request):  # 출석등록 화면
    return templates.TemplateResponse("attend.html", context={"request": request})


@app.get("/protected", response_class=HTMLResponse)
def get_main_admin(request: Request, token: str = Depends(oauth2_scheme)):
    return templates.TemplateResponse("index_admin.html", context={"request": request})


@app.post("/register")   # 관리자 계정 생성
def register(username: str, password: str, db: Session = Depends(get_db),
             token: str = Depends(oauth2_scheme)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).all()
    if user_db:
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(password)
    admin_db = Model_admin(username=username, password=hashed_password)
    db.add(admin_db)
    db.commit()
    return username


@app.get('/token')
def get_token(username: str, password: str, db: Session = Depends(get_db)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).first()
    user = None
    if user_db:
        user = username
    if (user is None) or (not auth_handler.verify_password(password, user_db.password)):
        raise HTTPException(status_code=401, detail="계정명 또는 비번이 잘못됐습니다")
    token = auth_handler.encode_token(username)
    return token


@app.post('/login/', response_class=HTMLResponse)  # 관리자 로그인
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).first()
    # user_db = get_user_by_username(username=username)
    user = None
    if user_db:
        user = username
    if (user is None) or (not auth_handler.verify_password(password, user_db.password)):
        # raise HTTPException(status_code=401, detail="계정명 또는 비번이 잘못됐습니다")
        return templates.TemplateResponse("login_failure.html", {"request": request})
    # token = dict(Authorization=f"Bearer {auth_handler.encode_token(user_db.username)}")
    token = auth_handler.encode_token(username)
    # context = {}
    # context['request'] = request
    # context['token'] = access_token
    # # 관리자 페이지 렌더링 리턴할때 context도 같이 전달
    response = RedirectResponse("/protected/attendance_table", status_code=302)
    response.set_cookie(key="access_token", value="Bearer {}".format(token), httponly=True)
    return response
    # return templates.TemplateResponse("login_success.html", context={"request": request, "token": token})
    # return {'access_token': access_token}


@app.get('/logout', response_class=HTMLResponse)
def logout(token: str = Depends(oauth2_scheme)):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
