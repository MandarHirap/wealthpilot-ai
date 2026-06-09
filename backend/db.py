from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

# Database
db = client["wealthpilot"]

# Collections
goals_collection = db["goals"]
progress_collection = db["progress"]
plans_collection = db["plans"]

# Test Connection
try:
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")