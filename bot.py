# bot.py
import asyncio
from bale import Bot, Message, CallbackQuery
from config import Config
from database import init_db
from handlers import BotHandlers
from scheduler import ReminderScheduler


bot = Bot(token=Config.BOT_TOKEN)


handlers = BotHandlers(bot)
scheduler = ReminderScheduler(bot)


@bot.event
async def on_ready():
    """زمانی که ربات آماده می‌شود"""
    print(f"✅ ربات {bot.user.username} آماده است!")
    scheduler.start()
    print("✅ Scheduler راه‌اندازی شد")


@bot.event
async def on_message(message: Message):
    """مدیریت پیام‌ها"""

    if message.author.is_bot:
        return

    text = message.text

    if not text:
        return

    if text == "/start" or text == "🏠 صفحه اصلی":
        await handlers.start_handler(message)
    elif text == "/help" or text == "❓ راهنما":
        await handlers.help_handler(message)
    elif text == "/addhabit" or text == "➕ افزودن عادت":
        await handlers.addhabit_handler(message)
    elif text == "/myhabits" or text == "📋 عادت‌های من":
        await handlers.myhabits_handler(message)
    elif text == "/stats" or text == "📊 آمار":
        await handlers.stats_handler(message)
    elif text == "/progress" or text == "📈 پیشرفت":
        await handlers.progress_handler(message)
    elif text == "/change_time" or text == "⏰ تغییر زمان":
        await handlers.change_time_handler(message)
    elif text == "/change_habit" or text == "🔄 تغییر عادت":
        await handlers.change_habit_handler(message)
    elif text == "/motivation" or text == "💪 انگیزه":
        await handlers.motivation_handler(message)
    else:
        await handlers.text_message_handler(message)


@bot.event
async def on_callback(callback: CallbackQuery):
    """مدیریت callbackها"""
    await handlers.callback_handler(callback)


if __name__ == "__main__":
    init_db()
    print("✅ دیتابیس آماده است")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ ربات متوقف شد")
        scheduler.stop()

