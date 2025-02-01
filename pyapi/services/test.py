from dotenv import load_dotenv
import os

dotenv_path = os.path.dirname(__file__)
dotenv_path = dotenv_path[:dotenv_path.find('pyapi')] + '.env'

load_dotenv(dotenv_path)

print(os.getenv("TWILIO_ACCOUNT_SID"))