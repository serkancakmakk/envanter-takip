from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

scheduler = None

def sync_ldap_users():
    from .utils import auto_get_all_ldap_users_and_groups  # İçe aktarmayı burada yapın
    auto_get_all_ldap_users_and_groups()
    print("Syncing LDAP users...")

def scheduler_listener(event):
    if event.exception:
        print(f"Job {event.job_id} failed")
    else:
        print(f"Job {event.job_id} completed successfully")

def start_scheduler():
    global scheduler
    if scheduler is None or not scheduler.running:
        scheduler = BackgroundScheduler()
        scheduler.add_job(sync_ldap_users, "cron", hour=1, id="sync-ldap-users-every-10-seconds")
        scheduler.add_listener(scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()
        print("Scheduler started.")
