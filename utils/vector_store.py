"""
Vector Store for RAG-based Question Retrieval
Uses ChromaDB for semantic search
"""

import chromadb
from chromadb.config import Settings
from typing import List
import os


class VectorStore:
    """
    Manages vector database for question bank
    Enables semantic search for relevant interview questions
    """
    
    def __init__(self, persist_directory: str = "./data/chromadb"):
        """Initialize ChromaDB client"""
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name="interview_questions")
        except:
            self.collection = self.client.create_collection(
                name="interview_questions",
                metadata={"description": "Interview question bank"}
            )
    
    def load_question_bank(self):
        """Load predefined question bank into vector store"""
        
        # Sample question bank (expand this significantly in production)
        question_bank = [
            # Technical - Software Engineering
            {"question": "Explain the difference between SQL and NoSQL databases. When would you use each?", 
             "category": "technical", "role": "software_engineer", "difficulty": "medium"},
            {"question": "What is the time complexity of common sorting algorithms?", 
             "category": "technical", "role": "software_engineer", "difficulty": "medium"},
            {"question": "Describe your approach to writing unit tests and maintaining test coverage.", 
             "category": "technical", "role": "software_engineer", "difficulty": "medium"},
            {"question": "Explain REST API design principles and best practices.", 
             "category": "technical", "role": "software_engineer", "difficulty": "medium"},
            {"question": "What strategies do you use for debugging production issues?", 
             "category": "technical", "role": "software_engineer", "difficulty": "hard"},
            
            # Technical - Data Science
            {"question": "Explain the bias-variance tradeoff in machine learning.", 
             "category": "technical", "role": "data_scientist", "difficulty": "medium"},
            {"question": "How do you handle imbalanced datasets?", 
             "category": "technical", "role": "data_scientist", "difficulty": "medium"},
            {"question": "Describe your process for feature engineering.", 
             "category": "technical", "role": "data_scientist", "difficulty": "hard"},
            
            # Behavioral
            {"question": "Tell me about a time when you disagreed with a team decision. How did you handle it?", 
             "category": "behavioral", "role": "general", "difficulty": "medium"},
            {"question": "Describe a situation where you had to learn a new technology quickly.", 
             "category": "behavioral", "role": "general", "difficulty": "easy"},
            {"question": "How do you prioritize tasks when everything seems urgent?", 
             "category": "behavioral", "role": "general", "difficulty": "medium"},
            {"question": "Tell me about a time you failed. What did you learn?", 
             "category": "behavioral", "role": "general", "difficulty": "medium"},
            
            # Problem Solving
            {"question": "How would you design a URL shortening service like bit.ly?", 
             "category": "problem_solving", "role": "software_engineer", "difficulty": "hard"},
            {"question": "Design a recommendation system for an e-commerce platform.", 
             "category": "problem_solving", "role": "data_scientist", "difficulty": "hard"},
            {"question": "How would you improve the user onboarding process for a mobile app?", 
             "category": "problem_solving", "role": "product_manager", "difficulty": "medium"},
            
            # Leadership/Management
            {"question": "How do you handle underperforming team members?", 
             "category": "behavioral", "role": "manager", "difficulty": "hard"},
            {"question": "Describe your approach to giving constructive feedback.", 
             "category": "behavioral", "role": "manager", "difficulty": "medium"},
        ]
        
        # Check if questions already loaded
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"✅ Question bank already loaded ({existing_count} questions)")
            return
        
        # Add questions to vector store
        documents = [q["question"] for q in question_bank]
        metadatas = [{"category": q["category"], "role": q["role"], "difficulty": q["difficulty"]} 
                    for q in question_bank]
        ids = [f"q_{i}" for i in range(len(question_bank))]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Loaded {len(question_bank)} questions into vector store")
    
    def search_questions(self, query: str, top_k: int = 5, 
                        category: str = None, role: str = None) -> List[str]:
        """
        Search for relevant questions using semantic similarity
        """
        where_filter = {}
        if category:
            where_filter["category"] = category
        if role:
            where_filter["role"] = role
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        if results and results['documents']:
            return results['documents'][0]
        
        return []
    
    def add_custom_question(self, question: str, category: str, 
                           role: str, difficulty: str):
        """Add a new question to the bank"""
        doc_id = f"custom_{self.collection.count()}"
        
        self.collection.add(
            documents=[question],
            metadatas=[{"category": category, "role": role, "difficulty": difficulty}],
            ids=[doc_id]
        )
        
        print(f"✅ Added custom question: {question[:50]}...")
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the question bank"""
        count = self.collection.count()
        
        return {
            "total_questions": count,
            "collection_name": self.collection.name
        }