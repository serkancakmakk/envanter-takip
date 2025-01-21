from __future__ import absolute_import, unicode_literals

# Bu dosya Celery uygulamasını başlatır
from .celery import app as celery_app

__all__ = ('celery_app',)