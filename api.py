from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from src.agent.companion import CompanionAgent
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
from dotenv import load_dotenv

load_dotenv()

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
    # Convert incoming dicts to LangChain message objects
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
    # Convert history for contextual quiz generation
    langchain_messages = []
    for m in request.messages:
        if m.role == "user":
            langchain_messages.append(HumanMessage(content=m.content))
        else:
            langchain_messages.append(AIMessage(content=m.content))
    
    # We'll use the "topic" detection logic here or just pass the whole history
    # For now, let's assume the frontend sends history and we build quiz from it
    quiz_data = agent.generate_quiz_from_history(langchain_messages)
    return quiz_data

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
