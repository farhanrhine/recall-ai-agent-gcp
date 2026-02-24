from langchain_core.tools import tool
import json
import os
from typing import List, Optional
from pydantic import BaseModel
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
    
    SYSTEM_PROMPT = f"""You are a technical quiz generator. 
    Generate exactly {num_questions} {difficulty} MCQs about {topic}.
    Each question must have exactly 4 options and one correct_answer.
    """

    class QuizResponse(BaseModel):
        questions: List[MCQQuestion]

    # Use with_structured_output for more reliable JSON generation
    structured_llm = llm.with_structured_output(QuizResponse)
    
    try:
        response = structured_llm.invoke([
            ("system", SYSTEM_PROMPT),
            ("user", f"Generate {num_questions} questions about {topic}.")
        ])
        
        return json.dumps([q.model_dump() for q in response.questions])
    except Exception as e:
        return f"Error creating quiz: {str(e)}"
