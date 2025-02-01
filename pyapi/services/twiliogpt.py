#twiliogpt.py
from dotenv import load_dotenv
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import openai


load_dotenv()

# init gpt client
openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# array to store messages
conversation = []

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = "+18445485842"

NGROK_URL = os.environ["NGROK_URL"]

# hardcoded test data
patient_contact_info = "+16155856532"
patient_first_name = "Noah"

# init twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/make_call", methods=["GET"])
def make_call():
    
    print("Placing call")
    
    conversation.clear()
    
    conversation.append({"role": "system", "content": "You are checking in on an elderly patient. Their name is " + patient_first_name + ". Ask to make sure they are feeling healthy and well, and ask whether they've taken their medications today. Keep your answers reasonably short."})
    
    twilio_client.calls.create(
        to=patient_contact_info,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{NGROK_URL}/answer",
        status_callback=f"{NGROK_URL}/call_ended"
    )
    return f"Calling " + str(patient_first_name) + " at " + str(patient_contact_info)

@app.route("/answer", methods=["POST"])
def answer_call():
    
    print("answer")
    
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
        # generate next response from OpenAI
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
        response.say("Sorry, I have experienced a software issue.")
    
    # return to the answer_call function, which will continue the conversation
    response.redirect("/answer")

    return str(response)

@app.route("/call_ended", methods=["GET", "POST"])
def callEnded():
    # Once the call ends, prompt ChatGPT to generate a short summary of the call for the 'response' key of the db
    print("Call ended")
    if len(conversation) > 1:
        conversation.append({"role": "user", "content": "Write a brief summary of that conversation"})
        chatgpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )
        
        print("Call summary: " + chatgpt_response.choices[0].message.content)
    
    return "Summary completed"

if __name__ == "__main__":
    app.run(debug=True, port=5050)
