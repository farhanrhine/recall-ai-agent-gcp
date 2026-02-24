from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from src.agent.companion import CompanionAgent
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

# Ensure we use UTF-8 for everything
os.environ["PYTHONIOENCODING"] = "utf-8"

app = FastAPI(title="AI Tutor API")
agent = CompanionAgent()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class QuizRequest(BaseModel):
    messages: List[ChatMessage]

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    langchain_messages = []
    for m in request.messages:
        if m.role == "user":
            langchain_messages.append(HumanMessage(content=m.content))
        else:
            langchain_messages.append(AIMessage(content=m.content))
    
    response = agent.chat(langchain_messages)
    return {"content": response.content}

@app.post("/api/quiz")
async def quiz_endpoint(request: QuizRequest):
    langchain_messages = []
    for m in request.messages:
        if m.role == "user":
            langchain_messages.append(HumanMessage(content=m.content))
        else:
            langchain_messages.append(AIMessage(content=m.content))
    
    quiz_data = agent.generate_quiz_from_history(langchain_messages)
    return quiz_data

@app.get("/", response_class=HTMLResponse)
async def get_index():
    # Explicitly read as UTF-8 for Windows compatibility
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Start on 8080 to avoid common port conflicts
    uvicorn.run(app, host="127.0.0.1", port=8080)
