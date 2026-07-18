from database.database import Base
from sqlalchemy import Column, Integer, String


class UserDB(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    role = Column(String)
    country = Column(String)


class EventDB(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    user = Column(String)
    action = Column(String)
    location = Column(String)
    status = Column(String)


class AlertDB(Base):

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user = Column(String)
    level = Column(String)
    score = Column(Integer)
    reason = Column(String)
