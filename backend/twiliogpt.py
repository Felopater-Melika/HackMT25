from dotenv import load_dotenv
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import openai

app = Flask(__name__)

load_dotenv()

# init gpt client
openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# array to store messages
conversation = [{"role": "system", "content": "You are a helpful AI assistant. Keep your answers short"}]

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = "+18445485842"
RECEIVING_NUMBER = "+16156840156"

# init twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/make_call", methods=["GET"])
def make_call():
    twilio_client.calls.create(
        to=RECEIVING_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url="https://56ca-161-45-254-242.ngrok-free.app/answer" # must be updated whenever ngrok is launched
    )
    return f"Calling {RECEIVING_NUMBER}..."

@app.route("/answer", methods=["POST"])
def answer_call():
    response = VoiceResponse()
    
    # if len(conversation) == 1, this is the first TTS of the call, therefore it should greet the user. Otherwise, it should repond appropriately
    if len(conversation) == 1:
        response.say("Hello! This is a machine learning model, how can I help you today?", voice="alice")
    else:
        response.say("Is there anything else I can help you with?")
        
    response.gather(
        input="speech",
        action="/process_speech",
        timeout=5
    )

    return str(response)

@app.route("/process_speech", methods=["POST"])
def process_speech():
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
