# database.py
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, Date, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    timezone = Column(String, default=Config.TIMEZONE)
    created_at = Column(DateTime, default=datetime.now)

    habits = relationship('Habit', back_populates='user', cascade='all, delete-orphan')


class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    habit_name = Column(String, nullable=False)
    reminder_time = Column(Time, nullable=False)
    start_date = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)

    user = relationship('User', back_populates='habits')
    logs = relationship('DailyLog', back_populates='habit', cascade='all, delete-orphan')


class DailyLog(Base):
    __tablename__ = 'daily_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    log_date = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    habit = relationship('Habit', back_populates='logs')


def init_db():
    """ایجاد جداول پایگاه داده"""
    Base.metadata.create_all(engine)
    print("✅ پایگاه داده آماده شد")


def get_session():
    """دریافت session جدید"""
    return Session()