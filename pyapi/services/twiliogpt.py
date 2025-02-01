# twiliogpt.py
from fastapi import APIRouter, Form, Request, Response
from dotenv import load_dotenv
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import openai

load_dotenv()

router = APIRouter()
# init gpt client
openai.api_key = os.environ["OPENAI_API_KEY"]

# array to store messages
conversation = []

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
# TWILIO_PHONE_NUMBER = "+18445485842"
TWILIO_PHONE_NUMBER = "+19137330309"

# hardcoded test data
patient_contact_info = "+16159240230"
patient_first_name = "Drew"

# init twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@router.get("/make_call")
def make_call():
    print("Placing call")
    
    conversation.clear()
    
    conversation.append({"role": "system", "content": "You are checking in on an elderly patient. Their name is " + patient_first_name + ". Ask to make sure they are feeling healthy and well, and ask whether they've taken their medications today. Keep your answers reasonably short."})
    
    twilio_client.calls.create(
        to=patient_contact_info,
        from_=TWILIO_PHONE_NUMBER,
        url="https://ba00-161-45-254-242.ngrok-free.app/answer", # must be updated whenever ngrok is launched
        status_callback="https://ba00-161-45-254-242.ngrok-free.app/call_ended"
    )
    return f"Calling " + str(patient_first_name) + " at " + str(patient_contact_info)

@router.post("/answer")
async def answer_call(request: Request):
    print("Answering call")
    try:
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
            timeout=1,
            speech_timeout="auto",
            barge_in=True
        )

        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        print("Error in answer_call:", e)
        return Response(content=str(VoiceResponse().say("Sorry, an error occurred.")), media_type="application/xml")

@router.post("/process_speech")
async def process_speech(request: Request):
    print("Processing user input")
    
    response = VoiceResponse()
    try:
        form_data = await request.form()
        speech_result = form_data.get("SpeechResult", "")

        # if "hang up" is included in the speech_result, exit the function/end the call
        if "hang up" in speech_result:
            print("User requested to hang up")
            response.say("Goodbye")
            return Response(content=str(response), media_type="application/xml")
        
        # add user response and print response, as to keep a log of the conversation
        print("User Input:", speech_result)
        conversation.append({"role": "user", "content": speech_result})

        try:
            # generate next response from OpenAI
            chatgpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=conversation
            )

            assistant_reply = chatgpt_response.choices[0].message['content']

            # update conversation and console
            conversation.append({"role": "assistant", "content": assistant_reply})
            print("AI Response:", assistant_reply)

            response.say(assistant_reply)

        except Exception as e:
            print("OpenAI API Error:", e)
            response.say("Sorry, I have experienced a software issue.")
        
        # return to the answer_call function, which will continue the conversation
        response.redirect("/answer")

        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        print("Error in process_speech:", e)
        return Response(content=str(VoiceResponse().say("Sorry, an error occurred.")), media_type="application/xml")

@router.api_route("/call_ended", methods=["GET", "POST"])
async def call_ended(request: Request):
    print("Call ended")
    try:
        # Log the request data for debugging
        form_data = await request.form()
        print("Call ended request data:", form_data)

        # Once the call ends, prompt ChatGPT to generate a short summary of the call for the 'response' key of the db
        if len(conversation) > 1:
            conversation.append({"role": "user", "content": "Write a brief summary of that conversation"})
            chatgpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=conversation
            )
            
            print("Call summary: " + chatgpt_response.choices[0].message['content'])
        
        return "Summary completed"
    except Exception as e:
        print("Error in call_ended:", e)
        return "Error in call_ended"