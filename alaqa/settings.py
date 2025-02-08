INSTALLED_APPS = [
    # ... existing apps ...
    'django_cron',
]

# Django Cron Settings
CRON_CLASSES = [
    'appointments.cron.AutoCompleteAppointmentsCronJob',
]

# Cron Job Settings
DJANGO_CRON_LOCK_BACKEND = 'django_cron.backends.lock.cache.CacheLock'
DJANGO_CRON_LOCKFILE_PATH = '/tmp'
DJANGO_CRON_CACHE = 'default'

# Number of minutes that a cron job may overlap
DJANGO_CRON_LOCK_TIME = 60 * 5  # 5 minutes

# Email notifications for failed cron jobs
DJANGO_CRON_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DJANGO_CRON_NOTIFY_BACKEND = 'django_cron.backends.post_save.PostSaveNotifier'

# Cron job logging
LOGGING = {
    # ... existing logging config ...
    'loggers': {
        # ... existing loggers ...
        'django_cron': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'appointments.cron': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
} 