#twiliogpt.py
from fastapi import APIRouter, Form, Request, Response
from loguru import logger
from dotenv import load_dotenv
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import openai
from pydantic import BaseModel
from datetime import datetime


load_dotenv()

logger.add(f"./services/logs/twiliogpt_{datetime.now().strftime('%Y-%m-%d_%H_%M')}.log", rotation="10MB")

router = APIRouter()
# init gpt client
openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# array to store messages
conversation = []

follow_up_topics = ["Nephew's piano concert, back pain, medication refills"]

# "name" : "status"
medications = {
    "levothyroxine": "taken",
    "ibuprofen": "not",
    "amlodipine" : "delayed",
    "trazodone" : "taking later",
    "metformin" : "need refill",
}

medication_updates = {}

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]

NGROK_URL = os.environ["NGROK_URL"]

# hardcoded test data
patient_contact_info = os.environ["PATIENT_PHONE_NUMBER"]
patient_first_name = "John"

# init twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@router.get("/make_call")
def make_call():
    
    logger.info("Placing call")
    
    prompt = f"""
    You are checking in on an elderly patient.
    Their name is {patient_first_name}. Ask to make sure they are feeling healthy and well, 
    and ask whether they've taken their medications today. Keep your answers reasonably short.
    If at any point it seems like they have a serious concern, 
    remimd them they should call their doctor or 911 (say as nine-one-one) for emergencies.
    Do not offer to call emergency services for them.
    Ask them one-by-one about their medications after checking in with the patient's personal life,
    and if they are taking them as prescribed.
    Medications: {medications}
    """
    
    if follow_up_topics:
        prompt += f"""
        Here is a list of follow up topics from the previous phone call.
        Spend some time discussing these briefly to be more personable at the beginning of the call:
        {follow_up_topics}"""
    
    conversation.append({"role": "system", "content": prompt})
    
    twilio_client.calls.create(
        to=patient_contact_info,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{NGROK_URL}/answer",
        status_callback=f"{NGROK_URL}/call_ended"
    )
    return f"Calling " + str(patient_first_name) + " at " + str(patient_contact_info)

@router.post("/answer")
def answer_call():

    logger.info("answer")

    response = VoiceResponse()

    conv_len = len(conversation)
    
    logger.info("Answering call or responding")
    logger.info("Conversation length is "+ str(conv_len))
    logger.info("Patient: " + str(patient_first_name))
    
    # if len(conversation) == 1, this is the first TTS of the call, therefore it should greet the user
    if conv_len == 1:
        response.say("Hi " + str(patient_first_name) + "! This is Blue Buddy calling to check in on you!", voice="alice")
        
    response.gather(
        input="speech",
        action="/process_speech",
        timeout=5,
        speech_timeout="auto",
        barge_in=True
    )
    print(str(response))
    return Response(content=str(response), media_type="application/xml")

class ProcessResponse(BaseModel):
    hang_up: bool
    medication: str
    status: str    

@router.post("/process_speech")
async def process_speech(request: Request):
    logger.info("Processing user input")

    response = VoiceResponse()
    # speech_result is a string and can be used as such
    form_date = await request.form()
    speech_result = form_date.get("SpeechResult")

    logger.warning("Speech Result: " + speech_result)
    
    # add user response and logger.info response, as to keep a log of the conversation
    logger.info("User Input:", speech_result)
    conversation.append({"role": "user", "content": speech_result})
    
    import time
    start_time = time.time()
    
    is_hang_up = False
    
    try:

        prompt = f"""
        Based on the following conversation, determine the following:
        1) if the user explicitly requests to end the call and if it is appropriate to hang up here. 
        Return 'true' or 'false' only.
        2) if the user is asked about the medicaiton they are taking, output which one medication they are 
        referring to and the status (taken/not taking/delayed/taking later/need refill).
        
        Conversation: 
        {conversation}
        """
        gpt_response = openai_client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format=ProcessResponse
        )
        output = gpt_response.choices[0].message.parsed
        is_hang_up = output.hang_up
        
        medication_name = output.medication
        medication_status = output.status
        medication_updates[medication_name] = medication_status
        
        print("GPT response took " + str(time.time() - start_time) + " seconds")
    except Exception as e:   
        print(e)
        is_hang_up = False

    # if "hang up" is included in the speech_result, exit the function/end the call
    if is_hang_up:
        logger.info("User requested to hang up")
        response.say("Goodbye")
        response.hangup()
        # route to call_ended
        response.redirect("/call_ended")

    try:
        # generate next response from OpenAI
        chatgpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )

        assistant_reply = chatgpt_response.choices[0].message.content

        # update conversation and console
        conversation.append({"role": "assistant", "content": assistant_reply})
        logger.info("AI Response:", assistant_reply)

        response.say(assistant_reply)

    except Exception as e:
        logger.info("OpenAI API Error:", e)
        response.say("Sorry, I have experienced a software issue.")

    # return to the answer_call function, which will continue the conversation
    response.redirect("/answer")

    return Response(content=str(response), media_type="application/xml")

class CallLog(BaseModel):
    summary: str
    follow_up_topics: str
    is_emergency: bool
    
@router.api_route("/call_ended", methods=["GET", "POST"])
def call_ended():
    # Once the call ends, prompt ChatGPT to generate a short summary of the call for the 'response' key of the db
    logger.info("Call ended")
    if len(conversation) > 1:
        
        prompt = f"""
        Please briefly summarize the following conversation between a medical assistant and an elderly patient,
        and provide a short comma separated list of follow-up keyword topics that the medical assistant should discuss with the patient
        in their next phone call. If the patient has an emergency concern (extreme pain, suicide, refusal to take medicine,
        falls, heart attack, etc.), please note that as true/false and the primary healthcare provider will be contacted immediately.
        Conversation:
        {conversation}
        """
        
        gpt_response = openai_client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format=CallLog
        )
        
        output = gpt_response.choices[0].message.parsed

        
        logger.info("Call summary: " + output.summary)
        logger.info("Follow-up topics: " + str(output.follow_up_topics))
        logger.info("Is emergency: " + str(output.is_emergency))
        logger.info("Medication updates: " + str(medication_updates))
        
        conversation.clear()
    
    return "Summary completed"
