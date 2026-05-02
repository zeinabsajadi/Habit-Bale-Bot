"""
user_stats.py
محاسبه آمار لازم برای سیستم انتخاب هوشمند گیف.
این ماژول فقط داده می‌خواند و هیچ تغییری در دیتابیس نمی‌دهد.
"""

from datetime import date, timedelta
from database import get_session, DailyLog, User, Habit


class UserStats:
    """
    آبجکت حاوی تمام آمار لازم برای تابع get_response_category.

    فیلدها:
        did_today    : آیا امروز عادت انجام شده (True/False)
        streak       : تعداد روزهای موفق متوالی فعلی
        miss_streak  : تعداد روزهای متوالی که انجام نشده (False یا None)
        relationship : امتیاز رابطه کاربر با ربات (0-100)
        last_comeback: آیا دیروز بعد از غیبت برگشته بود (True/False)
    """

    def __init__(self, did_today: bool, streak: int, miss_streak: int,
                 relationship: float, last_comeback: bool):
        self.did_today = did_today
        self.streak = streak
        self.miss_streak = miss_streak
        self.relationship = relationship
        self.last_comeback = last_comeback


def get_user_stats(user_id: int, habit_id: int) -> UserStats:
    """
    آمار کامل کاربر را برای یک عادت مشخص محاسبه می‌کند.
    این تابع فقط می‌خواند و هیچ چیزی را تغییر نمی‌دهد.
    """
    session = get_session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        relationship_score = float(user.relationship_score) if user and user.relationship_score is not None else 50.0
        last_comeback_date = user.last_comeback_date if user else None

        logs = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id
        ).order_by(DailyLog.log_date.desc()).all()

        today = date.today()
        yesterday = today - timedelta(days=1)

        # --- did_today ---
        did_today = False
        for log in logs:
            if log.log_date == today:
                did_today = (log.completed is True)
                break

        # --- streak (فقط True حساب می‌شود، False قطع می‌کند) ---
        streak = 0
        for log in logs:
            if log.log_date >= today:
                continue
            if log.completed is True:
                streak += 1
            elif log.completed is False:
                break
        if did_today:
            streak += 1

        # --- miss_streak (False یا None هر دو miss هستند) ---
        miss_streak = 0
        if not did_today:
            for log in logs:
                if log.log_date >= today:
                    continue
                if log.completed is not True:
                    miss_streak += 1
                else:
                    break
            miss_streak += 1  # امروز هم miss

        # --- last_comeback ---
        # دیروز True بوده، اما پریروز یا قبل‌تر miss داشته
        last_comeback = False
        if last_comeback_date and last_comeback_date == yesterday:
            last_comeback = True
        else:
            # بررسی مستقیم از لاگ‌ها
            yesterday_log = None
            day_before_yesterday_log = None
            for log in logs:
                if log.log_date == yesterday:
                    yesterday_log = log
                elif log.log_date == yesterday - timedelta(days=1):
                    day_before_yesterday_log = log

            if (yesterday_log and yesterday_log.completed is True and
                    day_before_yesterday_log and day_before_yesterday_log.completed is not True):
                last_comeback = True

        return UserStats(
            did_today=did_today,
            streak=streak,
            miss_streak=miss_streak,
            relationship=relationship_score,
            last_comeback=last_comeback,
        )
    finally:
        session.close()


def update_relationship_score(user_id: int, did_today: bool) -> None:
    """
    امتیاز رابطه را بعد از ثبت پاسخ روزانه به‌روزرسانی می‌کند.
    موفقیت: +2 (حداکثر 100)
    شکست:   -3 (حداقل 0)
    """
    session = get_session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            return

        current = float(user.relationship_score) if user.relationship_score is not None else 50.0

        if did_today:
            new_score = min(100.0, current + 2.0)
        else:
            new_score = max(0.0, current - 3.0)

        user.relationship_score = new_score
        session.commit()
    except Exception as e:
        print(f"⚠️ خطا در update_relationship_score: {e}")
    finally:
        session.close()


def record_comeback_if_needed(user_id: int, habit_id: int) -> None:
    """
    اگر کاربر امروز موفق بوده و دیروز miss داشته،
    last_comeback_date را ذخیره می‌کند تا فردا قابل استفاده باشد.
    """
    session = get_session()
    try:
        today = date.today()
        yesterday = today - timedelta(days=1)

        yesterday_log = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id,
            DailyLog.log_date == yesterday
        ).first()

        if yesterday_log and yesterday_log.completed is not True:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.last_comeback_date = today
                session.commit()
    except Exception as e:
        print(f"⚠️ خطا در record_comeback_if_needed: {e}")
    finally:
        session.close()