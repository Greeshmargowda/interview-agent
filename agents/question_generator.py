"""
Question Generator Agent
Generates adaptive interview questions using RAG and LLM
"""

from typing import Dict, Optional
import anthropic
import os
from utils.vector_store import VectorStore


class QuestionGeneratorAgent:
    """
    Generates contextual interview questions based on:
    - Job role and description
    - Candidate's experience level
    - Previous answers (adaptive)
    - Interview phase
    """
    
    def __init__(self, job_role: str, job_description: str, experience_years: int):
        self.job_role = job_role
        self.job_description = job_description
        self.experience_years = experience_years
        
        # Initialize Claude (you can also use OpenAI GPT-4)
        api_key = os.getenv('ANTHROPIC_API_KEY', 'your-api-key-here')
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Initialize vector store for RAG
        self.vector_store = VectorStore()
        self.vector_store.load_question_bank()
        
        # Track asked questions to avoid repetition
        self.asked_questions = set()
        
        # Question templates by phase
        self.phase_templates = {
            'introduction': [
                "Tell me about yourself and your experience with {job_role}",
                "What interests you about this {job_role} position?",
                "Walk me through your background relevant to {job_role}"
            ],
            'technical': [
                "Explain {concept} and how you've used it",
                "What's your approach to {technical_task}?",
                "Describe a challenging technical problem you solved"
            ],
            'behavioral': [
                "Tell me about a time when you {situation}",
                "How do you handle {challenge}?",
                "Describe your experience working with {context}"
            ],
            'problem_solving': [
                "How would you approach {problem}?",
                "Design a solution for {scenario}",
                "What would you do if {situation}?"
            ],
            'closing': [
                "Do you have any questions for us?",
                "What are your salary expectations?",
                "When would you be available to start?"
            ]
        }
    
    def generate_question(self, phase: str, context: str, 
                         previous_evaluation: Optional[Dict] = None,
                         candidate_name: str = "") -> str:
        """
        Generate an adaptive question based on current context
        Uses RAG to retrieve relevant questions from vector DB
        """
        
        # For introduction, use simple template
        if phase == 'introduction':
            return f"Hello {candidate_name}! Thanks for joining. To start, could you tell me about yourself and what excites you about this {self.job_role} role?"
        
        # For closing
        if phase == 'closing':
            return f"Thank you for your responses, {candidate_name}. Before we wrap up, do you have any questions for me about the role or the company?"
        
        # Retrieve relevant questions from vector store using RAG
        search_query = f"{phase} questions for {self.job_role} with {self.experience_years} years experience"
        similar_questions = self.vector_store.search_questions(search_query, top_k=5)
        
        # Build context for LLM
        context_for_llm = f"""
You are an expert interviewer conducting a {phase} phase interview for a {self.job_role} position.

Job Description: {self.job_description}
Candidate Experience: {self.experience_years} years
Interview History: {context}

Similar questions from question bank:
{self._format_similar_questions(similar_questions)}

IMPORTANT: Do NOT ask questions similar to these already asked questions:
{self._format_asked_questions()}
"""
        
        # Add adaptive component based on previous evaluation
        if previous_evaluation:
            score = previous_evaluation.get('overall_score', 50)
            if score < 50:
                context_for_llm += "\nNote: Previous answer was weak. Ask a slightly easier follow-up to build confidence."
            elif score > 80:
                context_for_llm += "\nNote: Previous answer was strong. Ask a more challenging question to assess depth."
        
        # Generate question using Claude
        prompt = f"""{context_for_llm}

Generate ONE specific, relevant interview question for the {phase} phase. 

Requirements:
- Make it specific to {self.job_role}
- Appropriate for {self.experience_years} years of experience
- Clear and professional
- Should assess {phase} skills
- Don't repeat questions already asked

Return ONLY the question, nothing else."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            question = message.content[0].text.strip()
            
            # Add to asked questions to avoid repetition
            self.asked_questions.add(question.lower())
            
            return question
            
        except Exception as e:
            print(f"Error generating question: {e}")
            # Fallback to template
            return self._get_fallback_question(phase)
    
    def _format_similar_questions(self, questions: list) -> str:
        """Format similar questions from vector search"""
        if not questions:
            return "No similar questions found."
        
        formatted = []
        for i, q in enumerate(questions[:3], 1):
            formatted.append(f"{i}. {q}")
        
        return "\n".join(formatted)
    
    def _format_asked_questions(self) -> str:
        """Format already asked questions to avoid repetition"""
        if not self.asked_questions:
            return "None yet."
        
        return "\n".join([f"- {q}" for q in list(self.asked_questions)])
    
    
    def _get_fallback_question(self, phase: str) -> str:
        """Get a fallback template question if LLM fails"""
        templates = self.phase_templates.get(phase, self.phase_templates['technical'])
        
        # Simple template substitution
        template = templates[0]
        
        if phase == 'technical':
            return "Can you explain your approach to writing clean, maintainable code? Give me a specific example from your experience."
            
        
        elif phase == 'behavioral':
            return "Tell me about a time when you faced a significant challenge at work. How did you handle it?"
        
        elif phase == 'problem_solving':
            return f"If you were asked to improve our team's efficiency by 30%, what would be your approach?"
        
        return template.format(job_role=self.job_role)