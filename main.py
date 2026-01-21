from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import uuid
import re

app = FastAPI(
    title="Gemini Portfolio Q&A",
    description="Interactive AI-powered portfolio assistant with multi-mode responses",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-flash-lite-latest"

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / f"interactions_{datetime.now().strftime('%Y%m%d')}.json"

conversations = {}

PORTFOLIO_CONTEXT = """
I am Faruna Godwin Abuh, an Applied AI Safety Engineer focused on AI safety,
interpretability, and low-resource NLP for African languages.

I build safety-aware AI systems and evaluation tools, with a focus on model behavior, dataset quality, and real-world deployment in underrepresented communities.

You are Godwin's AI Portfolio Assistant. Answer questions about his 7 AI/ML projects:

1. Red-Teaming LLMs for AI Safety - Automated adversarial testing framework for LLM vulnerabilities (prompt injection, jailbreaks). Tests 5+ attack categories with safety scoring. Coming soon to HuggingFace.

2. Igala-English Neural Machine Translation - First publicly available Igala MT system. Fine-tuned mBERT on 3,253 parallel sentences. Real-time bidirectional translation with confidence scoring. Live at: https://huggingface.co/spaces/Faruna01/igala-nmt-translator

3. **Mechanistic Interpretability Analysis** - Deep dive into mBERT attention patterns during Igala translation. Visualizes 12 layers × 12 heads with interactive Plotly heatmaps. Reveals how transformers handle tonal languages. Live at: https://huggingface.co/spaces/Faruna01/igala-mbert-interpretability

4. Igala GPT from Scratch - Decoder-only transformer built from first principles (no pretrained models). Custom BPE tokenizer, multi-head attention implementation. Trained on 268KB Igala corpus. Live at: https://huggingface.co/spaces/Faruna01/igala-gpt-from-scratch

5. Igala Dataset Explorer - 3,253 field-collected Igala-English sentence pairs. First comprehensive Igala NLP dataset. Interactive Streamlit app for researchers. Live at: https://huggingface.co/spaces/Faruna01/igala-streamlit-app-02

6. AI Safety & Calibration - GPT-2 calibration improvements (+15%). Direct Logit Attribution analysis. Selective prediction and abstention methods for reliable AI.

7. AI Portfolio Assistant (this chatbot!) - Full-stack conversational AI with memory, multi-mode responses, and Google Gemini API integration.

Key Achievements:
- First Igala GPT & NMT system ever built
- 3,253 parallel sentences collected (largest Igala corpus)
- Mechanistic interpretability research on low-resource languages
- All projects deployed and publicly accessible

Background:
- Strong believer in AI transparency and community impact
- Focused on underrepresented languages and AI safety
- Passionate about making AI accessible to African communities
"""

class Question(BaseModel):
    question: str
    session_id: Optional[str] = None
    mode: Optional[str] = "auto"  # auto, deep-dive, quick, story

def detect_response_mode(question: str) -> str:
    """Automatically detect appropriate response mode based on question"""
    question_lower = question.lower()
    
    # Deep-dive indicators
    deep_dive_keywords = ['how did', 'explain', 'technical', 'architecture', 'implement', 
                          'design', 'build', 'develop', 'challenge', 'approach']
    if any(keyword in question_lower for keyword in deep_dive_keywords):
        return "deep-dive"
    
    # Quick fact indicators
    quick_keywords = ['what is', 'which', 'when', 'where', 'list', 'name']
    if any(keyword in question_lower for keyword in quick_keywords):
        return "quick"
    
    # Story indicators
    story_keywords = ['why', 'journey', 'background', 'story', 'motivation', 'inspired']
    if any(keyword in question_lower for keyword in story_keywords):
        return "story"
    
    return "default"

def get_mode_instructions(mode: str) -> str:
    """Get prompt instructions for each response mode"""
    modes = {
        "deep-dive": """
Provide a detailed, technical explanation. Include:
- Specific technologies and methodologies
- Technical challenges and solutions
- Architecture decisions and trade-offs
- Code-level insights where relevant
Use technical language appropriate for engineers.
""",
        "quick": """
Provide a concise, factual answer. Use:
- Bullet points for lists
- Direct, brief sentences
- Key facts only, no elaboration
- 2-4 sentences maximum
""",
        "story": """
Provide a personal, narrative-style answer. Include:
- Personal motivations and values
- Journey and decision-making process
- Emotional connection to the work
- Impact on communities
Use first-person storytelling tone.
""",
        "default": """
Provide a balanced, conversational answer.
Be clear, informative, and personable.
Use 3-5 sentences with natural flow.
"""
    }
    return modes.get(mode, modes["default"])

def log_interaction(question: str, answer: str, response_time: float, 
                   session_id: str = None, mode: str = None, error: str = None):
    """Log each interaction to a JSON file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "mode": mode,
        "question": question,
        "answer": answer if not error else None,
        "error": error,
        "response_time_seconds": round(response_time, 2),
        "model": MODEL_NAME
    }
    
    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    
    logs.append(log_entry)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def build_prompt_with_history(question: str, mode: str, session_id: str = None) -> str:
    """Build prompt including conversation history and mode instructions"""
    mode_instruction = get_mode_instructions(mode)
    
    base_prompt = f"""You are an AI assistant answering questions about Faruna Godwin Abuh's portfolio.
Answer in first person (as Faruna).

{mode_instruction}

Context:
{PORTFOLIO_CONTEXT}
"""
    
    if session_id and session_id in conversations:
        history = conversations[session_id]
        if len(history) > 0:
            base_prompt += "\n\nPrevious conversation:\n"
            for msg in history[-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                base_prompt += f"{role}: {msg['content']}\n"
    
    base_prompt += f"\n\nCurrent question:\n{question}"
    return base_prompt

@app.get("/")
def read_root():
    return {
        "message": "Gemini Portfolio Q&A API with Multi-Mode Responses",
        "version": "0.4.0",
        "features": ["conversation_memory", "response_modes", "logging", "analytics"],
        "response_modes": {
            "auto": "Automatically detect best mode",
            "deep-dive": "Detailed technical explanations",
            "quick": "Brief factual answers",
            "story": "Personal narrative style",
            "default": "Balanced conversational"
        },
        "endpoints": {
            "ask": "/ask",
            "stats": "/stats",
            "new_session": "/session/new",
            "get_history": "/session/{session_id}",
            "docs": "/docs"
        }
    }

@app.get("/stats")
def get_stats():
    """Get interaction statistics"""
    if not LOG_FILE.exists():
        return {"total_interactions": 0, "message": "No logs yet"}
    
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
    
    total = len(logs)
    successful = len([l for l in logs if not l.get('error')])
    errors = total - successful
    avg_response_time = sum(l['response_time_seconds'] for l in logs) / total if total > 0 else 0
    
    unique_sessions = len(set(l.get('session_id') for l in logs if l.get('session_id')))
    
    # Mode usage statistics
    mode_counts = {}
    for log in logs:
        mode = log.get('mode', 'unknown')
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
    
    return {
        "total_interactions": total,
        "successful": successful,
        "errors": errors,
        "unique_sessions": unique_sessions,
        "active_conversations": len(conversations),
        "average_response_time_seconds": round(avg_response_time, 2),
        "mode_usage": mode_counts,
        "today": datetime.now().strftime('%Y-%m-%d')
    }

@app.post("/session/new")
def create_session():
    """Create a new conversation session"""
    session_id = str(uuid.uuid4())
    conversations[session_id] = []
    return {
        "session_id": session_id,
        "message": "New conversation session created"
    }

@app.get("/session/{session_id}")
def get_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversations:
        return {"error": "Session not found"}
    
    return {
        "session_id": session_id,
        "message_count": len(conversations[session_id]),
        "history": conversations[session_id]
    }

@app.post("/ask")
def ask_portfolio(q: Question):
    start_time = datetime.now()
    
    try:
        # Create or get session
        session_id = q.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            conversations[session_id] = []
        elif session_id not in conversations:
            conversations[session_id] = []
        
        # Determine response mode
        mode = q.mode
        if mode == "auto":
            mode = detect_response_mode(q.question)
        
        # Build prompt with history and mode
        prompt = build_prompt_with_history(q.question, mode, session_id)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        # Extract answer
        answer = None
        if hasattr(response, 'text'):
            answer = response.text
        elif hasattr(response, 'candidates'):
            answer = response.candidates[0].content.parts[0].text
        else:
            answer = "I couldn't generate a response. Please try again."
        
        # Store in conversation history
        conversations[session_id].append({"role": "user", "content": q.question})
        conversations[session_id].append({"role": "assistant", "content": answer})
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Log the interaction
        log_interaction(q.question, answer, response_time, session_id, mode)
        
        return {
            "answer": answer,
            "response_time": round(response_time, 2),
            "session_id": session_id,
            "mode_used": mode,
            "conversation_length": len(conversations[session_id]) // 2
        }
            
    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)
        
        log_interaction(q.question, None, response_time, session_id, mode, error=error_msg)
        
        return {
            "error": error_msg,
            "response_time": round(response_time, 2)
        }
