# handlers.py
from bale import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import get_session, User, Habit, DailyLog
from messages import Messages
from utils import get_habit_stats, generate_progress_graph, parse_time, check_consecutive_fails
from datetime import date, datetime
from config import Config

class BotHandlers:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}  # ذخیره وضعیت کاربران
    
    async def start_handler(self, message: Message):
        """هندلر دستور /start"""
        user_id = message.author.user_id
        session = get_session()
        
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=message.author.username
                )
                session.add(user)
                session.commit()
            
            await message.reply(Messages.WELCOME)
            self.user_states[user_id] = {'state': 'waiting_habit_name'}
        finally:
            session.close()
    
    async def help_handler(self, message: Message):
        """هندلر دستور /help"""
        await message.reply(Messages.HELP_MESSAGE)
    
    async def progress_handler(self, message: Message):
        """هندلر دستور /progress"""
        user_id = message.author.user_id
        session = get_session()
        
        try:
            habit = session.query(Habit).filter(
                Habit.user_id == user_id,
                Habit.is_active == True
            ).first()
            
            if not habit:
                await message.reply("هنوز عادتی ثبت نکردی! با /start شروع کن 🚀")
                return
            
            stats = get_habit_stats(habit.id)
            if not stats:
                await message.reply("مشکلی پیش اومد! دوباره تلاش کن.")
                return
            
            progress_text = Messages.PROGRESS_HEADER.format(**stats)
            progress_graph = generate_progress_graph(stats['logs'], stats['start_date'])
            
            await message.reply(progress_text + progress_graph)
        finally:
            session.close()
    
    async def motivation_handler(self, message: Message):
        """هندلر دستور /motivation"""
        motivation = Messages.get_random_motivation()
        await message.reply(motivation)
    
    async def change_time_handler(self, message: Message):
        """هندلر دستور /change_time"""
        user_id = message.author.user_id
        self.user_states[user_id] = {'state': 'waiting_new_time'}
        await message.reply("زمان جدید یادآوری رو بنویس (مثلاً: 08:30):")
    
    async def change_habit_handler(self, message: Message):
        """هندلر دستور /change_habit"""
        user_id = message.author.user_id
        session = get_session()
        
        try:
            habit = session.query(Habit).filter(
                Habit.user_id == user_id,
                Habit.is_active == True
            ).first()
            
            if habit:
                await message.reply(
                    "⚠️ توجه: اگر عادت جدید شروع کنی، پیشرفت فعلیت از دست میره.\n\n"
                    "مطمئنی می‌خوای ادامه بدی؟",
                    components=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("آره، مطمئنم", callback_data="confirm_change_habit"),
                            InlineKeyboardButton("نه، بیخیال", callback_data="cancel_change_habit")
                        ]
                    ])
                )
            else:
                await self.start_handler(message)
        finally:
            session.close()
    
    async def message_handler(self, message: Message):
        """هندلر پیام‌های متنی"""
        user_id = message.author.user_id
        text = message.text
        
        if user_id not in self.user_states:
            await message.reply("لطفاً با /start شروع کن یا از /help برای راهنمایی استفاده کن.")
            return
        
        state = self.user_states[user_id].get('state')
        
        if state == 'waiting_habit_name':
            await self.handle_habit_name(message, text)
        elif state == 'waiting_time':
            await self.handle_time(message, text)
        elif state == 'waiting_new_time':
            await self.handle_new_time(message, text)
    
    async def handle_habit_name(self, message: Message, habit_name: str):
        """پردازش نام عادت"""
        user_id = message.author.user_id
        self.user_states[user_id] = {
            'state': 'waiting_time',
            'habit_name': habit_name
        }
        await message.reply(Messages.HABIT_RECEIVED.format(habit_name=habit_name))
    
    async def handle_time(self, message: Message, time_str: str):
        """پردازش زمان یادآوری"""
        user_id = message.author.user_id
        reminder_time = parse_time(time_str)
        
        if not reminder_time:
            await message.reply("فرمت زمان اشتباهه! لطفاً به این شکل بنویس: HH:MM\nمثلاً: 08:30")
            return
        
        habit_name = self.user_states[user_id].get('habit_name')
        session = get_session()
        
        try:
            # غیرفعال کردن عادت‌های قبلی
            old_habits = session.query(Habit).filter(
                Habit.user_id == user_id,
                Habit.is_active == True
            ).all()
            for old_habit in old_habits:
                old_habit.is_active = False
            
            # ایجاد عادت جدید
            new_habit = Habit(
                user_id=user_id,
                habit_name=habit_name,
                reminder_time=reminder_time,
                start_date=date.today()
            )
            session.add(new_habit)
            session.commit()
            
            await message.reply(Messages.HABIT_CONFIRMED.format(
                habit_name=habit_name,
                reminder_time=reminder_time.strftime("%H:%M")
            ))
            
            del self.user_states[user_id]
        finally:
            session.close()
    
    async def handle_new_time(self, message: Message, time_str: str):
        """پردازش تغییر زمان"""
        user_id = message.author.user_id
        reminder_time = parse_time(time_str)
        
        if not reminder_time:
            await message.reply("فرمت زمان اشتباهه! لطفاً به این شکل بنویس: HH:MM\nمثلاً: 08:30")
            return
        
        session = get_session()
        try:
            habit = session.query(Habit).filter(
                Habit.user_id == user_id,
                Habit.is_active == True
            ).first()
            
            if habit:
                habit.reminder_time = reminder_time
                session.commit()
                await message.reply(f"زمان یادآوری به {reminder_time.strftime('%H:%M')} تغییر کرد! ✅")
            else:
                await message.reply("عادت فعالی پیدا نشد!")
            
            if user_id in self.user_states:
                del self.user_states[user_id]
        finally:
            session.close()
    
    async def callback_handler(self, callback: CallbackQuery):
        """هندلر callback های inline keyboard"""
        user_id = callback.user.user_id
        data = callback.data
        
        if data.startswith("daily_"):
            await self.handle_daily_response(callback)
        elif data == "confirm_change_habit":
            await self.handle_confirm_change_habit(callback)
        elif data == "cancel_change_habit":
            await callback.message.reply("باشه، ادامه میدیم! 💪")
    
    async def handle_daily_response(self, callback: CallbackQuery):
        """پردازش پاسخ روزانه"""
        user_id = callback.user.user_id
        data = callback.data
        habit_id = int(data.split("_")[1])
        completed = data.split("_")[2] == "yes"
        
        session = get_session()
        try:
            log = session.query(DailyLog).filter(
                DailyLog.habit_id == habit_id,
                DailyLog.log_date == date.today()
            ).first()
            
            if log:
                log.completed = completed
                log.responded_at = datetime.now()
            else:
                log = DailyLog(
                    habit_id=habit_id,
                    log_date=date.today(),
                    completed=completed,
                    responded_at=datetime.now()
                )
                session.add(log)
            
            session.commit()
            
            if completed:
                response = Messages.get_random_success()
                
                # بررسی استریک
                current_streak, _ = calculate_streak(habit_id)
                if current_streak in Config.STREAK_MILESTONES:
                    response += "\n\n" + Messages.STREAK_MESSAGES[current_streak]
            else:
                response = Messages.get_random_fail()
                
                # بررسی شکست‌های متوالی
                if check_consecutive_fails(habit_id, 3):
                    response += "\n\n" + Messages.MULTIPLE_FAIL_WARNING
            
            await callback.message.reply(response)
        finally:
            session.close()
    
    async def handle_confirm_change_habit(self, callback: CallbackQuery):
        """تایید تغییر عادت"""
        user_id = callback.user.user_id
        session = get_session()
        
        try:
            habit = session.query(Habit).filter(
                Habit.user_id == user_id,
                Habit.is_active == True
            ).first()
            
            if habit:
                habit.is_active = False
                session.commit()
            
            await callback.message.reply(Messages.WELCOME)
            self.user_states[user_id] = {'state': 'waiting_habit_name'}
        finally:
            session.close()

def calculate_streak(habit_id):
    """محاسبه استریک (تابع کمکی برای handlers)"""
    from utils import calculate_streak as calc_streak
    return calc_streak(habit_id)
