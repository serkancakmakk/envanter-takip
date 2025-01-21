# Dosyanın başına gelecektir
from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

# Django'nun settings modülünü ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')

app = Celery('inventory')

# Celery config ayarlarını Django settings'den al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django uygulamaları içinde Celery görevlerini bul
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
