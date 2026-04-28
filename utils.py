# utils.py
from datetime import datetime, time, date, timedelta
from database import get_session, Habit, DailyLog


def parse_time(time_str: str):
    """تبدیل رشته زمان به آبجکت time"""
    try:
        hour, minute = map(int, time_str.strip().split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)
    except Exception:
        pass
    return None


def get_habit_stats(habit_id: int):
    """دریافت آمار یک عادت"""
    session = get_session()
    try:
        habit = session.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return None

        logs = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id
        ).order_by(DailyLog.log_date).all()

        # completed=True موفق، completed=False ناموفق، completed=None بدون پاسخ
        success_count = sum(1 for log in logs if log.completed is True)
        fail_count = sum(1 for log in logs if log.completed is False)
        no_response_count = sum(1 for log in logs if log.completed is None)

        total_days = (date.today() - habit.start_date).days + 1
        success_rate = round((success_count / total_days * 100) if total_days > 0 else 0, 1)

        current_streak, best_streak = calculate_streak(habit_id)

        return {
            'habit_name': habit.habit_name,
            'current_day': total_days,
            'success_count': success_count,
            'fail_count': fail_count,
            'no_response_count': no_response_count,
            'success_rate': success_rate,
            'current_streak': current_streak,
            'best_streak': best_streak,
            'start_date': habit.start_date,
            'logs': logs
        }
    finally:
        session.close()


def calculate_streak(habit_id: int):
    """
    محاسبه استریک فعلی و بهترین استریک.
    - فقط completed=False استریک را می‌شکند.
    - completed=None (بدون پاسخ) استریک را نمی‌شکند اما به آن اضافه نمی‌کند.
    """
    session = get_session()
    try:
        logs = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id
        ).order_by(DailyLog.log_date.desc()).all()

        # محاسبه استریک فعلی (از آخرین روز به عقب، تا زمانی که False نباشد)
        current_streak = 0
        for log in logs:
            if log.completed is True:
                current_streak += 1
            elif log.completed is False:
                # شکست واقعی — استریک را می‌شکند
                break
            # None: بدون پاسخ — از استریک فعلی رد می‌شویم ولی نمی‌شکنیم

        # محاسبه بهترین استریک (فقط True‌های متوالی، False می‌شکند)
        best_streak = 0
        temp_streak = 0
        for log in reversed(logs):
            if log.completed is True:
                temp_streak += 1
                best_streak = max(best_streak, temp_streak)
            elif log.completed is False:
                temp_streak = 0
            # None: بدون پاسخ — نه اضافه می‌کند نه می‌شکند

        return current_streak, best_streak
    finally:
        session.close()


def check_consecutive_fails(habit_id: int, threshold: int = 3):
    """
    بررسی شکست‌های متوالی.
    هم completed=False و هم completed=None به عنوان «ناموفق» در نظر گرفته می‌شوند.
    """
    session = get_session()
    try:
        recent_logs = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id
        ).order_by(DailyLog.log_date.desc()).limit(threshold).all()

        if len(recent_logs) < threshold:
            return False

        # هر لاگی که True نباشد (False یا None) به عنوان ناموفق حساب می‌شود
        return all(log.completed is not True for log in recent_logs)
    finally:
        session.close()


def generate_progress_graph(logs, start_date):
    """تولید نمودار پیشرفت متنی برای ۷ روز اخیر"""
    if not logs:
        return "هنوز لاگی ثبت نشده!"

    graph = "📊 نمودار ۷ روز اخیر:\n\n"

    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    log_dict = {log.log_date: log for log in logs}

    # weekday(): 0=Monday, 1=Tuesday, ..., 6=Sunday
    day_names = ["دو", "سه", "چه", "پن", "جم", "شن", "یک"]

    for day in last_7_days:
        day_abbr = day_names[day.weekday()]

        if day < start_date:
            symbol = "⬜️"
        elif day in log_dict:
            log = log_dict[day]
            if log.completed is True:
                symbol = "✅"
            elif log.completed is False:
                symbol = "❌"
            else:
                symbol = "⏸"
        else:
            symbol = "⏸"

        graph += f"{day_abbr} {symbol} "

    graph += "\n\n✅ انجام شد | ❌ انجام نشد | ⏸ بدون پاسخ | ⬜️ قبل از شروع"

    return graph