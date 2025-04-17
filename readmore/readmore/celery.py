import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'readmore.settings')

app = Celery('readmore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
