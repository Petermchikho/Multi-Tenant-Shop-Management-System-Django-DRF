import os

from celery import Celery

from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-daily-revenue': {
        'task': 'reporting.tasks.update_daily_revenue_task',
        'schedule': crontab(hour=17, minute=22),  
    },
    'summarize-product-sales-every-hour': {
        'task': 'reorting.tasks.update_daily_product_sales',
        'schedule': crontab(minute=0),  # run at the start of every hour
    },
}


app.conf.timezone = 'Africa/Blantyre'

# Running on windows 

# celery -A api worker --loglevel=INFO --pool=solo
# celery -A api.celery_app flower
# celery -A api.celery_app flower --basic_auth=username:password
# storing the data
# pip install django-celery-results
# add in settings as 'django_celery_results',
# make migration
# pip install django-celery-beat
# add in settting as django_celery_beat
# running a celery beat
# celery -A api beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
