import os
from celery.schedules import crontab
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change_me_parking_v2')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{BASE_DIR / 'parking_db.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
    CELERY_TIMEZONE = 'UTC'
    CELERY_IMPORTS = ('tasks',)

    CELERY_BEAT_SCHEDULE = {
        'daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=18, minute=0),
            'args': ()
        },
        'monthly-reports': {
            'task': 'tasks.schedule_monthly_reports',
            'schedule': crontab(day_of_month=1, hour=0, minute=30),
            'args': ()
        },
    }

    MAIL_SERVER = '127.0.0.1' 
    MAIL_PORT = 1025
    MAIL_DEFAULT_SENDER = ('Parking App', 'admin@parkingapp.com')
    
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    FILE_STORAGE_PATH = '~/Documents/Studies/vehicle_parking_app_23f2003976/downloads'