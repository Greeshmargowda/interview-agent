"""
Database Manager
Handles all database operations using SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class DatabaseManager:
    """
    Manages interview data persistence
    """
    
    def __init__(self, db_path: str = "./data/interview_agent.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Interviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                interview_id TEXT PRIMARY KEY,
                candidate_name TEXT NOT NULL,
                candidate_email TEXT,
                job_role TEXT NOT NULL,
                job_description TEXT,
                experience_years INTEGER,
                status TEXT DEFAULT 'in_progress',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Interactions table (Q&A pairs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                score REAL,
                feedback TEXT,
                phase TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (interview_id) REFERENCES interviews(interview_id)
            )
        ''')
        
        # Final reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                interview_id TEXT PRIMARY KEY,
                report_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (interview_id) REFERENCES interviews(interview_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized")
    
    def create_interview(self, interview_id: str, candidate_name: str,
                        candidate_email: str, job_role: str, 
                        job_description: str, experience_years: int):
        """Create a new interview record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interviews 
            (interview_id, candidate_name, candidate_email, job_role, 
             job_description, experience_years)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (interview_id, candidate_name, candidate_email, job_role, 
              job_description, experience_years))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created interview: {interview_id}")
    
    def save_interaction(self, interview_id: str, question: str, 
                        answer: str, score: float, feedback: str, phase: str = ""):
        """Save a Q&A interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions 
            (interview_id, question, answer, score, feedback, phase)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (interview_id, question, answer, score, feedback, phase))
        
        conn.commit()
        conn.close()
    
    def save_final_report(self, interview_id: str, report_data: Dict):
        """Save final interview report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert report to JSON
        report_json = json.dumps(report_data)
        
        cursor.execute('''
            INSERT OR REPLACE INTO reports (interview_id, report_data)
            VALUES (?, ?)
        ''', (interview_id, report_json))
        
        # Update interview status
        cursor.execute('''
            UPDATE interviews 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE interview_id = ?
        ''', (interview_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved final report: {interview_id}")
    
    def get_final_report(self, interview_id: str) -> Optional[Dict]:
        """Retrieve final report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT report_data FROM reports WHERE interview_id = ?
        ''', (interview_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_interview(self, interview_id: str) -> Optional[Dict]:
        """Get interview details"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interviews WHERE interview_id = ?
        ''', (interview_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def get_all_interviews(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get all interviews"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interviews 
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_interactions(self, interview_id: str) -> List[Dict]:
        """Get all interactions for an interview"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interactions 
            WHERE interview_id = ?
            ORDER BY created_at ASC
        ''', (interview_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def update_interview_status(self, interview_id: str, status: str):
        """Update interview status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE interviews SET status = ? WHERE interview_id = ?
        ''', (status, interview_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total interviews
        cursor.execute('SELECT COUNT(*) FROM interviews')
        total = cursor.fetchone()[0]
        
        # Completed interviews
        cursor.execute("SELECT COUNT(*) FROM interviews WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        # Average scores
        cursor.execute('SELECT AVG(score) FROM interactions')
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_interviews': total,
            'completed_interviews': completed,
            'in_progress': total - completed,
            'average_score': round(avg_score, 2)
        }