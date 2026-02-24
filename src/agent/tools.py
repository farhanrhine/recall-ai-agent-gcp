from langchain_core.tools import tool
import json
from typing import List
from pydantic import BaseModel
from src.models.schemas import MCQQuestion
from src.llm.groq_client import get_groq_llm

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

    # Use with_structured_output for reliable JSON generation
    structured_llm = llm.with_structured_output(QuizResponse)
    
    try:
        response = structured_llm.invoke([
            ("system", SYSTEM_PROMPT),
            ("user", f"Generate {num_questions} questions about {topic}.")
        ])
        
        return json.dumps([q.model_dump() for q in response.questions])
    except Exception as e:
        return f"Error creating quiz: {str(e)}"
