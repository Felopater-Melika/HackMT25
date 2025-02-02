from apscheduler.schedulers.background import BackgroundScheduler
import time
import sqlalchemy
import sqlite3

#init sqlite db 
conn = sqlite3.connect('DB_NAME')
cursor = conn.cursor()


def my_daily_task():
    url = "http://localhost:8000/make_call"
    cursor.execute("""
    SELECT 
    patient,
    patient_id,
    phone_number,
    FROM patients;""")
    response = requests.get(url, '''TEMPORARY''')

def get_call_times_from_db():
    cursor.execute("""
    SELECT 
    schedule_time,
    id,
    FROM medication_schedules;""")

def main():
    scheduler = BackgroundScheduler()
    hour, minute = get_call_times_from_db()

    scheduler.add_job(my_daily_task, 'cron', hour=hour, minute=minute)
    scheduler.start()

main()

while True:
    time.sleep(1)
