from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from db import (
    goals_collection,
    progress_collection,
    plans_collection
)
import os
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()


class FinancialGoal(BaseModel):
    name: str
    age: int
    monthly_income: int
    monthly_investment: int
    goal: str

class ProgressUpdate(BaseModel):
    name: str
    current_savings: int

@app.get("/")
def root():
    return {
        "status": "WealthPilotAI Running"
    }


@app.post("/create-goal")
def create_goal(data: FinancialGoal):

    goals_collection.insert_one(data.model_dump())

    return {
        "status": "success",
        "message": "Goal saved successfully"
    }


@app.get("/goal/{name}")
def get_goal(name: str):

    goal = goals_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    if not goal:
        return {
            "status": "error",
            "message": "Goal not found"
        }

    return {
        "status": "success",
        "goal": goal
    }


@app.post("/plan/{name}")
def generate_plan(name: str):

    goal = goals_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    if not goal:
        return {
            "status": "error",
            "message": "Goal not found"
        }

    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
    You are WealthPilotAI, an expert financial planning agent.

    User Details:
    Name: {goal['name']}
    Age: {goal['age']}
    Monthly Income: ₹{goal['monthly_income']}
    Monthly Investment: ₹{goal['monthly_investment']}
    Goal: {goal['goal']}

    Analyze the user's financial goal and provide:

    1. Success Probability
    2. Recommended Investment Allocation
    3. Key Risks
    4. Monthly Action Plan
    5. Specific Steps the user should take immediately

    Keep the response practical and actionable.
    """

    response = model.generate_content(prompt)

    plans_collection.insert_one({
        "name": goal["name"],
        "plan": response.text
    })

    return {
        "status": "success",
        "plan": response.text
    }

@app.post("/update-progress")
def update_progress(data: ProgressUpdate):

    progress_collection.insert_one(
        data.model_dump()
    )

    return {
        "status": "success",
        "message": "Progress updated"
    }


@app.get("/check-status/{name}")
def check_status(name: str):

    goal = goals_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    progress = progress_collection.find_one(
    {"name": name},
    sort=[("_id", -1)]
)
    if not goal:
        return {"error": "Goal not found"}

    if not progress:
        return {"error": "No progress found"}

    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
    User Goal:
    {goal}

    Current Progress:
    {progress}

    Analyze:

    1. Is the user on track?
    2. What risks exist?
    3. What actions should be taken?
    4. How much should the user invest monthly now?
    """

    response = model.generate_content(prompt)

    return {
        "status": "success",
        "analysis": response.text
    }