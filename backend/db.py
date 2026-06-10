from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load Environment Variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Atlas Connection
client = MongoClient(MONGO_URI)

# WealthPilot AI Agent Database
db = client["wealthpilot"]

# ============================
# AGENT MEMORY COLLECTIONS
# ============================

# User Financial Goals
goals_collection = db["goals"]

# User Progress Updates
progress_collection = db["progress"]

# Generated Financial Plans
plans_collection = db["plans"]

# Agent Recommendations History
recommendations_collection = db["recommendations"]

# User Expenses / Spending Data
expenses_collection = db["expenses"]

# Agent Action Queue
agent_tasks_collection = db["agent_tasks"]

# Agent Activity Logs
agent_logs_collection = db["agent_logs"]

# Financial Health Scores
health_scores_collection = db["health_scores"]

# ============================
# CONNECTION TEST
# ============================

try:
    client.admin.command("ping")

    print("✅ MongoDB Atlas Connected")
    print("✅ WealthPilot Agent Memory Ready")

except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")