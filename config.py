# config.py
import os
from dotenv import load_dotenv
load_dotenv()
class Config:

    BOT_TOKEN = os.getenv('BALE_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

    DATABASE_URL = 'sqlite:///habit_tracker.db'

    TIMEZONE = 'Asia/Tehran'

    STREAK_MILESTONES = [3, 7, 14, 21, 30, 40]
    

    TARGET_DAYS = 40

    CONSECUTIVE_FAIL_THRESHOLD = 3
