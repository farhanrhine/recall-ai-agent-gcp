from src.llm.groq_client import get_groq_llm
from src.prompts.templates import STUDY_AGENT_SYSTEM_PROMPT, QUIZ_GENERATION_PROMPT
from src.models.schemas import MCQQuestion
import json
import re
from langchain_core.messages import SystemMessage

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
    
    def chat(self, messages: list):
        """Pure conversational chat. No tool-calling to avoid 400 errors."""
        # Ensure we are just using the base model for chat
        history = [SystemMessage(content=STUDY_AGENT_SYSTEM_PROMPT)] + messages
        return self.llm.invoke(history)

    def generate_quiz_data(self, topic: str):
        """
        Generates quiz data using raw JSON prompting. 
        This is the most stable way to get results from Groq.
        """
        prompt = f"""{QUIZ_GENERATION_PROMPT}
        Topic: {topic}

        Return ONLY a JSON object with this structure:
        {{
            "questions": [
                {{
                    "question": "Question text?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "Correct Option"
                }}
            ]
        }}
        """
        
        # Invoke without structured_output to avoid tool-use errors
        response = self.llm.invoke(prompt)
        text = response.content

        try:
            # Extract JSON using regex in case of conversational prefix/suffix
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "type": "quiz_data",
                    "topic": topic,
                    "questions": data["questions"]
                }
        except Exception as e:
            # Fallback/Debug
            return {"type": "error", "message": f"Parsing failed: {str(e)}", "raw": text}
