# config.py
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    # توکن ربات
    BOT_TOKEN = os.getenv('BALE_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    # تنظیمات پایگاه داده
    DATABASE_URL = 'sqlite:///habit_tracker.db'
    
    # تنظیمات زمان
    TIMEZONE = 'Asia/Tehran'
    
    # نقاط عطف استریک
    STREAK_MILESTONES = [3, 7, 14, 21, 30, 40]
    
    # تعداد روزهای هدف
    TARGET_DAYS = 40
    
    # آستانه هشدار شکست متوالی
    CONSECUTIVE_FAIL_THRESHOLD = 3
