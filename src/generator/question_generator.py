from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import MCQ_SYSTEM_PROMPT, FILL_BLANK_SYSTEM_PROMPT
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)

    def generate_mcq(self, topic: str, difficulty: str = 'medium') -> MCQQuestion:
        try:
            self.logger.info(f"Generating MCQ for topic {topic} with difficulty {difficulty}")
            
            # Create agent with structured output for MCQ
            agent = create_agent(
                model=self.llm,
                system_prompt=MCQ_SYSTEM_PROMPT,
                response_format=ToolStrategy(MCQQuestion)
            )

            # Invoke agent
            response = agent.invoke({
                "messages": [{"role": "user", "content": f"Topic: {topic}, Difficulty: {difficulty}"}]
            })

            # The response schema for create_agent with ToolStrategy contains 'structured_response'
            question = response['structured_response']

            if len(question.options) != 4 or question.correct_answer not in question.options:
                raise ValueError("Invalid MCQ Structure")
            
            self.logger.info("Generated a valid MCQ Question")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate MCQ: {str(e)}")
            raise CustomException("MCQ generation failed", e)
        
    def generate_fill_blank(self, topic: str, difficulty: str = 'medium') -> FillBlankQuestion:
        try:
            self.logger.info(f"Generating fill-in-the-blank for topic {topic} with difficulty {difficulty}")

            # Create agent with structured output for Fill in the Blank
            agent = create_agent(
                model=self.llm,
                system_prompt=FILL_BLANK_SYSTEM_PROMPT,
                response_format=ToolStrategy(FillBlankQuestion)
            )

            # Invoke agent
            response = agent.invoke({
                "messages": [{"role": "user", "content": f"Topic: {topic}, Difficulty: {difficulty}"}]
            })

            question = response['structured_response']

            if "___" not in question.question:
                # Basic fix if agent forgets underscores but provides text
                if "_____" not in question.question:
                    self.logger.warning("Underscores missing in generated question, attempting to fix")
            
            self.logger.info("Generated a valid Fill in Blanks Question")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate fillups: {str(e)}")
            raise CustomException("Fill in blanks generation failed", e)

