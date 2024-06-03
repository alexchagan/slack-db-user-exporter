import csv
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from slack_sdk import WebClient

MONGO_URI = os.environ["MONGO_URI"]
DB_NAME = os.environ["DB_NAME"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]
SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

file_format = 'xlsx'

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

today = datetime.now().date()
last_sunday = today - timedelta(days=today.weekday() + 1)
start_timestamp = datetime.combine(last_sunday, datetime.min.time())
end_timestamp = datetime.combine(last_sunday, datetime.max.time())

query = {
    "createdAt": {
        "$gte": start_timestamp,
        "$lte": end_timestamp
    }
}

projection = {"name": 1, "email": 1}
users = collection.find(query, projection)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
target_filename = f"user_data_{timestamp}.{file_format}"
target_path = os.path.join(os.getcwd(), target_filename)

with open(target_path, "w", newline="") as file:
    fieldnames = ["_id","name","email"]  
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for user in users:
        writer.writerow(user)

slack_client = WebClient(token=SLACK_API_TOKEN)

try:
    with open(target_path, "rb") as file:
        response = slack_client.files_upload_v2(
            channels=SLACK_CHANNEL,
            file=file,
            title=target_filename,
        )
        print(f"{file_format} file uploaded to Slack successfully.")
except Exception as e:
    print(f"Error uploading {file_format} file to Slack: {str(e)}")

os.remove(target_path)