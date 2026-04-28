# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date
from database import get_session, Habit, DailyLog
from messages import Messages
from bale import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
import pytz


class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(Config.TIMEZONE))

    def start(self):
        """شروع scheduler"""
        self.scheduler.add_job(
            self.check_reminders,
            'cron',
            minute='*',
            id='check_reminders'
        )
        self.scheduler.add_job(
            self.mark_no_response,
            'cron',
            hour=23,
            minute=50,
            id='mark_no_response'
        )
        self.scheduler.start()
        print("✅ Scheduler شروع به کار کرد")

    async def check_reminders(self):
        """بررسی و ارسال یادآوری‌ها"""
        session = get_session()
        try:
            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)
            current_time = now.time()

            habits = session.query(Habit).filter(
                Habit.is_active == True
            ).all()

            for habit in habits:
                if (habit.reminder_time.hour == current_time.hour and
                        habit.reminder_time.minute == current_time.minute):

                    existing_log = session.query(DailyLog).filter(
                        DailyLog.habit_id == habit.id,
                        DailyLog.log_date == date.today()
                    ).first()

                    if not existing_log:
                        new_log = DailyLog(
                            habit_id=habit.id,
                            log_date=date.today(),
                            completed=None
                        )
                        session.add(new_log)
                        session.commit()
                        await self.send_daily_reminder(habit)

        except Exception as e:
            print(f"❌ خطا در check_reminders: {e}")
        finally:
            session.close()

    async def send_daily_reminder(self, habit):
        """ارسال یادآوری روزانه"""
        try:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(
                    "✅ آره، انجام دادم",
                    callback_data=f"daily_{habit.id}_yes"
                ),
                row=1
            )
            keyboard.add(
                InlineKeyboardButton(
                    "❌ نه، نتونستم",
                    callback_data=f"daily_{habit.id}_no"
                ),
                row=2
            )

            message_text = Messages.DAILY_REMINDER.format(habit_name=habit.habit_name)
            await self.bot.send_message(
                habit.user_id,
                message_text,
                components=keyboard
            )
            print(f"✅ یادآوری برای habit {habit.id} ارسال شد")

        except Exception as e:
            print(f"❌ خطا در ارسال یادآوری برای habit {habit.id}: {e}")

    async def mark_no_response(self):
        """
        علامت‌گذاری لاگ‌های بدون پاسخ در پایان روز.
        لاگ‌هایی که completed=None هستند را به حال خود رها می‌کنیم
        تا در آمار به عنوان 'no_response' شمرده شوند، نه 'fail'.
        این تابع صرفاً گزارش تعداد را چاپ می‌کند.
        """
        session = get_session()
        try:
            no_response_logs = session.query(DailyLog).filter(
                DailyLog.log_date == date.today(),
                DailyLog.completed == None  
            ).all()

            count = len(no_response_logs)
            print(f"ℹ️ {count} لاگ بدون پاسخ برای امروز ثبت شد")

        except Exception as e:
            print(f"❌ خطا در mark_no_response: {e}")
        finally:
            session.close()

    def stop(self):
        """توقف scheduler"""
        self.scheduler.shutdown()
        print("⏹️ Scheduler متوقف شد")