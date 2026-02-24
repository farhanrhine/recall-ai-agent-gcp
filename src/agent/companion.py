from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from src.llm.groq_client import get_groq_llm
from src.prompts.templates import STUDY_AGENT_SYSTEM_PROMPT
from src.agent.tools import generate_study_quiz
from src.common.logger import get_logger

class CompanionAgent:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
        self.checkpointer = InMemorySaver()
        self.tools = [generate_study_quiz]
        
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=STUDY_AGENT_SYSTEM_PROMPT,
            checkpointer=self.checkpointer
        )

    def chat(self, message: str, thread_id: str = "study_session"):
        try:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Get count of messages before invocation
            state = self.agent.get_state(config)
            previous_msg_count = len(state.values.get("messages", [])) if state.values else 0

            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config
            )
            
            # Return all new messages
            return response["messages"][previous_msg_count:]
        except Exception as e:
            # If the tool call failed during the agent's turn, we catch it here
            self.logger.error(f"Agent turn failed: {e}")
            raise e
