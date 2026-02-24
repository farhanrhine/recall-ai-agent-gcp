from src.llm.groq_client import get_groq_llm
from src.prompts.templates import STUDY_AGENT_SYSTEM_PROMPT, QUIZ_GENERATION_PROMPT
from src.models.schemas import MCQQuestion
from typing import List
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
    
    def chat(self, messages: list):
        """Conversational loop without fragile tool-calling."""
        # Add system prompt to the history
        history = [SystemMessage(content=STUDY_AGENT_SYSTEM_PROMPT)] + messages
        response = self.llm.invoke(history)
        return response

    def generate_quiz_data(self, topic: str):
        """Generates structured quiz data reliably using with_structured_output."""
        class QuizResponse(BaseModel):
            questions: List[MCQQuestion]

        structured_llm = self.llm.with_structured_output(QuizResponse)
        
        response = structured_llm.invoke([
            ("system", QUIZ_GENERATION_PROMPT),
            ("user", f"Generate a quiz about: {topic}")
        ])
        
        return {
            "type": "quiz_data",
            "topic": topic,
            "questions": [q.model_dump() for q in response.questions]
        }
