import requests
import json

dummy_values = {
    "id": 1,
    "patient_id": 1,
    "call_datetime": "2023-10-05 10:00:00",
    "follow_up_topics": "Nephew's piano concert, back pain, medication refills",
    "prescription_ids": "1,2,3",
    "patient_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+16155856532",
    "caregivers": "Jane Doe",
    "prescription_name": "Aspirin",
    "medication_status": "On Track"
}

headers = {"Content-Type": "application/json"}

url = "http://localhost:8000/request"

response = requests.post(url, json=json.dumps(dummy_values), headers=headers)
print(response.json())