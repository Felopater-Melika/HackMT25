from apscheduler.schedulers.background import BackgroundScheduler
import time
import sqlite3
import requests

#init sqlite db 
conn = sqlite3.connect('DB_NAME')
cursor = conn.cursor()


# Pass to server as patient data
def bot_request():
    patient_info = conn.execute(f"""
    WITH todays_calls AS (
        SELECT 
            id AS call_id,
            patient_id,
            call_datetime
        FROM schedule
        WHERE DATE(call_datetime) = DATE('now')
    )
    SELECT 
        tc.call_id,
        tc.patient_id,
        tc.call_datetime,
        GROUP_CONCAT(DISTINCT pr.id) AS prescription_ids,  -- Multiple prescriptions?
        p.id AS patient_id,
        p.first_name,
        p.phone_number,
        p.caregivers,
        pres.name AS prescription_name,
        med.status AS medication_status
    FROM todays_calls AS tc
    JOIN patients AS p ON tc.patient_id = p.id
    JOIN prescriptions AS pr ON tc.patient_id = pr.patient_id
    JOIN medications AS med ON tc.patient_id = med.patient_id
    GROUP BY tc.call_id, p.id, pres.name, med.status;
    """).fetchall()
    
    headers = {"Content-Type": "application/json"}
    data = {
        "patient_info": patient_info
    }
    
    url = "http://localhost:8000/make_call"
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()
    

def get_todays_schedule_info():
    todays_info = cursor.execute("""
    SELECT 
        id,
        patient_id
        call_datetime
    FROM schedule
    WHERE DATE(call_datetime) = DATE('now') LIMIT 1;
    """)
    
    return todays_info.fetchall()

def main():
    scheduler = BackgroundScheduler()
    id, patient_id, call_datetime = get_todays_schedule_info()
    
    hour = call_datetime.hour
    minute = call_datetime.minute

    scheduler.add_job(bot_request, 'cron', hour=hour, minute=minute)
    scheduler.start()

main()

while True:
    time.sleep(1)
