from langchain.agents import create_agent
from src.llm.groq_client import get_groq_llm
from src.prompts.templates import AGENT_SYSTEM_PROMPT
from src.agent.tools import generate_study_quiz
from src.common.logger import get_logger

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
        self.tools = [generate_study_quiz]
        
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=AGENT_SYSTEM_PROMPT
        )

    def chat(self, messages: list):
        """
        Takes a list of current messages and returns only the new messages 
        generated during this turn.
        """
        # invoke expects a dict with 'messages'
        response = self.agent.invoke(
            {"messages": messages}
        )
        
        # We find how many messages were passed in
        input_count = len(messages)
        
        # Return only the new ones
        return response["messages"][input_count:]
