from fastapi import FastAPI
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WealthPilot Running"}


@app.get("/plan")
def generate_plan():

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = """
    You are an expert financial advisor.

    User:
    Age: 22
    Monthly Income: ₹50000
    Monthly Investment: ₹10000
    Goal: ₹1 Crore by age 40

    Give:
    1. Success probability
    2. Recommended allocation
    3. Risks
    4. Monthly action plan
    """

    response = model.generate_content(prompt)

    return {"plan": response.text}