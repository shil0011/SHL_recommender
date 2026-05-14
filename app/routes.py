from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .agent import SHLAgent

router = APIRouter()
agent = SHLAgent()

class Message(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    messages: List[Message]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatOutput(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/chat", response_model=ChatOutput)
async def chat(input: ChatInput):
    try:
        # Convert Pydantic models to list of dicts for the agent
        messages_dict = [{"role": m.role, "content": m.content} for m in input.messages]
        result = agent.process_message(messages_dict)
        return result
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
