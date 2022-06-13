from pydantic import BaseModel


class Schema_admin(BaseModel):
    username : str
    password : str

    class Config:
        orm_mode = True