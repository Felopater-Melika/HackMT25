from apscheduler.schedulers.background import BackgroundScheduler
import time
import sqlite3
import requests
import json

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
        ORDER BY call_datetime ASC
    )
    SELECT 
        tc.call_id,
        tc.patient_id,
        tc.call_datetime,
        tc.follow_up,
        GROUP_CONCAT(DISTINCT pr.id) AS prescription_ids,  -- Multiple prescriptions?
        p.id AS patient_id,
        p.first_name,
        p.last_name,
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
    
    dummy_values = {
        "id": 1,
        "patient_id": 1,
        "call_datetime": "2023-10-05 10:00:00",
        "follow_up": "Nephew's piano concert, back pain, medication refills",
        "prescription_ids": "1,2,3",
        "patient_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "caregivers": "Jane Doe",
        "prescription_name": "Aspirin",
        "medication_status": "On Track"
    }
    
    headers = {"Content-Type": "application/json"}
    
    url = "http://localhost:8000/request"
    
    response = requests.post(url, json=json.dumps(dummy_values), headers=headers)
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
