# AI Interview Agent - Multi-Agent Adaptive Interview System

## 📋 Overview

An intelligent AI-powered interview system that conducts adaptive interviews using a multi-agent architecture. The system dynamically adjusts questions based on candidate responses, evaluates answers across multiple dimensions, and generates comprehensive reports.

### Key Features

- **🎯 Adaptive Question Generation**: Questions evolve based on candidate performance using RAG (Retrieval-Augmented Generation)
- **🤖 Multi-Agent Architecture**: Coordinated agents for questions, evaluation, context management, and analytics
- **📊 Real-time Evaluation**: Immediate feedback on multiple dimensions (technical, communication, problem-solving, cultural fit)
- **🔄 State Machine Interview Flow**: Structured phases from introduction to closing
- **📈 Comprehensive Analytics**: Detailed reports with scores, insights, and hiring recommendations
- **💾 Persistent Storage**: SQLite database with vector store for semantic search

## 🏗️ Unique Architecture

### Multi-Agent System

The system employs a coordinated multi-agent architecture:

1. **Orchestrator Agent**: Coordinates all agents and manages interview state machine
2. **Question Generator Agent**: Creates contextual questions using LLM + RAG
3. **Response Evaluator Agent**: Multi-dimensional scoring of candidate answers
4. **Context Manager Agent**: Maintains conversation history and interview state
5. **Analytics Agent**: Real-time performance tracking and report generation

### Interview Phases

1. **Introduction**: Ice-breaking and role understanding
2. **Technical**: Role-specific technical assessment
3. **Behavioral**: Situation-based questions (STAR method)
4. **Problem Solving**: Design and analytical challenges
5. **Closing**: Wrap-up and candidate questions

### Tech Stack

**Backend:**
- FastAPI (Python web framework)
- LangChain (LLM orchestration)
- ChromaDB (Vector database for RAG)
- Anthropic Claude API / OpenAI GPT-4
- SQLite (Persistent storage)

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Responsive design
- Real-time UI updates

## 🚀 Setup & Installation

### Prerequisites

```bash
- Python 3.8 or higher
- Node.js (for optional frontend development)
- Anthropic API Key or OpenAI API Key
```

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd interview-agent
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5: Initialize Database

```bash
python init_db.py
```

### Step 6: Run the Application

**Start Backend:**
```bash
python main.py
```

**Access Frontend:**
Open `frontend/index.html` in your browser or serve via:
```bash
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

## 📁 Project Structure

```
interview-agent/
│
├── main.py                      # FastAPI server entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── README.md                    # This file
│
├── agents/                      # Multi-agent system
│   ├── __init__.py
│   ├── orchestrator.py         # Main coordinator agent
│   ├── question_generator.py  # Question generation with RAG
│   ├── response_evaluator.py  # Multi-dimensional evaluation
│   ├── context_manager.py     # Context & state management
│   └── analytics_agent.py     # Performance analytics
│
├── database/                    # Data persistence
│   ├── __init__.py
│   └── db_manager.py           # SQLite database manager
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── config.py               # Configuration
│   └── vector_store.py         # ChromaDB vector store
│
├── data/                        # Data directory (created at runtime)
│   ├── chromadb/               # Vector embeddings
│   └── interview_agent.db      # SQLite database
│
└── frontend/                    # Web interface
    ├── index.html              # Main HTML file
    ├── styles.css              # Styling
    └── script.js               # Frontend logic
```

## 🎮 Usage Guide

### Starting an Interview

1. Open the web interface
2. Fill in candidate details:
   - Full Name
   - Email
   - Job Role (select from dropdown)
   - Years of Experience
   - Job Description (optional)
   - Resume Summary (optional)
3. Click "Start Interview"

### During Interview

- Read each question carefully
- Type your answer in the text area
- Press "Submit" or use `Ctrl + Enter`
- View real-time feedback and scores in the sidebar
- Progress through phases automatically

### After Interview

- View comprehensive report with:
  - Overall score
  - Dimension-wise scores
  - Strengths and weaknesses
  - Technical assessment
  - Hiring recommendation
- Download report (PDF export)

### Dashboard

- View all interviews
- Check statistics
- Access previous reports

## 📊 Evaluation Dimensions

Candidates are evaluated on 4 key dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Technical Accuracy | 30% | Correctness and depth of technical knowledge |
| Communication Quality | 25% | Clarity, structure, and professionalism |
| Problem-Solving | 25% | Analytical thinking and approach |
| Cultural Fit | 20% | Team collaboration and values alignment |

## 🔧 Configuration

### Adjusting Interview Parameters

Edit `agents/orchestrator.py`:

```python
self.max_questions_per_phase = 3  # Questions per phase
self.PHASES = ['introduction', 'technical', ...]  # Interview phases
```

### Adding Custom Questions

Use the vector store API:

```python
from utils.vector_store import VectorStore

vs = VectorStore()
vs.add_custom_question(
    question="Your custom question?",
    category="technical",
    role="software_engineer",
    difficulty="hard"
)
```

### Changing LLM Model

Edit `agents/question_generator.py` and `agents/response_evaluator.py`:

```python
# For Claude
model="claude-sonnet-4-20250514"

# For OpenAI
model="gpt-4"
```

## 🔍 API Documentation

### Start Interview
```
POST /api/interview/start
Body: {
    candidate_name, candidate_email, job_role,
    job_description, experience_years, resume_summary
}
```

### Submit Answer
```
POST /api/interview/answer
Body: { interview_id, answer }
```

### Get Report
```
GET /api/interview/{interview_id}/report
```

### List Interviews
```
GET /api/interviews/list?limit=10&offset=0
```

Full API documentation: `http://localhost:8000/docs`

## 🎯 Features & Limitations

### Current Features ✅

- Multi-agent adaptive interview system
- Real-time evaluation and feedback
- RAG-based question generation
- Comprehensive reporting
- Database persistence
- Web-based interface
- Multiple job roles support
- Phase-based interview flow

### Known Limitations ⚠️

- Single concurrent interview per session (can be extended for production)
- No voice input/output (text-only)
- Limited to predefined job roles in question bank
- No video recording capability
- Requires internet connection for LLM API calls

### Potential Improvements 🚀

1. Voice Integration: Add speech-to-text and text-to-speech
2. Video Analysis: Facial expression and body language analysis
3. Multi-language Support: Conduct interviews in multiple languages
4. Advanced Analytics: ML-based hiring predictions
5. Integration: Connect with ATS systems (Greenhouse, Lever, etc.)
6. Collaborative Interviews: Multi-interviewer support
7. Custom Training: Fine-tune models on company-specific data
8. Mobile App: Native mobile applications
9. Real-time Collaboration: Live co-interviewing features
10. Advanced Security: End-to-end encryption, GDPR compliance

## 🧪 Testing

### Run Tests

```bash
pytest tests/
```

### Test Interview Flow

```bash
python tests/test_interview_flow.py
```

## 👥 Contributors

- Greeshma R Gowda - Initial Development

##  Acknowledgments

- Anthropic Claude API for LLM capabilities
- ChromaDB for vector storage
- FastAPI for backend framework
- Rooman Technologies for the challenge opportunity



## 🎓 Educational Purpose

This project was developed as part of the Rooman Technologies 48-Hour AI Agent Development Challenge.

---

**Built using Advanced Multi-Agent AI Architecture**