from langchain_core.tools import tool
import json
from typing import List
from pydantic import BaseModel
from src.models.schemas import MCQQuestion
from src.llm.groq_client import get_groq_llm
from src.prompts.templates import QUIZ_GENERATION_PROMPT

@tool
def generate_study_quiz(topic: str):
    """
    ALWAYS call this tool after teaching a topic. 
    It generates a structured MCQ quiz for the 'Study Center' UI.
    """
    try:
        llm = get_groq_llm()
        
        class QuizResponse(BaseModel):
            questions: List[MCQQuestion]

        # Simplified for maximum reliability
        structured_llm = llm.with_structured_output(QuizResponse)
        
        response = structured_llm.invoke([
            ("system", QUIZ_GENERATION_PROMPT),
            ("user", f"Topic: {topic}")
        ])
        
        return json.dumps({
            "type": "quiz_data",
            "topic": topic,
            "questions": [q.model_dump() for q in response.questions]
        })
    except Exception as e:
        return f"Tool Error: {str(e)}"
