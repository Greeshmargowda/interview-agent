"""
Interview Agent - FastAPI Backend (Simplified with Error Handling)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from datetime import datetime
import traceback
import os

# Check if .env file exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

app = FastAPI(title="Interview Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components with error handling
try:
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠️  Database initialization failed: {e}")
    db = None

# Store active interview sessions
active_interviews = {}

# Pydantic models
class InterviewStartRequest(BaseModel):
    candidate_name: str
    candidate_email: str
    job_role: str
    job_description: str
    experience_years: int
    resume_summary: Optional[str] = ""

class CandidateAnswer(BaseModel):
    interview_id: str
    answer: str

# Simple mock orchestrator for testing
class SimpleOrchestrator:
    def __init__(self, job_role, job_description, candidate_name, experience_years, resume_summary):
        self.job_role = job_role
        self.candidate_name = candidate_name
        self.questions = [
            f"Hello {candidate_name}! Tell me about yourself and your experience with {job_role}.",
            f"What interests you most about this {job_role} position?",
            "Describe a challenging project you've worked on.",
            "How do you stay updated with industry trends?",
            "Do you have any questions for us?"
        ]
        self.current_question_index = 0
        self.interview_history = []
    
    def start_interview(self):
        return self.questions[0]
    
    def process_answer(self, answer):
        self.interview_history.append({
            'question': self.questions[self.current_question_index],
            'answer': answer
        })
        
        self.current_question_index += 1
        
        if self.current_question_index >= len(self.questions):
            return {
                'interview_complete': True,
                'previous_question': self.questions[self.current_question_index - 1],
                'score': 75,
                'feedback': 'Thank you for your responses!'
            }
        
        return {
            'interview_complete': False,
            'next_question': self.questions[self.current_question_index],
            'phase': 'technical' if self.current_question_index < 3 else 'closing',
            'score': 70 + (self.current_question_index * 5),
            'feedback': 'Good answer! Keep going.',
            'previous_question': self.questions[self.current_question_index - 1]
        }
    
    def generate_final_report(self):
        return {
            'candidate_name': self.candidate_name,
            'job_role': self.job_role,
            'interview_date': datetime.now().isoformat(),
            'total_questions': len(self.interview_history),
            'overall_score': 75,
            'phase_scores': {'technical': 75, 'behavioral': 80},
            'dimension_scores': {
                'technical_accuracy': 75,
                'communication_quality': 80,
                'problem_solving': 70,
                'cultural_fit': 75
            },
            'strengths': ['Good communication', 'Relevant experience'],
            'weaknesses': ['Could provide more specific examples'],
            'technical_assessment': 'Proficient',
            'communication_quality': 'Good',
            'recommendation': 'Hire',
            'confidence': 'Medium',
            'reasoning': 'Candidate shows good potential.',
            'next_steps': ['Technical round', 'Team interview'],
            'interview_transcript': self.interview_history
        }

@app.get("/")
def read_root():
    return {
        "message": "Interview Agent API",
        "version": "1.0.0",
        "status": "active"
    }

@app.post("/api/interview/start")
async def start_interview(request: InterviewStartRequest):
    """Start a new interview session"""
    try:
        print(f"\n📝 Starting interview for: {request.candidate_name}")
        print(f"   Role: {request.job_role}")
        print(f"   Experience: {request.experience_years} years")
        
        # Try to import the real orchestrator, fall back to simple one
        try:
            from agents.orchestrator import InterviewOrchestrator
            orchestrator = InterviewOrchestrator(
                job_role=request.job_role,
                job_description=request.job_description,
                candidate_name=request.candidate_name,
                experience_years=request.experience_years,
                resume_summary=request.resume_summary
            )
            print("✅ Using full AI orchestrator")
        except Exception as e:
            print(f"⚠️  Full orchestrator failed: {e}")
            print("ℹ️  Using simple mock orchestrator")
            orchestrator = SimpleOrchestrator(
                job_role=request.job_role,
                job_description=request.job_description,
                candidate_name=request.candidate_name,
                experience_years=request.experience_years,
                resume_summary=request.resume_summary
            )
        
        # Generate interview ID
        interview_id = f"INT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.candidate_name[:3].upper()}"
        
        # Store in database if available
        if db:
            try:
                db.create_interview(
                    interview_id=interview_id,
                    candidate_name=request.candidate_name,
                    candidate_email=request.candidate_email,
                    job_role=request.job_role,
                    job_description=request.job_description,
                    experience_years=request.experience_years
                )
            except Exception as e:
                print(f"⚠️  Database save failed: {e}")
        
        # Start interview and get first question
        first_question = orchestrator.start_interview()
        
        # Store active session
        active_interviews[interview_id] = orchestrator
        
        print(f"✅ Interview started: {interview_id}")
        
        return {
            "success": True,
            "interview_id": interview_id,
            "message": "Interview started successfully",
            "first_question": first_question,
            "phase": "introduction"
        }
        
    except Exception as e:
        print(f"❌ Error starting interview: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@app.post("/api/interview/answer")
async def submit_answer(answer_data: CandidateAnswer):
    """Submit candidate answer and get next question"""
    try:
        interview_id = answer_data.interview_id
        
        if interview_id not in active_interviews:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        orchestrator = active_interviews[interview_id]
        
        # Process answer
        result = orchestrator.process_answer(answer_data.answer)
        
        # Save interaction to database if available
        if db:
            try:
                db.save_interaction(
                    interview_id=interview_id,
                    question=result['previous_question'],
                    answer=answer_data.answer,
                    score=result.get('score', 0),
                    feedback=result.get('feedback', ''),
                    phase=result.get('phase', '')
                )
            except Exception as e:
                print(f"⚠️  Database save failed: {e}")
        
        # Check if interview is complete
        if result.get('interview_complete', False):
            final_report = orchestrator.generate_final_report()
            
            if db:
                try:
                    db.save_final_report(interview_id, final_report)
                except Exception as e:
                    print(f"⚠️  Report save failed: {e}")
            
            del active_interviews[interview_id]
            
            return {
                "success": True,
                "interview_complete": True,
                "final_report": final_report,
                "message": "Interview completed successfully"
            }
        
        return {
            "success": True,
            "interview_complete": False,
            "next_question": result['next_question'],
            "phase": result.get('phase', 'technical'),
            "feedback": result.get('feedback', ''),
            "score": result.get('score', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing answer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/{interview_id}/status")
async def get_interview_status(interview_id: str):
    """Get current interview status"""
    try:
        if interview_id in active_interviews:
            return {
                "success": True,
                "status": "in_progress"
            }
        elif db:
            report = db.get_final_report(interview_id)
            if report:
                return {
                    "success": True,
                    "status": "completed",
                    "data": report
                }
        
        raise HTTPException(status_code=404, detail="Interview not found")
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/{interview_id}/report")
async def get_interview_report(interview_id: str):
    """Get final interview report"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        report = db.get_final_report(interview_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interviews/list")
async def list_interviews(limit: int = 10, offset: int = 0):
    """List all interviews"""
    try:
        if not db:
            return {
                "success": True,
                "interviews": [],
                "count": 0
            }
        
        interviews = db.get_all_interviews(limit=limit, offset=offset)
        return {
            "success": True,
            "interviews": interviews,
            "count": len(interviews)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_interviews": len(active_interviews),
        "database": "connected" if db else "unavailable"
    }

if __name__ == "__main__":
    print("🚀 Starting Interview Agent API Server...")
    print("📊 Dashboard: http://localhost:8000/docs")
    print("💡 API will work with or without full AI components")
    print()
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  WARNING: No API key found!")
        print("   Add ANTHROPIC_API_KEY or OPENAI_API_KEY to .env file")
        print("   System will work with mock responses for now")
        print()
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)