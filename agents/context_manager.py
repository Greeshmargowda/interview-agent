"""
Context Manager Agent
Maintains conversation history and interview state
"""

from typing import List, Dict
from collections import deque


class ContextManagerAgent:
    """
    Manages interview context and conversation history
    Implements sliding window to maintain relevant context
    """
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.full_history = []  # Keep complete history
        self.state = {
            'topics_covered': set(),
            'knowledge_gaps': [],
            'strong_areas': []
        }
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        message = {
            'role': role,
            'content': content
        }
        self.conversation_history.append(message)
        self.full_history.append(message)
    
    def get_context(self, last_n: int = 10) -> str:
        """Get formatted context for LLM"""
        recent = list(self.conversation_history)[-last_n:]
        
        formatted = []
        for msg in recent:
            role = "Interviewer" if msg['role'] == 'assistant' else "Candidate"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def update_state(self, topic: str = None, gap: str = None, strength: str = None):
        """Update interview state tracking"""
        if topic:
            self.state['topics_covered'].add(topic)
        if gap:
            self.state['knowledge_gaps'].append(gap)
        if strength:
            self.state['strong_areas'].append(strength)
    
    def get_full_history(self) -> List[Dict]:
        """Get complete conversation history"""
        return self.full_history
    
    def get_state_summary(self) -> Dict:
        """Get summary of interview state"""
        return {
            'topics_covered': list(self.state['topics_covered']),
            'knowledge_gaps': self.state['knowledge_gaps'],
            'strong_areas': self.state['strong_areas'],
            'total_exchanges': len(self.full_history) // 2
        }