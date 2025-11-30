"""
Response Evaluator Agent
Evaluates candidate responses on multiple dimensions
"""

from typing import Dict, List
import anthropic
import os
import json


class ResponseEvaluatorAgent:
    """
    Evaluates candidate responses using multi-dimensional scoring:
    - Technical Accuracy (30%)
    - Communication Quality (25%)
    - Problem-Solving Ability (25%)
    - Cultural Fit (20%)
    """
    
    EVALUATION_DIMENSIONS = {
        'technical_accuracy': 0.30,
        'communication_quality': 0.25,
        'problem_solving': 0.25,
        'cultural_fit': 0.20
    }
    
    def __init__(self, job_role: str, job_description: str):
        self.job_role = job_role
        self.job_description = job_description
        
        # Initialize Claude API
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        if not api_key:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. Using simple evaluation.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def evaluate_response(self, question: str, answer: str, 
                         phase: str, context: str) -> Dict:
        """
        Evaluate a candidate's response
        Returns detailed scores and feedback
        """
        
        # Build evaluation prompt
        prompt = f"""You are an expert interviewer evaluating a candidate's response.

Job Role: {self.job_role}
Job Description: {self.job_description}
Interview Phase: {phase}

Question Asked: {question}
Candidate's Answer: {answer}

Evaluate this response on the following dimensions (score 0-100 for each):

1. Technical Accuracy (30%): How technically correct and detailed is the answer?
2. Communication Quality (25%): How clear, structured, and professional is the communication?
3. Problem-Solving Ability (25%): Does the answer demonstrate analytical thinking and problem-solving skills?
4. Cultural Fit (20%): Does the response align with professional values and team collaboration?

Provide your evaluation in this EXACT JSON format:
{{
  "technical_accuracy": <score 0-100>,
  "communication_quality": <score 0-100>,
  "problem_solving": <score 0-100>,
  "cultural_fit": <score 0-100>,
  "feedback": "<brief constructive feedback>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "areas_for_improvement": ["<area 1>", "<area 2>"]
}}

Be objective and fair. Consider the candidate's experience level."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Parse JSON response
            # Try to extract JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(response_text)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(evaluation)
            evaluation['overall_score'] = overall_score
            evaluation['phase'] = phase
            
            return evaluation
            
        except Exception as e:
            print(f"Error in evaluation: {e}")
            # Return default evaluation
            return self._get_default_evaluation(answer, phase)
    
    def _calculate_overall_score(self, evaluation: Dict) -> float:
        """Calculate weighted overall score"""
        score = 0
        for dimension, weight in self.EVALUATION_DIMENSIONS.items():
            score += evaluation.get(dimension, 50) * weight
        
        return round(score, 2)
    
    def _get_default_evaluation(self, answer: str, phase: str) -> Dict:
        """Fallback evaluation if API fails"""
        # Basic heuristics
        answer_length = len(answer.split())
        
        if answer_length < 10:
            base_score = 30
        elif answer_length < 30:
            base_score = 50
        elif answer_length < 80:
            base_score = 70
        else:
            base_score = 80
        
        return {
            'technical_accuracy': base_score,
            'communication_quality': base_score,
            'problem_solving': base_score,
            'cultural_fit': base_score,
            'overall_score': base_score,
            'feedback': "Thank you for your response. Could you elaborate more on specific examples?",
            'strengths': ["Provided a response"],
            'areas_for_improvement': ["Could provide more specific examples"],
            'phase': phase
        }
    
    def generate_overall_assessment(self, interview_history: List[Dict]) -> Dict:
        """Generate overall assessment from entire interview"""
        
        # Aggregate scores by dimension
        dimension_scores = {dim: [] for dim in self.EVALUATION_DIMENSIONS.keys()}
        
        for interaction in interview_history:
            eval_data = interaction.get('evaluation', {})
            for dim in self.EVALUATION_DIMENSIONS.keys():
                if dim in eval_data:
                    dimension_scores[dim].append(eval_data[dim])
        
        # Calculate averages
        avg_scores = {}
        for dim, scores in dimension_scores.items():
            if scores:
                avg_scores[dim] = round(sum(scores) / len(scores), 2)
            else:
                avg_scores[dim] = 50
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for dim, score in avg_scores.items():
            dim_name = dim.replace('_', ' ').title()
            if score >= 75:
                strengths.append(f"{dim_name}: {score}/100")
            elif score < 60:
                weaknesses.append(f"{dim_name}: {score}/100")
        
        # Determine technical level
        tech_score = avg_scores.get('technical_accuracy', 50)
        if tech_score >= 80:
            tech_level = "Expert"
        elif tech_score >= 65:
            tech_level = "Proficient"
        elif tech_score >= 50:
            tech_level = "Intermediate"
        else:
            tech_level = "Beginner"
        
        # Communication quality assessment
        comm_score = avg_scores.get('communication_quality', 50)
        if comm_score >= 80:
            comm_quality = "Excellent - Clear, structured, and professional"
        elif comm_score >= 65:
            comm_quality = "Good - Generally clear with minor areas for improvement"
        elif comm_score >= 50:
            comm_quality = "Adequate - Could improve structure and clarity"
        else:
            comm_quality = "Needs Improvement - Responses lack clarity"
        
        return {
            'dimension_scores': avg_scores,
            'strengths': strengths if strengths else ["Completed the interview"],
            'weaknesses': weaknesses if weaknesses else ["No major weaknesses identified"],
            'technical_level': tech_level,
            'communication_quality': comm_quality
        }