"""
Setup and Installation Script
Run this to initialize the Interview Agent system
"""

import os
import sys
import subprocess


def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'data/chromadb',
        'agents',
        'database',
        'utils',
        'frontend',
        'tests'
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        # Create __init__.py for Python packages
        if dir_path in ['agents', 'database', 'utils']:
            init_file = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""{dir_path.capitalize()} module"""')
    
    print("✅ Created project directories")


def create_env_file():
    """Create .env template if it doesn't exist"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_PATH=./data/interview_agent.db
VECTOR_DB_PATH=./data/chromadb

# LLM Settings
DEFAULT_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=1000
TEMPERATURE=0.7

# Interview Settings
MAX_QUESTIONS_PER_PHASE=3

# Server Settings
HOST=0.0.0.0
PORT=8000
""")
        print("✅ Created .env file template")
        print("⚠️  Please edit .env and add your API keys!")
    else:
        print("ℹ️  .env file already exists")


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Please run manually: pip install -r requirements.txt")


def initialize_database():
    """Initialize database and vector store"""
    print("💾 Initializing database...")
    try:
        from database.db_manager import DatabaseManager
        from utils.vector_store import VectorStore
        
        # Initialize database
        db = DatabaseManager()
        print("✅ Database initialized")
        
        # Initialize vector store
        vs = VectorStore()
        vs.load_question_bank()
        print("✅ Vector store initialized")
        
    except Exception as e:
        print(f"⚠️  Error initializing database: {e}")
        print("   You can run this later after installing dependencies")


def create_readme():
    """Check if README exists"""
    if os.path.exists('README.md'):
        print("✅ README.md found")
    else:
        print("⚠️  README.md not found - please create documentation")


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📝 Next Steps:\n")
    print("1. Edit .env file and add your API key:")
    print("   - Get Anthropic API key from: https://console.anthropic.com/")
    print("   - Or OpenAI API key from: https://platform.openai.com/\n")
    print("2. Run the application:")
    print("   python main.py\n")
    print("3. Open frontend in browser:")
    print("   - Option A: Open frontend/index.html directly")
    print("   - Option B: Run: cd frontend && python -m http.server 8080\n")
    print("4. Access the API documentation:")
    print("   http://localhost:8000/docs\n")
    print("="*60)


def main():
    """Main setup function"""
    print("\n🚀 Interview Agent Setup Script")
    print("="*60 + "\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected\n")
    
    # Run setup steps
    create_directories()
    create_env_file()
    create_readme()
    
    # Ask user if they want to install dependencies
    response = input("\n📦 Install dependencies now? (y/n): ").lower()
    if response == 'y':
        install_dependencies()
        
        # Initialize database
        response = input("\n💾 Initialize database and vector store? (y/n): ").lower()
        if response == 'y':
            initialize_database()
    
    print_next_steps()


if __name__ == "__main__":
    main()