#twiliogpt.py
from fastapi import APIRouter, Form, Request, Response
from loguru import logger
from dotenv import load_dotenv
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import openai


load_dotenv()

router = APIRouter()
# init gpt client
openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# array to store messages
conversation = []

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
    
    conversation.clear()
    
    conversation.append({"role": "system", "content": "You are checking in on an elderly patient. Their name is " + patient_first_name + ". Ask to make sure they are feeling healthy and well, and ask whether they've taken their medications today. Keep your answers reasonably short."})
    
    twilio_client.calls.create(
        to=patient_contact_info,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{NGROK_URL}/answer", # must be updated whenever ngrok is launched
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

@router.post("/process_speech")
async def process_speech(request: Request):
    logger.info("Processing user input")

    response = VoiceResponse()
    # speech_result is a string and can be used as such
    form_date = await request.form()
    speech_result = form_date.get("SpeechResult")

    logger.warning("Speech Result: " + speech_result)

    # if "hang up" is included in the speech_result, exit the function/end the call
    if "hang up" in speech_result:
        logger.info("User requested to hang up")
        response.say("Goodbye")
        return

    # add user response and logger.info response, as to keep a log of the conversation
    logger.info("User Input:", speech_result)
    conversation.append({"role": "user", "content": speech_result})

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

@router.api_route("/call_ended", methods=["GET", "POST"])
def call_ended():
    # Once the call ends, prompt ChatGPT to generate a short summary of the call for the 'response' key of the db
    logger.info("Call ended")
    if len(conversation) > 1:
        conversation.append({"role": "user", "content": "Write a brief summary of that conversation"})
        chatgpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )
        
        logger.info("Call summary: " + chatgpt_response.choices[0].message.content)
    
    return "Summary completed"
