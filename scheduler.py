# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_session, Habit, DailyLog
from messages import Messages
from datetime import date, datetime, timedelta
from bale import InlineKeyboardMarkup, InlineKeyboardButton
import pytz

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tehran'))
    
    def start(self):
        """شروع scheduler"""
        # هر دقیقه چک می‌کنه که آیا باید پیام بفرسته
        self.scheduler.add_job(
            self.check_reminders,
            'cron',
            minute='*',
            id='check_reminders'
        )
        
        # هر شب ساعت ۲۳:۵۰ لاگ‌های بدون پاسخ رو ثبت می‌کنه
        self.scheduler.add_job(
            self.mark_no_response,
            'cron',
            hour=23,
            minute=50,
            id='mark_no_response'
        )
        
        self.scheduler.start()
    
    async def check_reminders(self):
        """بررسی و ارسال یادآوری‌ها"""
        session = get_session()
        try:
            current_time = datetime.now().time()
            current_minute = current_time.replace(second=0, microsecond=0)
            
            habits = session.query(Habit).filter(Habit.is_active == True).all()
            
            for habit in habits:
                habit_time = habit.reminder_time.replace(second=0, microsecond=0)
                
                if habit_time == current_minute:
                    # بررسی که امروز لاگ نداشته باشه
                    existing_log = session.query(DailyLog).filter(
                        DailyLog.habit_id == habit.id,
                        DailyLog.log_date == date.today()
                    ).first()
                    
                    if not existing_log:
                        await self.send_daily_reminder(habit)
                        
                        # ایجاد لاگ جدید
                        new_log = DailyLog(
                            habit_id=habit.id,
                            log_date=date.today(),
                            completed=None
                        )
                        session.add(new_log)
                        session.commit()
        finally:
            session.close()
    
    async def send_daily_reminder(self, habit):
        """ارسال پیام یادآوری روزانه"""
        try:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ آره، انجام دادم",
                        callback_data=f"daily_{habit.id}_yes"
                    ),
                    InlineKeyboardButton(
                        "❌ نه، نتونستم",
                        callback_data=f"daily_{habit.id}_no"
                    )
                ]
            ])
            
            message = Messages.daily_reminder(habit.name)
            
            await self.bot.send_message(
                habit.user_id,
                message,
                components=keyboard
            )
        except Exception as e:
            print(f"خطا در ارسال یادآوری برای عادت {habit.id}: {e}")
    
    async def mark_no_response(self):
        """علامت‌گذاری لاگ‌های بدون پاسخ"""
        session = get_session()
        try:
            today = date.today()
            
            # پیدا کردن لاگ‌هایی که completed=None هستن
            no_response_logs = session.query(DailyLog).filter(
                DailyLog.log_date == today,
                DailyLog.completed == None
            ).all()
            
            for log in no_response_logs:
                log.completed = False
            
            session.commit()
        finally:
            session.close()
    
    def stop(self):
        """توقف scheduler"""
        self.scheduler.shutdown()
