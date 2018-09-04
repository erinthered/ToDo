from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///todo.db', echo=True)

# Base class
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    todos = relationship('Todo', backref='user', lazy='dynamic')

    def __init__(self, username):
        self.username = username

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String)

Base.metadata.create_all(engine)
