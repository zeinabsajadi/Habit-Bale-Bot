from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, Date, Time, Float, ForeignKey, text
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

    # --- فیلدهای جدید برای سیستم گیف هوشمند ---
    relationship_score = Column(Float, default=50.0)   # امتیاز رابطه (0-100)
    last_comeback_date = Column(Date, nullable=True)    # تاریخ آخرین بازگشت بعد از غیبت

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
    failure_reason = Column(String, nullable=True)
    habit = relationship('Habit', back_populates='logs')


def _run_migrations():
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(daily_logs)"))
            columns = [row[1] for row in result.fetchall()]

            if "failure_reason" not in columns:
                conn.execute(text("ALTER TABLE daily_logs ADD COLUMN failure_reason TEXT"))
                conn.commit()
                print("✅ Migration: ستون failure_reason اضافه شد.")
            else:
                print("ℹ️ Migration: ستون failure_reason از قبل موجود است.")

        except Exception as e:
            print(f"⚠️ Migration warning (daily_logs): {e}")

    # migration برای فیلدهای جدید جدول users
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if "relationship_score" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN relationship_score REAL DEFAULT 50.0"))
                conn.commit()
                print("✅ Migration: ستون relationship_score اضافه شد.")
            else:
                print("ℹ️ Migration: ستون relationship_score از قبل موجود است.")

            if "last_comeback_date" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_comeback_date DATE"))
                conn.commit()
                print("✅ Migration: ستون last_comeback_date اضافه شد.")
            else:
                print("ℹ️ Migration: ستون last_comeback_date از قبل موجود است.")

        except Exception as e:
            print(f"⚠️ Migration warning (users): {e}")


def init_db():
    """ایجاد جداول پایگاه داده و اجرای migration ها"""
    Base.metadata.create_all(engine)
    _run_migrations()
    print("✅ پایگاه داده آماده شد")


def get_session():
    """دریافت session جدید"""
    return Session()