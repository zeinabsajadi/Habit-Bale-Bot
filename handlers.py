# handlers.py
from bale import Bot, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, MenuKeyboardMarkup, MenuKeyboardButton
from database import get_session, User, Habit, DailyLog
from messages import Messages
from utils import parse_time, get_habit_stats, check_consecutive_fails, generate_progress_graph
from datetime import date, datetime
from config import Config
import random


class BotHandlers:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}

    def get_main_menu_keyboard(self):
        """ایجاد منوی اصلی ربات"""
        keyboard = MenuKeyboardMarkup()
    
    # اضافه کردن هر دکمه به صورت جداگانه با مشخص کردن ردیف
        keyboard.add(MenuKeyboardButton("➕ افزودن عادت"), row=0)
        keyboard.add(MenuKeyboardButton("📋 عادت‌های من"), row=0)
        keyboard.add(MenuKeyboardButton("📊 آمار"), row=1)
        keyboard.add(MenuKeyboardButton("📈 پیشرفت"), row=1)
        keyboard.add(MenuKeyboardButton("⏰ تغییر زمان"), row=2)
        keyboard.add(MenuKeyboardButton("🔄 تغییر عادت"), row=2)
        keyboard.add(MenuKeyboardButton("💪 انگیزه"), row=3)
        keyboard.add(MenuKeyboardButton("❓ راهنما"), row=3)
        keyboard.add(MenuKeyboardButton("🏠 صفحه اصلی"), row=4)
    
        return keyboard

    async def start_handler(self, message: Message):
        session = get_session()
        try:
            user = session.query(User).filter(
                User.user_id == message.author.user_id
            ).first()
            if not user:
                user = User(user_id=message.author.user_id)
                session.add(user)
                session.commit()

            self.user_states[message.author.user_id] = {'step': 'waiting_for_habit'}
            await message.reply(Messages.WELCOME, components=self.get_main_menu_keyboard())
        except Exception as e:
            print(f"❌ خطا در start_handler: {e}")
        finally:
            session.close()

    async def help_handler(self, message: Message):
        await message.reply(Messages.HELP, components=self.get_main_menu_keyboard())

    async def addhabit_handler(self, message: Message):
        self.user_states[message.author.user_id] = {'step': 'waiting_for_habit'}
        await message.reply(Messages.GET_HABIT_NAME, components=self.get_main_menu_keyboard())

    async def myhabits_handler(self, message: Message):
        session = get_session()
        try:
            habits = session.query(Habit).filter(
                Habit.user_id == message.author.user_id,
                Habit.is_active == True
            ).all()

            if not habits:
                await message.reply(
                    "❌ شما هیچ عادت فعالی ندارید.\n\n"
                    "برای اضافه کردن عادت جدید از دستور /addhabit استفاده کنید.",
                    components=self.get_main_menu_keyboard()
                )
                return

            text = "📋 عادت‌های فعال شما:\n\n"
            for i, habit in enumerate(habits, 1):
                text += f"{i}. {habit.habit_name}\n"
                text += f"   ⏰ زمان یادآوری: {habit.reminder_time.strftime('%H:%M')}\n"
                text += f"   📅 تاریخ شروع: {habit.start_date.strftime('%Y/%m/%d')}\n\n"

            await message.reply(text, components=self.get_main_menu_keyboard())
        except Exception as e:
            print(f"❌ خطا در myhabits_handler: {e}")
        finally:
            session.close()

    async def stats_handler(self, message: Message):
        session = get_session()
        try:
            habits = session.query(Habit).filter(
                Habit.user_id == message.author.user_id,
                Habit.is_active == True
            ).all()

            if not habits:
                await message.reply("❌ شما هیچ عادت فعالی ندارید.", components=self.get_main_menu_keyboard())
                return

            text = "📊 آمار عادت‌های شما:\n\n"
            for habit in habits:
                stats = get_habit_stats(habit.id)
                if not stats:
                    continue
                text += f"🎯 {habit.habit_name}\n"
                text += f"✅ روزهای موفق: {stats['success_count']}\n"
                text += f"❌ روزهای ناموفق: {stats['fail_count']}\n"
                text += f"⏸️ بدون پاسخ: {stats['no_response_count']}\n"
                text += f"📈 درصد موفقیت: {stats['success_rate']}%\n"
                text += f"🔥 استریک فعلی: {stats['current_streak']} روز\n"
                text += f"🏆 بهترین استریک: {stats['best_streak']} روز\n\n"

            await message.reply(text, components=self.get_main_menu_keyboard())
        except Exception as e:
            print(f"❌ خطا در stats_handler: {e}")
        finally:
            session.close()

    async def progress_handler(self, message: Message):
        session = get_session()
        try:
            habits = session.query(Habit).filter(
                Habit.user_id == message.author.user_id,
                Habit.is_active == True
            ).all()

            if not habits:
                await message.reply("❌ شما هیچ عادت فعالی ندارید.", components=self.get_main_menu_keyboard())
                return

            for habit in habits:
                stats = get_habit_stats(habit.id)
                if not stats:
                    continue

                text = Messages.PROGRESS_HEADER.format(
                    habit_name=habit.habit_name,
                    current_day=stats['current_day'],
                    success_count=stats['success_count'],
                    fail_count=stats['fail_count'],
                    no_response_count=stats['no_response_count'],
                    success_rate=stats['success_rate'],
                    current_streak=stats['current_streak'],
                    best_streak=stats['best_streak']
                )

                logs = session.query(DailyLog).filter(
                    DailyLog.habit_id == habit.id
                ).order_by(DailyLog.log_date).all()

                graph = generate_progress_graph(logs, habit.start_date)
                text += graph

                failure_summary = generate_failure_reason_summary(logs)
                if failure_summary:
                    text += f"\n\n{failure_summary}"

                await message.reply(text, components=self.get_main_menu_keyboard())

        except Exception as e:
            print(f"❌ خطا در progress_handler: {e}")
        finally:
            session.close()

    async def change_time_handler(self, message: Message):
        self.user_states[message.author.user_id] = {'step': 'waiting_for_new_time'}
        await message.reply(
            "⏰ لطفاً زمان جدید یادآوری را به فرمت HH:MM وارد کنید (مثال: 08:30)",
            components=self.get_main_menu_keyboard()
        )

    async def change_habit_handler(self, message: Message):
        session = get_session()
        try:
            habits = session.query(Habit).filter(
                Habit.user_id == message.author.user_id,
                Habit.is_active == True
            ).all()

            if not habits:
                await message.reply("❌ شما هیچ عادت فعالی ندارید.", components=self.get_main_menu_keyboard())
                return

            if len(habits) == 1:
                self.user_states[message.author.user_id] = {
                    'step': 'confirm_change_habit',
                    'old_habit_id': habits[0].id
                }

                keyboard = InlineKeyboardMarkup()
                keyboard.add(
                    InlineKeyboardButton(
                        "✅ بله، مطمئنم",
                        callback_data=f"confirm_change_{habits[0].id}"
                    ),
                    row=1
                )
                keyboard.add(
                    InlineKeyboardButton("❌ انصراف", callback_data="cancel_change"),
                    row=2
                )

                await message.reply(
                    f"⚠️ شما در حال حاضر روی عادت «{habits[0].habit_name}» کار می‌کنید.\n\n"
                    "آیا مطمئن هستید که می‌خواهید این عادت را غیرفعال کرده و عادت جدیدی شروع کنید؟",
                    components=keyboard
                )
            else:
                text = "📋 عادت‌های فعال شما:\n\n"
                for i, habit in enumerate(habits, 1):
                    text += f"{i}. {habit.habit_name}\n"
                text += "\n🔢 شماره عادتی که می‌خواهید غیرفعال کنید را وارد کنید:"

                self.user_states[message.author.user_id] = {
                    'step': 'select_habit_to_change',
                    'habits': [h.id for h in habits]
                }
                await message.reply(text, components=self.get_main_menu_keyboard())
        except Exception as e:
            print(f"❌ خطا در change_habit_handler: {e}")
        finally:
            session.close()

    async def motivation_handler(self, message: Message):
        quote = Messages.get_random_motivation()
        await message.reply(f"💪 {quote}", components=self.get_main_menu_keyboard())

    async def text_message_handler(self, message: Message):
        user_id = message.author.user_id

        if not message.text:
            return

        if user_id not in self.user_states:
            return

        state = self.user_states[user_id]
        session = get_session()

        try:
            if state['step'] == 'waiting_for_habit':
                state['habit_name'] = message.text.strip()
                state['step'] = 'waiting_for_time'
                await message.reply(Messages.GET_REMINDER_TIME, components=self.get_main_menu_keyboard())

            elif state['step'] == 'waiting_for_time':
                reminder_time = parse_time(message.text)
                if not reminder_time:
                    await message.reply(
                        "❌ فرمت زمان نادرست است. لطفاً به فرمت HH:MM وارد کنید (مثال: 08:30)",
                        components=self.get_main_menu_keyboard()
                    )
                    return

                old_habits = session.query(Habit).filter(
                    Habit.user_id == user_id,
                    Habit.is_active == True
                ).all()
                for old_habit in old_habits:
                    old_habit.is_active = False

                new_habit = Habit(
                    user_id=user_id,
                    habit_name=state['habit_name'],
                    reminder_time=reminder_time,
                    start_date=date.today()
                )
                session.add(new_habit)
                session.commit()

                await message.reply(
                    Messages.HABIT_CONFIRMED.format(
                        habit_name=state['habit_name'],
                        reminder_time=reminder_time.strftime('%H:%M')
                    ),
                    components=self.get_main_menu_keyboard()
                )
                del self.user_states[user_id]

            elif state['step'] == 'waiting_for_new_time':
                new_time = parse_time(message.text)
                if not new_time:
                    await message.reply(
                        "❌ فرمت زمان نادرست است. لطفاً به فرمت HH:MM وارد کنید (مثال: 08:30)",
                        components=self.get_main_menu_keyboard()
                    )
                    return

                habits = session.query(Habit).filter(
                    Habit.user_id == user_id,
                    Habit.is_active == True
                ).all()
                for habit in habits:
                    habit.reminder_time = new_time

                session.commit()
                await message.reply(
                    f"✅ زمان یادآوری به {new_time.strftime('%H:%M')} تغییر یافت.",
                    components=self.get_main_menu_keyboard()
                )
                del self.user_states[user_id]

            elif state['step'] == 'select_habit_to_change':
                try:
                    index = int(message.text.strip()) - 1
                    if 0 <= index < len(state['habits']):
                        habit_id = state['habits'][index]
                        habit = session.query(Habit).filter(
                            Habit.id == habit_id
                        ).first()

                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(
                            InlineKeyboardButton(
                                "✅ بله، مطمئنم",
                                callback_data=f"confirm_change_{habit_id}"
                            ),
                            row=1
                        )
                        keyboard.add(
                            InlineKeyboardButton(
                                "❌ انصراف",
                                callback_data="cancel_change"
                            ),
                            row=2
                        )

                        state['step'] = 'confirm_change_habit'
                        state['old_habit_id'] = habit_id

                        await message.reply(
                            f"⚠️ آیا مطمئن هستید که می‌خواهید عادت «{habit.habit_name}» را غیرفعال کنید؟",
                            components=keyboard
                        )
                    else:
                        await message.reply("❌ شماره نامعتبر است.", components=self.get_main_menu_keyboard())
                except ValueError:
                    await message.reply("❌ لطفاً یک عدد وارد کنید.", components=self.get_main_menu_keyboard())

        except Exception as e:
            print(f"❌ خطا در text_message_handler: {e}")
        finally:
            session.close()

    async def send_failure_reason_menu(self, user_id: int, habit_id: int):
        """ارسال منوی دلایل عدم انجام عادت"""
        try:
            keyboard = InlineKeyboardMarkup()

            reason_items = list(Messages.FAILURE_REASONS.items())
            for i, (reason_key, reason_label) in enumerate(reason_items):
                row_num = i + 1
                keyboard.add(
                    InlineKeyboardButton(
                        reason_label,
                        callback_data=f"reason_{habit_id}_{reason_key}"
                    ),
                    row=row_num
                )

            keyboard.add(
                InlineKeyboardButton(
                    "⏭️ رد کردن",
                    callback_data=f"reason_{habit_id}_skip"
                ),
                row=len(reason_items) + 1
            )

            await self.bot.send_message(
                user_id,
                Messages.SELECT_FAILURE_REASON,
                components=keyboard
            )
        except Exception as e:
            print(f"❌ خطا در send_failure_reason_menu: {e}")

    async def callback_handler(self, callback: CallbackQuery):
        data = callback.data
        try:
            user_id = callback.author.user_id
        except AttributeError:
            try:
                user_id = callback.user.user_id
            except AttributeError:
                print("❌ خطا در callback_handler: نمی‌توان user_id را استخراج کرد")
                return

        session = get_session()

        try:
            if data.startswith("daily_"):
                parts = data.split("_")
                habit_id = int(parts[1])
                response = parts[2]

                log = session.query(DailyLog).filter(
                    DailyLog.habit_id == habit_id,
                    DailyLog.log_date == date.today()
                ).first()

                if not log:
                    await self.bot.send_message(user_id, "❌ لاگ امروز یافت نشد.")
                    return

                if log.completed is not None:
                    await self.bot.send_message(user_id, "✅ قبلاً پاسخ این روز رو ثبت کردی.")
                    return

                log.completed = (response == "yes")
                log.responded_at = datetime.now()
                session.commit()

                if response == "yes":
                    stats = get_habit_stats(habit_id)
                    reply = Messages.get_random_success()

                    if stats and stats['current_streak'] in Messages.STREAK_MESSAGES:
                        reply += f"\n\n{Messages.STREAK_MESSAGES[stats['current_streak']]}"

                    await self.bot.send_message(user_id, reply)

                else:
                    consecutive_fails = check_consecutive_fails(habit_id)
                    reply = Messages.get_random_fail()

                    if consecutive_fails:
                        reply += f"\n\n{Messages.MULTIPLE_FAIL_WARNING}"

                    await self.bot.send_message(user_id, reply)
                    await self.send_failure_reason_menu(user_id, habit_id)

            elif data.startswith("reason_"):
                parts = data.split("_", 2)
                if len(parts) < 3:
                    return

                habit_id = int(parts[1])
                reason_key = parts[2]

                if reason_key == "skip":
                    await self.bot.send_message(
                        user_id,
                        "باشه! فردا دوباره تلاش کن 💪"
                    )
                    return

                log = session.query(DailyLog).filter(
                    DailyLog.habit_id == habit_id,
                    DailyLog.log_date == date.today()
                ).first()

                if log and log.completed is False:
                    log.failure_reason = reason_key
                    session.commit()

                responses = Messages.FAILURE_REASON_RESPONSES.get(reason_key, [])
                if responses:
                    reply = random.choice(responses)
                    reply += Messages.FAILURE_REASON_FOOTER
                    await self.bot.send_message(user_id, reply)
                else:
                    await self.bot.send_message(
                        user_id,
                        f"ممنون که دلیلت رو گفتی 💙{Messages.FAILURE_REASON_FOOTER}"
                    )

            elif data.startswith("confirm_change_"):
                habit_id = int(data.replace("confirm_change_", ""))

                habit = session.query(Habit).filter(
                    Habit.id == habit_id
                ).first()

                if habit:
                    habit.is_active = False
                    session.commit()
                    await self.bot.send_message(
                        user_id,
                        Messages.habit_toggled(habit.habit_name, False),
                        components=self.get_main_menu_keyboard()
                    )
                    await self.bot.send_message(
                        user_id,
                        "✅ حالا می‌تونید با دستور /addhabit عادت جدیدتون رو شروع کنید.",
                        components=self.get_main_menu_keyboard()
                    )

                if user_id in self.user_states:
                    del self.user_states[user_id]

            elif data == "cancel_change":
                await self.bot.send_message(
                    user_id,
                    "❌ عملیات لغو شد.",
                    components=self.get_main_menu_keyboard()
                )
                if user_id in self.user_states:
                    del self.user_states[user_id]

        except Exception as e:
            print(f"❌ خطا در callback_handler: {e}")
        finally:
            session.close()


def generate_failure_reason_summary(logs) -> str:
    """
    تولید خلاصه دلایل عدم انجام عادت از لاگ‌ها.
    فقط لاگ‌هایی که failure_reason دارند در نظر گرفته می‌شوند.
    """
    reason_counts = {}
    for log in logs:
        if log.completed is False and log.failure_reason:
            reason = log.failure_reason
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    if not reason_counts:
        return ""

    sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)

    summary = "📋 دلایل عدم انجام عادت:\n"
    for reason_key, count in sorted_reasons:
        label = Messages.FAILURE_REASONS.get(reason_key, reason_key)
        summary += f"  • {label}: {count} بار\n"

    return summary
