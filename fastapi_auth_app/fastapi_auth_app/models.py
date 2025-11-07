from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    boards = relationship("Board", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="boards")
    members = relationship("BoardMember", back_populates="board")
    tasks = relationship("Task", back_populates="board")

class BoardMember(Base):
    __tablename__ = "board_members"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="member")

    board = relationship("Board", back_populates="members")
    user = relationship("User")

class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="To Do")
    board_id = Column(Integer, ForeignKey("boards.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))

    board = relationship("Board", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
