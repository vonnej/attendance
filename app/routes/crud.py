from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse

from app.config.auth import AuthHandler
from app.config.auth_wrapper import AuthWrapperClass
from app.config.conn import get_db
from app.config.database import engine
from app.models.model_admin import Model_admin
from app.models.model_attendee import Model_attendee

router = APIRouter()

session = Session(bind=engine)

auth_handler = AuthHandler()

oauth2_scheme = AuthWrapperClass()


@router.get("/attendees")
def get_attendee_client(db: Session = Depends(get_db)):
    return db.query(Model_attendee.attendee_name).all()


@router.get("/protected/attendees")
def get_attendee_admin(username=Depends(auth_handler.auth_wrapper),
                       db: Session = Depends(get_db)):  # 관리자: 전체 출석 데이터 조회(이름, 날짜, 게시시간, 수정시간 모든 정보)
    return db.query(Model_attendee.attendee_name, Model_attendee.attend_date).all()


@router.get("/attendees/{attend_date}")  # 해당일자 출석자 이름 조회
def get_attendee_by_day(attend_date: date,
                        db: Session = Depends(get_db)):
    attendee = db.query(Model_attendee.attendee_name).filter(Model_attendee.attend_date == attend_date).all()
    attendees = []

    for i in range(len(attendee)):
        attendees.append(attendee[i][0])

    if len(attendees) > 0:
        return attendees
    else:
        return "참석자가 없습니다"


users = session.query(Model_admin).all()  # list of tuples로 반환


@router.get("/return_attendees_today")  # 당일 출석자 반환
def get_attendee_by_today(db: Session = Depends(get_db)):
    today = datetime.now().date()
    attendee = db.query(Model_attendee.attendee_name).filter(Model_attendee.attend_date == today).all()
    attendees = []

    for i in range(len(attendee)):
        attendees.append(attendee[i][0])

    if len(attendees) > 0:
        return attendees
    else:
        return "참석자가 없습니다"


def get_user_by_username(username: str):
    return session.query(Model_admin).filter(Model_admin.username == username).first()


@router.post("/attendees/create_by_date", response_class=HTMLResponse)
def create_attendee_by_date(attendee_name: str = Form(...), attend_date: date = Form(...),
                            db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    attendee_db = Model_attendee(attendee_name=attendee_name,
                                 attend_date=attend_date,
                                 create_time=datetime.now())
    db.add(attendee_db)
    db.commit()

    return RedirectResponse(url="/attendance_table", status_code=302)


@router.post("/attendees/create/", response_class=HTMLResponse)
def create_attendee(attendee_name: str = Form(...), attend_date: date = datetime.today(),
                    db: Session = Depends(get_db)):  # 참석자: 출석 기능(당일 출석은 당일날만 가능)
    # Attendees 데이터베이스 모델 인스턴스 생성                                          # 폼데이터
    attendee = db.query(Model_attendee).get((attendee_name, attend_date))

    if attendee_name == attendee.attendee_name:
        raise HTTPException(status_code=500, detail="중복된 이름입니다")
        # return RedirectResponse(url="create_duplicate.html", status_code=302)
    if not attendee:
        attendee_db = Model_attendee(attendee_name=attendee_name,
                                     attend_date=datetime.today(),
                                     create_time=datetime.now()
                                     )

        db.add(attendee_db)  # 세션에 추가하고 커밋
        db.commit()

    return RedirectResponse(url="/attend_success", status_code=302)


@router.post("/attendees/update", response_class=HTMLResponse)
def update_attendee_admin(attendee_name: str = Form(...), attend_date: date = Form(...), new_name: str = Form(...),
                          db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):  # 관리자: 출석내용 수정기능(이름 수정)

    attendee = db.query(Model_attendee).get((attendee_name, attend_date))

    if attendee:
        attendee.attendee_name = new_name  # 입력받은 새 이름으로 변경
        attendee.update_time = datetime.now()  # 업데이트된 시간 변경
        db.commit()  # 커밋하기

    if not attendee:
        raise HTTPException(status_code=500, detail="참석자가 존재하지 않거나 날짜가 다릅니다")  # 코드 수정 404 아님 인터널 에러로 변경

    return RedirectResponse(url="/attendance_table", status_code=302)


@router.post("/attendees/delete", response_class=HTMLResponse)
def delete_attendee_admin(attendee_name: str = Form(...), attend_date: date = Form(...),
                          db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):  # 관리자: 참석자 삭제

    attendee = db.query(Model_attendee).get((attendee_name, attend_date))

    if attendee:
        db.delete(attendee)
        db.commit()
    else:
        raise HTTPException(status_code=500, detail="삭제할 이름이 없거나 날짜가 틀립니다")

    return RedirectResponse(url="/attendance_table", status_code=302)
    # return "{} 삭제 완료!".format(attendee_name)
