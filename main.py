import os
import uvicorn
import spacy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from contextlib import asynccontextmanager

def ensure_spacy_model():
    try:
        spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model 'en_core_web_sm'...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

from analytics_system.chatbot import ValorantChatbot

# Global chatbot instance
chatbot_instance: Optional[ValorantChatbot] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot_instance
    print("API: Starting up...")
    ensure_spacy_model()
    print("API: Initializing ValorantChatbot (ML models and data)...")
    try:
        # Pre-load the models here
        chatbot_instance = ValorantChatbot()
        print("API: Chatbot ready.")
    except Exception as e:
        print(f"API ERROR: Failed to initialize chatbot: {str(e)}")
    
    yield
    print("API: Shutting down...")

app = FastAPI(title="ScoutAnt AI API", lifespan=lifespan)

# Add CORS middleware to allow the frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_chatbot():
    if chatbot_instance is None:
        raise HTTPException(status_code=503, detail="AI System is still initializing or failed to start")
    return chatbot_instance

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        chatbot = get_chatbot()
        bot_result = chatbot.handle_query(request.message)
        
        return ChatResponse(
            response=bot_result["response"],
            data=bot_result["data"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    if chatbot_instance is None:
        return {"status": "initializing"}
    return {"status": "healthy"}

if __name__ == "__main__":
    # Increased timeout settings to prevent worker kills during heavy model usage or slow connections
    # Note: reload is False by default here to prevent constant model re-loading during UI development
    print(f"--- Starting ScoutAnt AI Server ---")
    print(f"--- Host: http://localhost:8000 ---")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False, 
        timeout_keep_alive=600,  # 10 minutes
        log_level="info"
    )

