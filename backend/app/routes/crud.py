from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from backend.app.config.conn import get_db
from backend.app.config.database import engine
from backend.app.models.model_admin import Model_admin
from backend.app.models.model_attendee import Model_attendee
from backend.app.routes.security import auth_handler

router = APIRouter()

session = Session(bind=engine)

@router.get("/attendees")
def get_attendee_client(db: Session=Depends(get_db)):
    return db.query(Model_attendee.attendee_name).all()

# @router.get("/protected/attendees")
# def get_attendee_admin(username=Depends(auth_handler.auth_wrapper),
#                  db: Session = Depends(get_db)):   # 관리자: 전체 출석 데이터 조회(이름, 날짜, 게시시간, 수정시간 모든 정보)
#     return db.query(Model_attendee.attendee_name, Model_attendee.attend_date).all()


@router.get("/attendees/{attend_date}")   # 관리자: 해당일자 출석 데이터 조회(전체정보 출력)
def get_attendee_by_day_(attend_date: date,
                         db: Session = Depends(get_db)):
    return db.query(Model_attendee.attendee_name).filter(Model_attendee.attend_date == attend_date).all()

users = session.query(Model_admin).all()   # list of tuples로 반환

print(session.query(Model_attendee.attendee_name).all())

def get_user_by_username(username: str):
    return session.query(Model_admin).filter(Model_admin.username == username).first()

@router.post("/attendees/create/")
def create_attendee(attendee_name: str = Form(...), db: Session =Depends(get_db)):    # 참석자: 출석 기능(당일 출석은 당일날만 가능)
        # Attendees 데이터베이스 모델 인스턴스 생성                                          # 폼데이터
    attendee_db = Model_attendee(attendee_name = attendee_name,
                                 attend_date = datetime.today(),
                                 create_time = datetime.now()
                                 )
    db.add(attendee_db)  # 세션에 추가하고 커밋
    db.commit()
    return RedirectResponse(url="/attendance_table", status_code=302)


@router.put("/attendees/update")
def update_attendee_admin(attendee_name: str, attend_date: date, new_name: str,
                    db: Session = Depends(get_db)):  # 관리자: 출석내용 수정기능(이름 수정)

    attendee = db.query(Model_attendee).get((attendee_name, attend_date))

    if attendee:
        attendee.attendee_name = new_name  # 입력받은 새 이름으로 변경
        attendee.update_time = datetime.now()  # 업데이트된 시간 변경
        db.commit()  # 커밋하기

    if not attendee:
        raise HTTPException(status_code=500, detail="참석자가 존재하지 않거나 날짜가 다릅니다")  ## 코드 수정 404 아님 인터널 에러로 변경

    return attendee


@router.delete("/attendees/delete")
def delete_attendee_admin(attendee_name: str, attend_date: date,
                    db: Session = Depends(get_db)):  # 관리자: 참석자 삭제

    attendee = db.query(Model_attendee).get((attendee_name, attend_date))

    if attendee:
        db.delete(attendee)
        db.commit()
    else:
        raise HTTPException(status_code=500, detail="삭제할 이름이 없거나 날짜가 틀립니다")

    return "{} 삭제 완료!".format(attendee_name)



