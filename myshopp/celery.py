import os
from celery import Celery

# переменная, содержит:название, настройки.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshopp.settings')

app = Celery('myshopp')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
