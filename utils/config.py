"""
Configuration Management
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/interview_agent.db')
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './data/chromadb')
    
    # LLM Settings
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'claude-sonnet-4-20250514')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Interview Settings
    MAX_QUESTIONS_PER_PHASE = int(os.getenv('MAX_QUESTIONS_PER_PHASE', '3'))
    INTERVIEW_PHASES = ['introduction', 'technical', 'behavioral', 'problem_solving', 'closing']
    
    # Server Settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8000'))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.ANTHROPIC_API_KEY and not cls.OPENAI_API_KEY:
            print("⚠️  Warning: No API key found. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY")
            print("    Add your key to .env file or set as environment variable")
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(cls.DATABASE_PATH), exist_ok=True)
        os.makedirs(cls.VECTOR_DB_PATH, exist_ok=True)
        
        return True


# Validate on import
Config.validate()