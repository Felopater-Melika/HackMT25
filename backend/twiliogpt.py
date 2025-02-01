#twiliogpt.py
# test with python twiliogpt.py '{ \"id\": 0, \"caregiver_id\": 0, \"first_name\": \"Noah\", \"last_name\": \"Cagle\", \"date_of_birth\": \"02/19/02\", \"contact_info\": \"+16156840156\", \"created_at\": \"nothing\", \"updated_at\": \"nothing\" }'

from dotenv import load_dotenv
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import openai
import sys
import json

app = Flask(__name__)

load_dotenv()

# init gpt client
openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# array to store messages
conversation = []

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = "+18445485842"
RECEIVING_NUMBER = "+16156840156"

patient_id = ""
caregiver_id = ""
patient_first_name = ""
patient_last_name = ""
patient_date_of_birth = ""
patient_contact_info = ""
patient_created_at = ""
patient_updated_at = ""

# init twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# this function should parse the json and assign its values to variables, but it doesn't seem to do so
def load_params():
    patientJsonParam = sys.argv[1]
    
    patientJsonDict = json.loads(patientJsonParam)
    
    patient_id = patientJsonDict["id"]
    caregiver_id = patientJsonDict["caregiver_id"]
    patient_first_name = patientJsonDict["first_name"]
    patient_last_name = patientJsonDict["last_name"]
    patient_date_of_birth = patientJsonDict["date_of_birth"]
    patient_contact_info = patientJsonDict["contact_info"]
    patient_created_at = patientJsonDict["created_at"]
    patient_updated_at = patientJsonDict["updated_at"]

@app.route("/make_call", methods=["GET"])
def make_call():
    
    print("Placing call")
    
    # reinit params because the load_params function doesnt work :(
    patientJsonParam = sys.argv[1]
    
    patientJsonDict = json.loads(patientJsonParam)
    
    patient_id = patientJsonDict["id"]
    caregiver_id = patientJsonDict["caregiver_id"]
    patient_first_name = patientJsonDict["first_name"]
    patient_last_name = patientJsonDict["last_name"]
    patient_date_of_birth = patientJsonDict["date_of_birth"]
    patient_contact_info = patientJsonDict["contact_info"]
    patient_created_at = patientJsonDict["created_at"]
    patient_updated_at = patientJsonDict["updated_at"]
    
    conversation.append({"role": "system", "content": "You are checking in on an elderly patient. Their name is " + str(patient_first_name) + ". Ask to make sure they are feeling healthy and well, and ask whether they've taken their medications today. Keep your answers reasonably short."})
    
    twilio_client.calls.create(
        to=patient_contact_info,
        from_=TWILIO_PHONE_NUMBER,
        url="https://2a9e-161-45-254-242.ngrok-free.app/answer" # must be updated whenever ngrok is launched
    )
    return f"Calling " + str(patient_first_name) + " at " + str(patient_contact_info)

@app.route("/answer", methods=["POST"])
def answer_call():
    
    # reinit params because the load_params function doesnt work :(
    patientJsonParam = sys.argv[1]
    
    patientJsonDict = json.loads(patientJsonParam)
    
    patient_id = patientJsonDict["id"]
    caregiver_id = patientJsonDict["caregiver_id"]
    patient_first_name = patientJsonDict["first_name"]
    patient_last_name = patientJsonDict["last_name"]
    patient_date_of_birth = patientJsonDict["date_of_birth"]
    patient_contact_info = patientJsonDict["contact_info"]
    patient_created_at = patientJsonDict["created_at"]
    patient_updated_at = patientJsonDict["updated_at"]
    
    response = VoiceResponse()
    
    conv_len = len(conversation)
    
    print("Answering call or responding")
    print("Conversation length is "+ str(conv_len))
    print("Patient: " + str(patient_first_name))
    
    # if len(conversation) == 1, this is the first TTS of the call, therefore it should greet the user
    if conv_len == 1:
        response.say("Hi " + str(patient_first_name) + "! This is Blue Buddy calling to check in on you!", voice="alice")
        
    response.gather(
        input="speech",
        action="/process_speech",
        timeout=5
    )

    return str(response)

@app.route("/process_speech", methods=["POST"])
def process_speech():
    
    print("Processing user input")
    
    response = VoiceResponse()
    # speech_result is a string and can by used as such
    speech_result = request.form.get("SpeechResult", "")
    
    # if "hang up" is included in the speech_result, exit the function/end the call
    if "hang up" in speech_result:
        print("User requested to hang up")
        response.say("Goodbye")
        return
    
    # add user response and print response, as to keep a log of the conversation
    print("User Input:", speech_result)
    conversation.append({"role": "user", "content": speech_result})

    try:
        chatgpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )

        assistant_reply = chatgpt_response.choices[0].message.content

        # update conversation and console
        conversation.append({"role": "assistant", "content": assistant_reply})
        print("AI Response:", assistant_reply)

        response.say(assistant_reply)

    except Exception as e:
        print("OpenAI API Error:", e)
        response.say("Sorry, I am having trouble responding right now.")
    
    # return to the answer_call function, which will continue the conversation
    response.redirect("/answer")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
