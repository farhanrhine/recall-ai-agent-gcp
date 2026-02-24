from langchain.agents import create_agent
from src.llm.groq_client import get_groq_llm
from src.prompts.templates import AGENT_SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT
from src.models.schemas import MCQQuestion
from typing import List
from pydantic import BaseModel
import json

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
    
    def chat(self, messages: list):
        """General conversational agent."""
        agent = create_agent(
            model=self.llm,
            system_prompt=AGENT_SYSTEM_PROMPT
        )
        response = agent.invoke({"messages": messages})
        return response["messages"][len(messages):]

    def generate_quiz(self, topic: str, num_questions: int, difficulty: str):
        """Structured quiz generator using the latest agentic patterns."""
        
        class QuizResponse(BaseModel):
            questions: List[MCQQuestion]

        # Use structured output for reliability
        structured_llm = self.llm.with_structured_output(QuizResponse)
        
        response = structured_llm.invoke([
            ("system", QUIZ_SYSTEM_PROMPT),
            ("user", f"Generate a {difficulty} quiz with {num_questions} questions about {topic}.")
        ])
        
        return response.questions
