import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account

# Load from .env
load_dotenv()

# Get the environment variable
service_json = os.getenv("GOOGLE_SERVICE_JSON")

if not service_json:
    raise ValueError("GOOGLE_SERVICE_JSON environment variable not found")

# Parse JSON from the string
service_account_info = json.loads(service_json)

# Now use it to create credentials
credentials = service_account.Credentials.from_service_account_info(service_account_info)
