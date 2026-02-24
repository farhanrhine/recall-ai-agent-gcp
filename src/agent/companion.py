from src.llm.groq_client import get_groq_llm
from src.prompts.templates import STUDY_AGENT_SYSTEM_PROMPT, QUIZ_GENERATION_PROMPT
from src.models.schemas import MCQQuestion
import json
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
    
    def chat(self, messages: list):
        """Conversational chat focused on teaching."""
        history = [SystemMessage(content=STUDY_AGENT_SYSTEM_PROMPT)] + messages
        return self.llm.invoke(history)

    def generate_quiz_from_history(self, history: list):
        """
        Generates a quiz based on what was actually discussed in the chat history.
        Ensures the quiz is relevant and doesn't hallucinate outside the taught context.
        """
        # Convert message objects to a readable string for the LLM
        context_str = ""
        for m in history[-4:]: # Use the last few messages for immediate context
            role = "User" if isinstance(m, HumanMessage) else "Tutor"
            context_str += f"{role}: {m.content}\n"

        prompt = f"""{QUIZ_GENERATION_PROMPT}

        ### CONVERSATION HISTORY:
        {context_str}

        Return ONLY a JSON object:
        {{
            "questions": [
                {{
                    "question": "text",
                    "options": ["...", "...", "...", "..."],
                    "correct_answer": "..."
                }}
            ]
        }}
        """
        
        response = self.llm.invoke(prompt)
        text = response.content

        try:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "type": "quiz_data",
                    "questions": data["questions"]
                }
        except Exception as e:
            return {"type": "error", "message": f"Parsing failed: {str(e)}", "raw": text}
