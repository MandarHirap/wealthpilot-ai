from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from db import (
    goals_collection,
    progress_collection,
    plans_collection,
    recommendations_collection,
    expenses_collection,
    agent_tasks_collection,
    agent_logs_collection,
    health_scores_collection
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


class AgentRequest(BaseModel):
    task: str


@app.get("/")
def root():
    return {
        "status": "WealthPilotAI Agent Running"
    }


@app.post("/create-goal")
def create_goal(data: FinancialGoal):

    goals_collection.insert_one(data.model_dump())

    return {
        "status": "success",
        "message": "Goal saved successfully"
    }


@app.post("/update-progress")
def update_progress(data: ProgressUpdate):

    progress_collection.insert_one(data.model_dump())

    return {
        "status": "success",
        "message": "Progress updated"
    }


@app.post("/plan/{name}")
def generate_plan(name: str):

    goal = goals_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    if not goal:
        return {"error": "Goal not found"}

    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
    You are WealthPilotAI.

    User Goal:
    {goal}

    Generate a detailed financial roadmap.
    """

    response = model.generate_content(prompt)

    plans_collection.insert_one({
        "name": name,
        "plan": response.text
    })

    return {
        "status": "success",
        "plan": response.text
    }


@app.post("/agent/{name}")
def run_agent(name: str, data: AgentRequest):

    goal = goals_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    if not goal:
        return {
            "error": "Goal not found"
        }

    latest_progress = progress_collection.find_one(
        {"name": name},
        sort=[("_id", -1)]
    )

    latest_plan = plans_collection.find_one(
        {"name": name},
        sort=[("_id", -1)]
    )

    previous_recommendations = list(
        recommendations_collection.find(
            {"name": name},
            {"_id": 0}
        )
    )

    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
    You are WealthPilotAI.

    Act as an autonomous financial planning agent.

    Goal:
    {goal}

    Latest Progress:
    {latest_progress}

    Latest Plan:
    {latest_plan}

    Previous Recommendations:
    {previous_recommendations}

    User Task:
    {data.task}

    Perform these steps:

    1. Analyze the user's goal
    2. Analyze current financial progress
    3. Review previous recommendations
    4. Identify risks
    5. Decide the next action
    6. Assign a priority

    Respond EXACTLY in this format:

    Recommendation:
    <recommendation>

    Action:
    <single next action>

    Priority:
    <Low/Medium/High>
    """

    response = model.generate_content(prompt)

    recommendation_text = response.text

    # Save recommendation memory
    recommendations_collection.insert_one({
        "name": name,
        "task": data.task,
        "recommendation": recommendation_text
    })

    # Save agent task
    agent_tasks_collection.insert_one({
        "name": name,
        "source_task": data.task,
        "generated_action": recommendation_text,
        "status": "pending"
    })

    # Save agent log
    agent_logs_collection.insert_one({
        "name": name,
        "event": "agent_execution",
        "task": data.task
    })

    return {
        "status": "success",
        "recommendation": recommendation_text
    }

@app.get("/history/{name}")
def get_history(name: str):

    goals = list(
        goals_collection.find(
            {"name": name},
            {"_id": 0}
        )
    )

    plans = list(
        plans_collection.find(
            {"name": name},
            {"_id": 0}
        )
    )

    progress = list(
        progress_collection.find(
            {"name": name},
            {"_id": 0}
        )
    )

    recommendations = list(
        recommendations_collection.find(
            {"name": name},
            {"_id": 0}
        )
    )

    return {
        "goals": goals,
        "plans": plans,
        "progress": progress,
        "recommendations": recommendations
    }



@app.get("/health-score/{name}")
def health_score(name: str):

    goal = goals_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    progress = progress_collection.find_one(
        {"name": name},
        sort=[("_id", -1)]
    )

    if not goal or not progress:
        return {
            "error": "Data missing"
        }

    score = min(
        int(
            (progress["current_savings"] /
             max(goal["monthly_investment"], 1))
        ),
        100
    )

    health_scores_collection.insert_one({
        "name": name,
        "score": score
    })

    return {
        "name": name,
        "financial_health_score": score
    }