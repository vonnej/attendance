from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class schema_attendee(BaseModel):
    attendee_name : str
    attend_date : date
    create_time : datetime
    update_time : Optional[datetime] = None

    class Config:
        orm_mode = True



