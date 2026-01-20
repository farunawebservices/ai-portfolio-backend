# 💬 AI Portfolio Assistant

Full-stack conversational AI system featuring Next.js frontend and FastAPI backend powered by Google Gemini API. Provides personalized portfolio Q&A with multi-mode responses, conversation memory, and production logging.

## 🎯 Overview

This project demonstrates **production-grade AI integration** with:

- **Multi-mode responses**: Deep-dive, quick, story, default
- **Conversation memory**: Maintains context across interactions
- **Real-time streaming**: FastAPI backend with async processing
- **Analytics**: Session tracking and conversation logging
- **Full-stack deployment**: Next.js + FastAPI architecture

## 🚀 Live Demo

Coming soon - deploying to Google Cloud Run

## ✨ Features

- ✅ **Google Gemini Integration**: Production API usage with error handling
- ✅ **4 Response Modes**: Automatic mode detection based on query type
- ✅ **Session Persistence**: Conversation memory across page reloads
- ✅ **Real-time Logging**: Analytics dashboard for usage metrics
- ✅ **Responsive UI**: Mobile-friendly chat widget
- ✅ **CORS Configured**: Secure cross-origin requests

## 🏗️ Architecture

Frontend (Next.js) Backend (FastAPI)
┌─────────────────┐ ┌──────────────────┐
│ Chat Widget │───────▶│ /chat endpoint │
│ (React) │ │ (Gemini API) │
└─────────────────┘ └──────────────────┘
│ │
│ ▼
│ ┌──────────────────┐
│ │ Conversation │
│ │ Memory Store │
│ └──────────────────┘
│ │
▼ ▼
┌─────────────────┐ ┌──────────────────┐
│ Session Store │ │ Logging System │
└─────────────────┘ └──────────────────┘


## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18
- Tailwind CSS
- Framer Motion (animations)

**Backend:**
- FastAPI (Python 3.10+)
- Google Gemini API
- Uvicorn (ASGI server)
- Python-dotenv

**Deployment:**
- Frontend: Vercel / Google Cloud Run
- Backend: Google Cloud Run
- Environment: Docker containerized

## 📦 Installation

### Backend Setup

```bash
# Navigate to backend folder
cd gemini-portfolio-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your GOOGLE_API_KEY to .env

# Run backend
uvicorn main:app --reload --port 8000

Frontend Setup
# Navigate to frontend folder
cd my-portfolio-app

# Install dependencies
npm install

# Run development server
npm run dev

Visit: http://localhost:3000

🔍 Usage
Backend API
# POST /chat
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Tell me about your red-teaming project",
        "mode": "deep-dive",
        "session_id": "user123"
    }
)

print(response.json()["response"])

Response Modes
Deep-dive (mode: "deep-dive")

Detailed technical explanations

Code examples and architecture

Use case: Project deep-dives

Quick (mode: "quick")

Concise 2-3 sentence responses

Key facts only

Use case: Quick questions

Story (mode: "story")

Narrative format with personal context

Journey and lessons learned

Use case: "Tell me about yourself"

Default (mode: "default")

Balanced response

Moderate detail

📊 Example Conversations
User: "What's your background in AI safety?"

Assistant (Story Mode):
I started exploring AI safety after building my first Igala-English translator 
and realizing how unpredictable model behavior can be with low-resource languages. 
That led me to red-teaming, where I built a framework to systematically test LLM 
vulnerabilities. Now I focus on making models more transparent and reliable before 
deployment.

User: "Show me code from your interpretability project"

Assistant (Deep-dive Mode):
# Here's how I visualize attention patterns in mBERT:

from interpretability import AttentionAnalyzer
import plotly.graph_objects as go

analyzer = AttentionAnalyzer(model_name="bert-base-multilingual-cased")
attention_map = analyzer.get_attention(
    source_text="Ọma ẹdu la",
    layer=6,
    head=3
)

# Creates interactive heatmap showing token-to-token attention scores
fig = go.Figure(data=go.Heatmap(z=attention_map))
fig.show()

⚠️ Limitations
API Costs: Gemini API has usage limits on free tier

Session Storage: In-memory only; resets on server restart

Scalability: Single-instance deployment; no load balancing

Context Window: Limited to 10 previous messages

Error Handling: Basic retry logic; no exponential backoff

🔒 Security Considerations
✅ API keys stored in environment variables

✅ CORS configured for specific origins

✅ Input validation on all endpoints

❌ No rate limiting (should add for production)

❌ No authentication (public demo)

🔮 Future Work
 Add Redis for persistent session storage

 Implement rate limiting and abuse prevention

 Add user authentication (OAuth)

 Build analytics dashboard

 Support file uploads (PDFs, images)

 Multi-language support

📄 Environment Variables
Backend (.env):
GOOGLE_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
LOG_LEVEL=INFO

Frontend (.env.local):
NEXT_PUBLIC_API_URL=http://localhost:8000

📄 License
MIT License - See LICENSE for details

🙏 Acknowledgments
Google Gemini API team

Next.js and FastAPI communities

Vercel for deployment platform

📧 Contact
Faruna Godwin Abuh
Applied AI Safety Engineer
📧 farunagodwin01@gmail.com
