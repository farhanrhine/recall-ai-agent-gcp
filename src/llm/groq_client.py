from langchain.chat_models import init_chat_model
from src.config.settings import settings

def get_groq_llm():
    return init_chat_model(
        model=settings.MODEL_NAME,
        model_provider="groq",
        api_key=settings.GROQ_API_KEY,
        temperature=settings.TEMPERATURE
    )