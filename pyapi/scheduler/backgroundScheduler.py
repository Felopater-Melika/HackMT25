from apscheduler.schedulers.background import BackgroundScheduler
import time
import requests
from pydantic import BaseModel


class CallRequest(BaseModel):
    first_name: str
    last_name: str
    follow_up_topics: str
    phone_number: str
    caregiver_number: str
    prescriptions: dict
    bio: str
    hour: str
    minute: str

def bot_request(call_schedule: CallRequest):
    # Call API to schedule call
    url = "http://127.0.0.1:8000/make_call"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=call_schedule.model_dump_json())
    

def schedule_call(call_schedule: CallRequest):
    hour, minute = call_schedule.hour, call_schedule.minute
    
    scheduler = BackgroundScheduler()

    scheduler.add_job(bot_request, 'cron', hour=hour, minute=minute, args=[call_schedule])
    scheduler.start()


dummy_data = CallRequest(
    first_name="John",
    last_name="Doe",
    follow_up_topics="Nephew's piano concert, back pain, medication refills",
    phone_number="+16159240230",
    caregiver_number="drewh6472@gmail.com",
    prescriptions={"levothyroxine": "taken", "ibuprofen": "not", "amlodipine" : "delayed"},
    bio="John is a 65 year old man who loves football. He has diabetes and high blood pressure.",
    hour="4",
    minute="6",
)
schedule_call(dummy_data)

while True:
    time.sleep(1)
