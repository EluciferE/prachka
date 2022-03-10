from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from os import path
from uuid import uuid1

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    chat_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    status = Column(String, nullable=False)
    tmp = Column(String)

    def __init__(self, chat_id: int, username: str, status: str, tmp: str = ""):
        self.chat_id = chat_id
        self.username = username
        self.status = status
        self.tmp = tmp

    def __repr__(self):
        return f"User [{self.username}: {self.status}], tmp: {self.tmp}"


class Request(Base):
    __tablename__ = "requests"

    username = Column(String, primary_key=True)
    day = Column(String, nullable=False)
    time = Column(String, nullable=False)
    machine = Column(String, nullable=False)
    value = Column(String)

    def __init__(self, username: str, day: str, time: str, machine: str, value: str):
        self.username = username
        self.day = day
        self.time = time
        self.machine = machine
        self.value = value


class SignUp(Base):
    __tablename__ = "signup"

    username = Column(String, primary_key=True)
    date = Column(String, nullable=False)

    def __init__(self, username: str, date: str):
        self.username = username
        self.date = date


class Note(Base):
    __tablename__ = "note"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    date = Column(String, nullable=False)
    day = Column(String, nullable=False)
    time = Column(String, nullable=False)
    machine = Column(String, nullable=False)
    value = Column(String)
    cell = Column(String, nullable=False)

    announceStart = Column(Boolean, nullable=False)
    announceEnd = Column(Boolean, nullable=False)
    announceNextDay = Column(Boolean, nullable=False)

    def __init__(self, username: str, date: str, day: str, time: str,
                 machine: str, value: str, cell: str):
        self.id = str(uuid1())
        self.username = username
        self.date = date
        self.day = day
        self.time = time
        self.machine = machine
        self.value = value
        self.cell = cell

        self.announceStart = False
        self.announceEnd = False
        self.announceNextDay = False


class AntiSpam(Base):
    __tablename__ = "antispam"

    username = Column(String, primary_key=True)
    date = Column(String, nullable=False)

    def __init__(self, username: str, date: str):
        self.username = username
        self.date = date


def getSession() -> Session:
    engine = create_engine(f"sqlite:///dataBase/main.sqlite?check_same_thread=False")
    if not path.exists("main.sqlite"):
        Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()