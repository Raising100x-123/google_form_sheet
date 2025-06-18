import gspread
import os
import json
from google.oauth2.service_account import Credentials
from pymongo import MongoClient
from datetime import datetime

# ✅ MongoDB Setup
MONGO_URI = "mongodb+srv://Ashwanth:qOQZJWXjbi0IFykD@atlascluster.wub5i.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["Chatbot"]
collection = db["leads"]

# ✅ Google Sheets Setup
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ✅ Load Google credentials from local JSON file
with open(r"C:\Users\CMI10\Desktop\raising100x\google_form_sheet\service_account.json") as f:
    service_account_info = json.load(f)

credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(credentials)

# ✅ Open target Google Sheet
spreadsheet = client.open("chatbotnisaa_responses")
sheet = spreadsheet.sheet1

# ✅ Find existing row using session_id
def find_row_by_session_id(session_id):
    records = sheet.get_all_records()
    for idx, record in enumerate(records, start=2):  # start=2 as row 1 = header
        if record.get('session_id') == session_id:
            return idx
    return None

# ✅ Insert or update a row in the Google Sheet
def upsert_google_sheet(doc):
    try:
        session_id = doc.get("session_id", "")
        contact_number = doc.get("contact_number", "")
        email_id = doc.get("email_id", "")
        location = doc.get("location", "")
        name = doc.get("name", "")
        service_interest = doc.get("service_interest", "")
        appointment_date = doc.get("Appointment_date", "")
        appointment_time = doc.get("Appointment_Time", "")
        updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        all_rows = sheet.get_all_records()
        serial_number = len(all_rows) + 1

        row_data = [
            serial_number,
            session_id,
            contact_number,
            email_id,
            location,
            name,
            service_interest,
            appointment_date,
            appointment_time,
            updated_at
        ]

        row_number = find_row_by_session_id(session_id)

        if row_number:
            sheet.update(f'A{row_number}:J{row_number}', [row_data])
            print(f"✅ Updated session_id {session_id} at row {row_number}")
        else:
            sheet.append_row(row_data)
            print(f"✅ Inserted new session_id {session_id}")
    except Exception as e:
        print(f"❌ Google Sheet update failed for session_id {doc.get('session_id', '')}: {e}")

# ✅ Initial Sync (Optional - sync existing records once)
print("📦 Syncing existing MongoDB records to Google Sheet...")
try:
    for doc in collection.find():
        upsert_google_sheet(doc)
    print("✅ Initial sync complete.\n")
except Exception as e:
    print(f"❌ Error during initial sync: {e}")

# ✅ MongoDB Change Stream Listener
print("⏳ Listening for MongoDB Changes (real-time updates)...")

try:
    with collection.watch(full_document='updateLookup') as stream:
        for change in stream:
            if change['operationType'] in ['insert', 'update', 'replace']:
                doc = change['fullDocument']
                upsert_google_sheet(doc)
except Exception as e:
    print(f"❌ Error in change stream listener: {e}")
