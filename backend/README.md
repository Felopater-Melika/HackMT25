# Call Bot Directions

The call bot runs from the Twilio API and OpenAI API. It is a flask server, and requires 4 packages:
- twilio
- openai
- flask
- python_dotenv

You also need to install ngrok and create a free account on their website. You MUST create a ngrok account, then add your ngrok auth-token. The command to set your auth-token is: `ngrok config add-authtoken [your auth token]`. I will put mine in the Discord.

To operate the call bot, both ngrok and the flask server (twiliogpt.py) need to be running at the same time, on the same port (default 5000).

ngrok creates a public domain that receives http requests from Twilio, then forwards those requests to the flask server at localhost:5000

The public domain is hardcoded into the twilio_client.create() function. The 'url' parameter of this function should be '[ngrok domain]/answer', while the 'status_callback' parameter should be '[ngrok domain]/call_status'