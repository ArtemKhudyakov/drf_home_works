from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-inactive-users-weekly': {
        'task': 'lms.tasks.check_inactive_users',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Каждый понедельник в 9:00
    },
    'update-course-statistics-daily': {
        'task': 'lms.tasks.update_course_statistics',
        'schedule': crontab(hour=2, minute=0),  # Ежедневно в 2:00
    },
    'send-newsletter-monthly': {
        'task': 'lms.tasks.send_newsletter',
        'schedule': crontab(day_of_month=1, hour=10, minute=0),  # 1-го числа каждого месяца в 10:00
    },
'check-course-updates-hourly': {
        'task': 'lms.tasks.check_lesson_updates',
        'schedule': crontab(minute=0),  # Каждый час
    },

    'send-course-update-notifications': {
        'task': 'lms.tasks.send_course_update_notification',
        'schedule': crontab(hour=9, minute=0),  # Ежедневно в 9:00
    },
}
