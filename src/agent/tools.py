from langchain_core.tools import tool
import json
import os
from typing import List, Optional
from src.models.schemas import MCQQuestion, FillBlankQuestion
from src.llm.groq_client import get_groq_llm
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

MEMORY_FILE = "user_profile.json"

@tool
def save_user_detail(detail_key: str, value: str):
    """Save a specific detail about the user (e.g., 'goal', 'stressor', 'hobby', 'expertise')."""
    profile = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                profile = json.load(f)
        except:
            profile = {}
    
    profile[detail_key] = value
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(profile, f, indent=4)
    
    return f"Successfully saved {detail_key}."

@tool
def get_user_profile():
    """Retrieve the entire saved user profile. Use this to personalize quizzes and advice."""
    if not os.path.exists(MEMORY_FILE):
        return "No profile saved yet."
    
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.dumps(json.load(f), indent=2)
    except:
        return "Error reading profile."

@tool
def generate_study_quiz(topic: str, num_questions: int = 5, difficulty: str = "medium"):
    """
    Generate a highly structured MCQ quiz on a specific topic.
    Returns a list of question objects with options and correct answers.
    """
    llm = get_groq_llm()
    
    # Define a focused prompt for the sub-agent
    SYSTEM_PROMPT = f"""You are a professional educational content creator. 
    Your job is to generate a {difficulty} quiz about {topic} with exactly {num_questions} questions.
    Each question must have exactly 4 options.
    """

    # We use a dataclass/BaseModel for the response format
    from pydantic import BaseModel
    class QuizResponse(BaseModel):
        questions: List[MCQQuestion]

    # Create a internal structured agent
    agent = create_agent(
        model=llm,
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(QuizResponse)
    )

    response = agent.invoke({
        "messages": [{"role": "user", "content": f"Generate {num_questions} MCQs about {topic}."}]
    })

    questions = response['structured_response'].questions
    
    # Store questions in session state for the UI to pick up
    # In a real tool, we return data that the main agent can present
    return json.dumps([q.model_dump() for q in questions])
