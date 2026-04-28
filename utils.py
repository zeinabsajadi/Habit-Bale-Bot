# utils.py
from datetime import datetime, date, timedelta
from database import get_session, DailyLog, Habit

def calculate_streak(habit_id):
    """محاسبه استریک فعلی و بهترین استریک"""
    session = get_session()
    try:
        logs = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id
        ).order_by(DailyLog.log_date.desc()).all()
        
        current_streak = 0
        best_streak = 0
        temp_streak = 0
        
        for log in reversed(logs):
            if log.completed:
                temp_streak += 1
                best_streak = max(best_streak, temp_streak)
            else:
                temp_streak = 0
        
        # محاسبه استریک فعلی
        for log in logs:
            if log.completed:
                current_streak += 1
            else:
                break
        
        return current_streak, best_streak
    finally:
        session.close()

def get_habit_stats(habit_id):
    """دریافت آمار کامل یک عادت"""
    session = get_session()
    try:
        habit = session.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return None
        
        logs = session.query(DailyLog).filter(DailyLog.habit_id == habit_id).all()
        
        success_count = sum(1 for log in logs if log.completed is True)
        fail_count = sum(1 for log in logs if log.completed is False)
        no_response_count = sum(1 for log in logs if log.completed is None)
        
        total_days = (date.today() - habit.start_date).days + 1
        success_rate = round((success_count / total_days * 100), 1) if total_days > 0 else 0
        
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
            'logs': logs,
            'start_date': habit.start_date
        }
    finally:
        session.close()

def generate_progress_graph(logs, start_date):
    graph = ""
    current_date = start_date
    today = date.today()
    week_num = 1
    week_logs = []
    
    while current_date <= today and (current_date - start_date).days < 40:
        log = next((l for l in logs if l.log_date == current_date), None)
        
        if log:
            if log.completed is True:
                week_logs.append("✅")
            elif log.completed is False:
                week_logs.append("❌")
            else:
                week_logs.append("⏭️")
        else:
            week_logs.append("⬜")
        
        if len(week_logs) == 7:
            graph += f"هفته {week_num}: {''.join(week_logs)}\n"
            week_logs = []
            week_num += 1
        
        current_date += timedelta(days=1)
    
    if week_logs:
        graph += f"هفته {week_num}: {''.join(week_logs)}\n"
    
    return graph

def parse_time(time_str):
    try:
        return datetime.strptime(time_str.strip(), "%H:%M").time()
    except:
        return None

def check_consecutive_fails(habit_id, days=3):
    session = get_session()
    try:
        recent_logs = session.query(DailyLog).filter(
            DailyLog.habit_id == habit_id
        ).order_by(DailyLog.log_date.desc()).limit(days).all()
        
        if len(recent_logs) < days:
            return False
        
        return all(log.completed is False for log in recent_logs)
    finally:
        session.close()
