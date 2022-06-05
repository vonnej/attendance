from sqlalchemy import String, Date, DateTime, Column

from app.config.database import Base


class Model_attendee(Base):
    __tablename__ = "attendees"
    attendee_name = Column(String, primary_key=True, index=True)
    attend_date = Column(Date, primary_key=True, index=True)
    create_time = Column(DateTime)
    update_time = Column(DateTime, nullable=True)




