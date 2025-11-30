"""
Analytics Agent
Tracks performance metrics and generates insights
"""

from typing import Dict, List
from collections import defaultdict


class AnalyticsAgent:
    """
    Analyzes interview performance in real-time
    Generates metrics and insights
    """
    
    def __init__(self):
        self.phase_data = defaultdict(list)
        self.dimension_data = defaultdict(list)
        self.all_scores = []
    
    def add_interaction(self, phase: str, evaluation: Dict):
        """Record an interaction for analytics"""
        overall_score = evaluation.get('overall_score', 0)
        
        # Store by phase
        self.phase_data[phase].append({
            'score': overall_score,
            'evaluation': evaluation
        })
        
        # Store dimension scores
        for dimension in ['technical_accuracy', 'communication_quality', 
                         'problem_solving', 'cultural_fit']:
            if dimension in evaluation:
                self.dimension_data[dimension].append(evaluation[dimension])
        
        # Store all scores
        self.all_scores.append(overall_score)
    
    def get_recent_scores(self, n: int = 3) -> List[float]:
        """Get n most recent scores"""
        return self.all_scores[-n:] if self.all_scores else []
    
    def get_phase_average(self, phase: str) -> float:
        """Get average score for a specific phase"""
        if phase not in self.phase_data or not self.phase_data[phase]:
            return 0.0
        
        scores = [item['score'] for item in self.phase_data[phase]]
        return round(sum(scores) / len(scores), 2)
    
    def get_dimension_average(self, dimension: str) -> float:
        """Get average score for a specific dimension"""
        if dimension not in self.dimension_data or not self.dimension_data[dimension]:
            return 0.0
        
        scores = self.dimension_data[dimension]
        return round(sum(scores) / len(scores), 2)
    
    def get_summary(self) -> Dict:
        """Get real-time analytics summary"""
        if not self.all_scores:
            return {
                'overall_average': 0,
                'total_interactions': 0,
                'trend': 'neutral'
            }
        
        overall_avg = round(sum(self.all_scores) / len(self.all_scores), 2)
        
        # Calculate trend
        trend = 'neutral'
        if len(self.all_scores) >= 3:
            recent_avg = sum(self.all_scores[-3:]) / 3
            earlier_avg = sum(self.all_scores[:-3]) / max(len(self.all_scores) - 3, 1)
            
            if recent_avg > earlier_avg + 5:
                trend = 'improving'
            elif recent_avg < earlier_avg - 5:
                trend = 'declining'
        
        return {
            'overall_average': overall_avg,
            'total_interactions': len(self.all_scores),
            'trend': trend,
            'latest_score': self.all_scores[-1] if self.all_scores else 0
        }
    
    def generate_final_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        if not self.all_scores:
            return self._get_empty_report()
        
        # Calculate overall score
        overall_score = round(sum(self.all_scores) / len(self.all_scores), 2)
        
        # Calculate phase scores
        phase_scores = {}
        for phase in self.phase_data.keys():
            phase_scores[phase] = self.get_phase_average(phase)
        
        # Calculate dimension scores
        dimension_scores = {}
        for dimension in ['technical_accuracy', 'communication_quality', 
                         'problem_solving', 'cultural_fit']:
            dimension_scores[dimension] = self.get_dimension_average(dimension)
        
        # Performance trend analysis
        trend_data = self._analyze_trend()
        
        return {
            'overall_score': overall_score,
            'phase_scores': phase_scores,
            'dimension_scores': dimension_scores,
            'total_questions': len(self.all_scores),
            'performance_trend': trend_data['trend'],
            'consistency': trend_data['consistency'],
            'score_distribution': self._get_score_distribution()
        }
    
    def _analyze_trend(self) -> Dict:
        """Analyze performance trend throughout interview"""
        if len(self.all_scores) < 3:
            return {'trend': 'insufficient_data', 'consistency': 'N/A'}
        
        first_third = self.all_scores[:len(self.all_scores)//3]
        last_third = self.all_scores[-len(self.all_scores)//3:]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        diff = last_avg - first_avg
        
        if diff > 10:
            trend = 'Strong Improvement'
        elif diff > 5:
            trend = 'Improving'
        elif diff < -10:
            trend = 'Declining'
        elif diff < -5:
            trend = 'Slight Decline'
        else:
            trend = 'Consistent'
        
        # Calculate consistency (inverse of standard deviation)
        mean_score = sum(self.all_scores) / len(self.all_scores)
        variance = sum((x - mean_score) ** 2 for x in self.all_scores) / len(self.all_scores)
        std_dev = variance ** 0.5
        
        if std_dev < 10:
            consistency = 'High'
        elif std_dev < 20:
            consistency = 'Medium'
        else:
            consistency = 'Low'
        
        return {
            'trend': trend,
            'consistency': consistency
        }
    
    def _get_score_distribution(self) -> Dict:
        """Get distribution of scores"""
        if not self.all_scores:
            return {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        
        distribution = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        
        for score in self.all_scores:
            if score >= 80:
                distribution['excellent'] += 1
            elif score >= 65:
                distribution['good'] += 1
            elif score >= 50:
                distribution['average'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _get_empty_report(self) -> Dict:
        """Return empty report structure"""
        return {
            'overall_score': 0,
            'phase_scores': {},
            'dimension_scores': {},
            'total_questions': 0,
            'performance_trend': 'N/A',
            'consistency': 'N/A',
            'score_distribution': {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        }