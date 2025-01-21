from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import start_scheduler

from django.apps import AppConfig

from django.apps import AppConfig

class InventoryTrackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_track'

    def ready(self):
        # Burada içe aktarma yapın
        from .tasks import start_scheduler
        start_scheduler()