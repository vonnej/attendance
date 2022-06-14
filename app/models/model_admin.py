from sqlalchemy import Column, String

from app.config.database import Base


class Model_admin(Base):
    __tablename__ = "admins"
    username = Column(String(30), primary_key=True, index=True)
    password = Column(String(255))




