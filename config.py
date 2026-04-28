# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bale Bot Token
    BOT_TOKEN = os.getenv('BALE_BOT_TOKEN')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///habit_bot.db')
    
    # Settings
    HABIT_DURATION_DAYS = 40
    REMINDER_RETRY_HOURS = 2
    DEFAULT_TIMEZONE = 'Asia/Tehran'
    
    # Streak milestones
    STREAK_MILESTONES = [3, 7, 14, 21, 30, 40]
