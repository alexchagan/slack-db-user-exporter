import csv
import os
from datetime import datetime
from pymongo import MongoClient
from slack_sdk import WebClient
#

MONGO_URI = ""
DB_NAME = ""
COLLECTION_NAME = ""

SLACK_API_TOKEN = ""
SLACK_CHANNEL = ""

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

projection = {"name": 1, "email": 1}
users = collection.find({}, projection)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"user_data_{timestamp}.csv"
csv_path = os.path.join(os.getcwd(), csv_filename)

with open(csv_path, "w", newline="") as csv_file:
    fieldnames = ["_id","name","email"]  
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for user in users:
        writer.writerow(user)

slack_client = WebClient(token=SLACK_API_TOKEN)

try:
    with open(csv_path, "rb") as csv_file:
        response = slack_client.files_upload_v2(
            channels=SLACK_CHANNEL,
            file=csv_file,
            title=csv_filename,
        )
        print("CSV file uploaded to Slack successfully.")
except Exception as e:
    print(f"Error uploading CSV file to Slack: {str(e)}")

os.remove(csv_path)