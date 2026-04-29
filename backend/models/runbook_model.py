# models/runbook_model.py
import sqlite3
from config import Config

class RunbookModel:
    """Database operations for runbooks"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
    
    def get_all_runbooks(self):
        """Fetch all runbooks from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, category, keywords, steps FROM runbooks')
        rows = cursor.fetchall()
        conn.close()
        
        runbooks = []
        for row in rows:
            runbooks.append({
                'id': row[0],
                'title': row[1],
                'category': row[2],
                'keywords': row[3],
                'steps': row[4]
            })
        return runbooks
    
    def get_runbook_by_id(self, runbook_id):
        """Fetch specific runbook by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, title, category, keywords, steps FROM runbooks WHERE id = ?',
            (runbook_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'category': row[2],
                'keywords': row[3],
                'steps': row[4]
            }
        return None
    
    def get_runbooks_by_ids(self, runbook_ids):
        """Fetch multiple runbooks by IDs"""
        runbooks = []
        for rb_id in runbook_ids:
            runbook = self.get_runbook_by_id(rb_id)
            if runbook:
                runbooks.append(runbook)
        return runbooks
    
    def create_runbook(self, title, category, keywords, steps):
        """Insert new runbook into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO runbooks (title, category, keywords, steps) VALUES (?, ?, ?, ?)",
            (title, category, keywords, steps)
        )
        runbook_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return runbook_id