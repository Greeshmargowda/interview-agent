"""
Interview Orchestrator Agent
Coordinates all sub-agents and manages interview flow
"""

from typing import Dict, List
from datetime import datetime
import json

from agents.question_generator import QuestionGeneratorAgent
from agents.response_evaluator import ResponseEvaluatorAgent
from agents.context_manager import ContextManagerAgent
from agents.analytics_agent import AnalyticsAgent


class InterviewOrchestrator:
    """
    Main orchestrator that coordinates all interview agents
    Implements state machine for interview phases
    """
    
    PHASES = ['introduction', 'technical', 'behavioral', 'problem_solving', 'closing']
    
    def __init__(self, job_role: str, job_description: str, 
                 candidate_name: str, experience_years: int, resume_summary: str = ""):
        self.job_role = job_role
        self.job_description = job_description
        self.candidate_name = candidate_name
        self.experience_years = experience_years
        self.resume_summary = resume_summary
        
        # Initialize sub-agents
        self.question_gen = QuestionGeneratorAgent(job_role, job_description, experience_years)
        self.evaluator = ResponseEvaluatorAgent(job_role, job_description)
        self.context_mgr = ContextManagerAgent()
        self.analytics = AnalyticsAgent()
        
        # Interview state
        self.current_phase = 'introduction'
        self.phase_index = 0
        self.questions_asked = 0
        self.questions_in_current_phase = 0
        
        # Different questions per phase
        self.max_questions_per_phase = {
            'introduction': 1,      # Only 1 intro question
            'technical': 3,         # 3 technical questions
            'behavioral': 2,        # 2 behavioral questions
            'problem_solving': 2,   # 2 problem solving questions
            'closing': 1            # 1 closing question
        }
        
        self.current_question = None
        self.interview_history = []
        
        # Performance tracking
        self.phase_scores = {}
        self.overall_score = 0
        
        print(f"✅ Interview Orchestrator initialized for {candidate_name} - {job_role}")
    
    def start_interview(self) -> str:
        """Start the interview and return first question"""
        # Generate introduction question
        self.current_question = self.question_gen.generate_question(
            phase='introduction',
            context=self.context_mgr.get_context(),
            candidate_name=self.candidate_name
        )
        
        self.context_mgr.add_to_history('assistant', self.current_question)
        
        return self.current_question
    
    def process_answer(self, answer: str) -> Dict:
        """
        Process candidate's answer and determine next action
        Returns: dict with next_question, feedback, score, phase info
        """
        # Add answer to context
        self.context_mgr.add_to_history('candidate', answer)
        
        # Evaluate the response
        evaluation = self.evaluator.evaluate_response(
            question=self.current_question,
            answer=answer,
            phase=self.current_phase,
            context=self.context_mgr.get_context()
        )
        
        # Store evaluation
        self.interview_history.append({
            'question': self.current_question,
            'answer': answer,
            'evaluation': evaluation,
            'phase': self.current_phase,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update analytics
        self.analytics.add_interaction(self.current_phase, evaluation)
        
        self.questions_asked += 1
        self.questions_in_current_phase += 1
        
        # Determine if we should move to next phase
        should_transition = self._should_transition_phase()
        
        if should_transition:
            self._transition_to_next_phase()
            self.questions_in_current_phase = 0  # Reset for new phase
        
        if should_transition:
            self._transition_to_next_phase()
        
        # Check if interview is complete
        if self.current_phase == 'closing' and self.questions_asked >= 1:
            return {
                'interview_complete': True,
                'previous_question': self.current_question,
                'score': evaluation['overall_score'],
                'feedback': evaluation['feedback']
            }
        
        # Generate next question based on current phase and performance
        next_question = self.question_gen.generate_question(
            phase=self.current_phase,
            context=self.context_mgr.get_context(),
            previous_evaluation=evaluation,
            candidate_name=self.candidate_name
        )
        
        self.current_question = next_question
        self.context_mgr.add_to_history('assistant', next_question)
        
        return {
            'interview_complete': False,
            'next_question': next_question,
            'phase': self.current_phase,
            'score': evaluation['overall_score'],
            'feedback': evaluation['feedback'],
            'previous_question': self.current_question
        }
    
    def _should_transition_phase(self) -> bool:
        """Determine if we should move to next interview phase"""
        # Get max questions for current phase
        max_for_phase = self.max_questions_per_phase.get(self.current_phase, 3)
        
        # Transition after max questions for this specific phase
        if self.questions_in_current_phase >= max_for_phase:
            return True
        
        # Or if performance is exceptionally good/bad (skip phase early)
        recent_scores = self.analytics.get_recent_scores(2)
        if len(recent_scores) >= 2:
            avg_score = sum(recent_scores) / len(recent_scores)
            # Skip phase if doing very well or very poorly
            if avg_score >= 90 or avg_score <= 30:
                return True
        
        return False
    
    def _transition_to_next_phase(self):
        """Move to next interview phase"""
        self.phase_index += 1
        
        if self.phase_index < len(self.PHASES):
            self.current_phase = self.PHASES[self.phase_index]
            print(f"📍 Transitioning to phase: {self.current_phase}")
        else:
            self.current_phase = 'closing'
    
    def get_status(self) -> Dict:
        """Get current interview status"""
        return {
            'phase': self.current_phase,
            'questions_asked': self.questions_asked,
            'current_question': self.current_question,
            'phase_progress': f"{self.phase_index + 1}/{len(self.PHASES)}",
            'analytics': self.analytics.get_summary()
        }
    
    def generate_final_report(self) -> Dict:
        """Generate comprehensive final interview report"""
        # Calculate final scores
        final_analytics = self.analytics.generate_final_report()
        
        # Get detailed insights from evaluator
        overall_assessment = self.evaluator.generate_overall_assessment(
            self.interview_history
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_analytics, overall_assessment)
        
        report = {
            'candidate_name': self.candidate_name,
            'job_role': self.job_role,
            'interview_date': datetime.now().isoformat(),
            'total_questions': self.questions_asked,
            'duration_estimate': f"{self.questions_asked * 3} minutes",
            
            # Scores
            'overall_score': final_analytics['overall_score'],
            'phase_scores': final_analytics['phase_scores'],
            'dimension_scores': final_analytics['dimension_scores'],
            
            # Detailed assessment
            'strengths': overall_assessment['strengths'],
            'weaknesses': overall_assessment['weaknesses'],
            'technical_assessment': overall_assessment['technical_level'],
            'communication_quality': overall_assessment['communication_quality'],
            
            # Recommendation
            'recommendation': recommendations['decision'],
            'confidence': recommendations['confidence'],
            'reasoning': recommendations['reasoning'],
            'next_steps': recommendations['next_steps'],
            
            # Detailed history
            'interview_transcript': self.interview_history
        }
        
        return report
    
    def _generate_recommendations(self, analytics: Dict, assessment: Dict) -> Dict:
        """Generate hiring recommendations"""
        score = analytics['overall_score']
        
        if score >= 75:
            decision = "Strong Hire"
            confidence = "High"
            reasoning = "Candidate demonstrated strong technical skills and excellent communication."
            next_steps = ["Proceed to final round", "Send offer"]
        elif score >= 60:
            decision = "Hire"
            confidence = "Medium"
            reasoning = "Candidate shows good potential with room for growth."
            next_steps = ["Additional technical interview", "Team fit assessment"]
        elif score >= 45:
            decision = "Maybe"
            confidence = "Low"
            reasoning = "Candidate has some skills but significant gaps identified."
            next_steps = ["Skills assessment test", "Consider for junior role"]
        else:
            decision = "No Hire"
            confidence = "High"
            reasoning = "Candidate did not meet the requirements for this position."
            next_steps = ["Send rejection with feedback", "Keep in talent pool"]
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'next_steps': next_steps
        }