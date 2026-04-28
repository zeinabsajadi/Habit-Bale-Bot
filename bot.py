# bot.py
import asyncio
from bale import Bot, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, get_session, User, Habit, DailyLog
from messages import Messages
from scheduler import ReminderScheduler
from datetime import datetime, time, date
import os

# توکن ربات
TOKEN = os.getenv('BALE_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

bot = Bot(token=TOKEN)
scheduler = ReminderScheduler(bot)

# حالت‌های مختلف کاربر
user_states = {}

@bot.listen()
async def on_ready():
    """زمانی که ربات آماده می‌شود"""
    print(f"ربات {bot.user.username} آماده است!")
    init_db()
    scheduler.start()

@bot.listen()
async def on_message(message: Message):
    """مدیریت پیام‌های دریافتی"""
    user_id = message.author.user_id
    text = message.content
    
    session = get_session()
    try:
        # بررسی وجود کاربر
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, username=message.author.username)
            session.add(user)
            session.commit()
        
        # دستور /start
        if text == '/start':
            await message.reply(Messages.welcome())
            return
        
        # دستور /help
        if text == '/help':
            await message.reply(Messages.help_message())
            return
        
        # دستور /addhabit
        if text == '/addhabit':
            user_states[user_id] = {'state': 'waiting_habit_name'}
            await message.reply(Messages.ask_habit_name())
            return
        
        # دستور /myhabits
        if text == '/myhabits':
            habits = session.query(Habit).filter(Habit.user_id == user_id).all()
            if not habits:
                await message.reply(Messages.no_habits())
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"{'✅' if h.is_active else '❌'} {h.name}",
                        callback_data=f"habit_{h.id}"
                    )] for h in habits
                ])
                await message.reply(Messages.habits_list(), components=keyboard)
            return
        
        # دستور /stats
        if text == '/stats':
            habits = session.query(Habit).filter(Habit.user_id == user_id).all()
            if not habits:
                await message.reply(Messages.no_habits())
            else:
                stats_text = "📊 آمار عادت‌های شما:\n\n"
                for habit in habits:
                    logs = session.query(DailyLog).filter(
                        DailyLog.habit_id == habit.id,
                        DailyLog.completed == True
                    ).count()
                    total_logs = session.query(DailyLog).filter(
                        DailyLog.habit_id == habit.id
                    ).count()
                    success_rate = (logs / total_logs * 100) if total_logs > 0 else 0
                    stats_text += f"🔹 {habit.name}\n"
                    stats_text += f"   موفق: {logs} روز از {total_logs} روز ({success_rate:.1f}%)\n\n"
                await message.reply(stats_text)
            return
        
        # مدیریت state های کاربر
        if user_id in user_states:
            state = user_states[user_id]['state']
            
            if state == 'waiting_habit_name':
                user_states[user_id]['habit_name'] = text
                user_states[user_id]['state'] = 'waiting_reminder_time'
                await message.reply(Messages.ask_reminder_time())
                return
            
            elif state == 'waiting_reminder_time':
                try:
                    hour, minute = map(int, text.split(':'))
                    reminder_time = time(hour=hour, minute=minute)
                    
                    habit = Habit(
                        user_id=user_id,
                        name=user_states[user_id]['habit_name'],
                        reminder_time=reminder_time,
                        is_active=True
                    )
                    session.add(habit)
                    session.commit()
                    
                    del user_states[user_id]
                    await message.reply(Messages.habit_created(habit.name, reminder_time))
                except ValueError:
                    await message.reply(Messages.invalid_time_format())
                return
        
        # پیام پیش‌فرض
        await message.reply(Messages.unknown_command())
    
    finally:
        session.close()

@bot.listen()
async def on_callback(callback: CallbackQuery):
    """مدیریت callback های دکمه‌ها"""
    user_id = callback.user.user_id
    data = callback.data
    
    session = get_session()
    try:
        # مدیریت پاسخ یادآوری روزانه
        if data.startswith('daily_'):
            parts = data.split('_')
            habit_id = int(parts[1])
            response = parts[2]  # yes یا no
            
            log = session.query(DailyLog).filter(
                DailyLog.habit_id == habit_id,
                DailyLog.log_date == date.today()
            ).first()
            
            if log:
                log.completed = (response == 'yes')
                session.commit()
                
                habit = session.query(Habit).filter(Habit.id == habit_id).first()
                if response == 'yes':
                    await callback.message.edit(Messages.habit_completed(habit.name))
                else:
                    await callback.message.edit(Messages.habit_not_completed(habit.name))
            
            await callback.answer()
            return
        
        # مدیریت نمایش جزئیات عادت
        if data.startswith('habit_'):
            habit_id = int(data.split('_')[1])
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            
            if habit:
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "✅ فعال" if habit.is_active else "❌ غیرفعال",
                            callback_data=f"toggle_{habit_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🗑 حذف عادت",
                            callback_data=f"delete_{habit_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔙 بازگشت",
                            callback_data="back_to_list"
                        )
                    ]
                ])
                
                logs_count = session.query(DailyLog).filter(
                    DailyLog.habit_id == habit_id,
                    DailyLog.completed == True
                ).count()
                
                detail_text = f"📋 {habit.name}\n\n"
                detail_text += f"⏰ زمان یادآوری: {habit.reminder_time.strftime('%H:%M')}\n"
                detail_text += f"📊 روزهای موفق: {logs_count}\n"
                detail_text += f"وضعیت: {'فعال ✅' if habit.is_active else 'غیرفعال ❌'}"
                
                await callback.message.edit(detail_text, components=keyboard)
            
            await callback.answer()
            return
        
        # فعال/غیرفعال کردن عادت
        if data.startswith('toggle_'):
            habit_id = int(data.split('_')[1])
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            
            if habit:
                habit.is_active = not habit.is_active
                session.commit()
                await callback.answer(f"عادت {'فعال' if habit.is_active else 'غیرفعال'} شد")
                
                # به‌روزرسانی پیام
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "✅ فعال" if habit.is_active else "❌ غیرفعال",
                            callback_data=f"toggle_{habit_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🗑 حذف عادت",
                            callback_data=f"delete_{habit_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔙 بازگشت",
                            callback_data="back_to_list"
                        )
                    ]
                ])
                
                logs_count = session.query(DailyLog).filter(
                    DailyLog.habit_id == habit_id,
                    DailyLog.completed == True
                ).count()
                
                detail_text = f"📋 {habit.name}\n\n"
                detail_text += f"⏰ زمان یادآوری: {habit.reminder_time.strftime('%H:%M')}\n"
                detail_text += f"📊 روزهای موفق: {logs_count}\n"
                detail_text += f"وضعیت: {'فعال ✅' if habit.is_active else 'غیرفعال ❌'}"
                
                await callback.message.edit(detail_text, components=keyboard)
            return
        
        # حذف عادت
        if data.startswith('delete_'):
            habit_id = int(data.split('_')[1])
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            
            if habit:
                session.delete(habit)
                session.commit()
                await callback.message.edit("🗑 عادت با موفقیت حذف شد")
                await callback.answer()
            return
        
        # بازگشت به لیست
        if data == 'back_to_list':
            habits = session.query(Habit).filter(Habit.user_id == user_id).all()
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"{'✅' if h.is_active else '❌'} {h.name}",
                    callback_data=f"habit_{h.id}"
                )] for h in habits
            ])
            await callback.message.edit(Messages.habits_list(), components=keyboard)
            await callback.answer()
            return
    
    finally:
        session.close()

if __name__ == '__main__':
    bot.run()
