from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from src.llm.groq_client import get_groq_llm
from src.prompts.templates import AGENT_SYSTEM_PROMPT
from src.agent.tools import save_user_detail, get_user_profile, generate_study_quiz
from src.common.logger import get_logger

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
        self.checkpointer = InMemorySaver()
        self.tools = [save_user_detail, get_user_profile, generate_study_quiz]
        
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=AGENT_SYSTEM_PROMPT,
            checkpointer=self.checkpointer
        )

    def chat(self, message: str, thread_id: str = "default_user"):
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get count of messages before invocation
        state = self.agent.get_state(config)
        previous_msg_count = len(state.values.get("messages", [])) if state.values else 0

        response = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config
        )
        
        # Return only the new messages
        return response["messages"][previous_msg_count:]
