"""
gif_sender.py
انتخاب دسته‌بندی مناسب براساس آمار کاربر و ارسال گیف متناظر.
"""

import random
from user_stats import UserStats
from gifs import GIFS


def get_response_category(user: UserStats) -> str:
    """
    براساس آمار کاربر، دسته‌بندی مناسب برای گیف را برمی‌گرداند.
    دقیقاً همان الگوریتم تعریف‌شده در مستندات پروژه.
    """
    s = user.streak
    ms = user.miss_streak
    r = user.relationship
    lc = user.last_comeback

    # --- موفقیت ---
    if user.did_today:
        if lc:
            return "comeback_praise"
        if s == 1:
            return "fresh_start"
        if s in (2, 3):
            return "building_momentum"
        if 4 <= s <= 6:
            return "on_fire"
        if s >= 7 and s % 7 == 0:
            return "milestone"
        if s >= 7:
            return "streak_keeper"
        return "generic_done"

    # --- شکست ---
    else:
        if ms == 1 and r >= 70:
            return "gentle_miss"
        if ms == 1 and r < 70:
            return "concerned_miss"
        if ms == 2:
            return "two_day_miss"
        if ms == 3:
            return "three_day_miss"
        if ms >= 4 and r >= 50:
            return "disappointed_miss"
        if ms >= 4 and r < 50:
            return "cold_miss"
        return "generic_miss"


def pick_gif(category: str) -> str | None:
    """
    از لیست گیف‌های یک دسته‌بندی، یکی را تصادفی انتخاب می‌کند.
    اگر دسته‌بندی وجود نداشت یا لیست خالی بود، None برمی‌گرداند.
    """
    gif_list = GIFS.get(category)
    if not gif_list:
        return None
    return random.choice(gif_list)


async def send_response_gif(bot, user_id: int, user_stats: UserStats) -> None:
    """
    گیف مناسب را انتخاب و به عنوان پیام جداگانه برای کاربر ارسال می‌کند.
    در صورت خطا، ربات کرش نمی‌کند — فقط لاگ می‌دهد.

    پارامترها:
        bot        : آبجکت Bot از کتابخانه bale
        user_id    : شناسه کاربر در بله
        user_stats : آبجکت UserStats حاوی آمار محاسبه‌شده
    """
    try:
        category = get_response_category(user_stats)
        gif_id = pick_gif(category)

        if not gif_id:
            print(f"ℹ️ gif_sender: هیچ گیفی برای دسته‌بندی '{category}' پیدا نشد.")
            return

        await bot.send_animation(
            chat_id=user_id,
            animation=gif_id
        )

    except Exception as e:
        # خطا در ارسال گیف نباید روی جریان اصلی ربات تأثیر بگذارد
        print(f"⚠️ gif_sender: خطا در ارسال گیف برای user_id={user_id}: {e}")