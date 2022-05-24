import templates as templates
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.app.routes import crud, security
from backend.app.routes.security import auth_handler

app = FastAPI()


templates = Jinja2Templates(directory="templates")

app.include_router(crud.router)
app.include_router(security.router)

@app.get("/", response_class=HTMLResponse)
def get_main_page(request: Request):    # 메인화면
    return templates.TemplateResponse("index.html", context= {"request": request})

@app.get("/attendance_table/", response_class=HTMLResponse)
def get_attendance_table_page(request: Request):   # 출석부화면
    return templates.TemplateResponse("attendance_table.html", context= {"request": request})

@app.get("/login_page/", response_class=HTMLResponse)
def get_login_page(request: Request):   # 로그인화면
    return templates.TemplateResponse("login.html", context= {"request": request})

@app.get("/attend/", response_class=HTMLResponse)
def get_attend_input_page(request: Request):  # 출석등록 화면
    return templates.TemplateResponse("attend.html", context= {"request": request})

@app.get("/protected_main", response_class=HTMLResponse)
def get_main_admin(request: Request):
        return templates.TemplateResponse("index_admin.html", context= {"request": request})

@app.get("/protected")
def protected(username=Depends(auth_handler.auth_wrapper)):
    return {'name': username}

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)


