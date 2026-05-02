"""
gifs.py
دیکشنری گیف‌ها.
هر کلید با یک دسته‌بندی در get_response_category متناظر است.
مقادیر را با file_id واقعی تلگرام/بله جایگزین کنید.
"""

GIFS: dict[str, list[str]] = {
    # موفقیت — برگشتی بعد از غیبت
    "comeback_praise": [
        "AgACAgQAAxkBAAIBAAFcomeback1AAAA",
        "AgACAgQAAxkBAAIBAAFcomeback2AAAA",
    ],

    # موفقیت — اولین روز / شروع تازه
    "fresh_start": [
        "AgACAgQAAxkBAAIBAAFfresh1AAAA",
        "AgACAgQAAxkBAAIBAAFfresh2AAAA",
    ],

    # موفقیت — روزهای ۲ و ۳ (داری می‌سازی)
    "building_momentum": [
        "AgACAgQAAxkBAAIBAAFmomentum1AAAA",
        "AgACAgQAAxkBAAIBAAFmomentum2AAAA",
    ],

    # موفقیت — روزهای ۴ تا ۶ (آتیشی)
    "on_fire": [
        "AgACAgQAAxkBAAIBAAFfire1AAAA",
        "AgACAgQAAxkBAAIBAAFfire2AAAA",
    ],

    # موفقیت — مایلستون هفتگی (۷، ۱۴، ۲۱، ...)
    "milestone": [
        "AgACAgQAAxkBAAIBAAFmilestone1AAAA",
        "AgACAgQAAxkBAAIBAAFmilestone2AAAA",
    ],

    # موفقیت — نگه‌دارنده استریک (بالای ۷ روز)
    "streak_keeper": [
        "AgACAgQAAxkBAAIBAAFkeeper1AAAA",
        "AgACAgQAAxkBAAIBAAFkeeper2AAAA",
    ],

    # موفقیت — حالت عمومی
    "generic_done": [
        "AgACAgQAAxkBAAIBAAFdone1AAAA",
        "AgACAgQAAxkBAAIBAAFdone2AAAA",
    ],

    # شکست — اولین بار، رابطه خوب
    "gentle_miss": [
        "AgACAgQAAxkBAAIBAAFgentle1AAAA",
        "AgACAgQAAxkBAAIBAAFgentle2AAAA",
    ],

    # شکست — اولین بار، سابقه ضعیف
    "concerned_miss": [
        "AgACAgQAAxkBAAIBAAFconcerned1AAAA",
        "AgACAgQAAxkBAAIBAAFconcerned2AAAA",
    ],

    # شکست — دو روز متوالی
    "two_day_miss": [
        "AgACAgQAAxkBAAIBAAFtwoday1AAAA",
        "AgACAgQAAxkBAAIBAAFtwoday2AAAA",
    ],

    # شکست — سه روز متوالی
    "three_day_miss": [
        "AgACAgQAAxkBAAIBAAFthreeday1AAAA",
        "AgACAgQAAxkBAAIBAAFthreeday2AAAA",
    ],

    # شکست — چهار روز به بالا، رابطه متوسط به بالا
    "disappointed_miss": [
        "AgACAgQAAxkBAAIBAAFdisappointed1AAAA",
        "AgACAgQAAxkBAAIBAAFdisappointed2AAAA",
    ],

    # شکست — چهار روز به بالا، رابطه ضعیف
    "cold_miss": [
        "AgACAgQAAxkBAAIBAAFcold1AAAA",
        "AgACAgQAAxkBAAIBAAFcold2AAAA",
    ],

    # شکست — حالت عمومی
    "generic_miss": [
        "AgACAgQAAxkBAAIBAAFmiss1AAAA",
        "AgACAgQAAxkBAAIBAAFmiss2AAAA",
    ],
}