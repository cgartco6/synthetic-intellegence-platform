import sqlite3
import logging
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "ai_platform.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("database")
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with required tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    payload TEXT,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Social media posts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_media_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scheduled_time TIMESTAMP,
                    status TEXT DEFAULT 'draft',
                    post_id TEXT,
                    metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    metadata TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_task(self, task_data: Dict[str, Any]) -> bool:
        """Save task to database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks 
                    (id, type, agent_name, payload, status, result, error, created_at, started_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_data['id'],
                    task_data['type'],
                    task_data['agent_name'],
                    json.dumps(task_data.get('payload', {})),
                    task_data['status'],
                    json.dumps(task_data.get('result', {})),
                    task_data.get('error'),
                    task_data.get('created_at'),
                    task_data.get('started_at'),
                    task_data.get('completed_at')
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to save task: {str(e)}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get task: {str(e)}")
            return None
    
    def update_task_status(self, task_id: str, status: str, result: Dict = None, error: str = None):
        """Update task status"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                update_fields = ['status = ?']
                params = [status]
                
                if result is not None:
                    update_fields.append('result = ?')
                    params.append(json.dumps(result))
                
                if error is not None:
                    update_fields.append('error = ?')
                    params.append(error)
                
                if status == 'running':
                    update_fields.append('started_at = ?')
                    params.append(datetime.now().isoformat())
                elif status in ['completed', 'failed']:
                    update_fields.append('completed_at = ?')
                    params.append(datetime.now().isoformat())
                
                params.append(task_id)
                
                cursor.execute(
                    f'UPDATE tasks SET {", ".join(update_fields)} WHERE id = ?',
                    params
                )
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to update task status: {str(e)}")
            return False
    
    def create_project(self, name: str, project_type: str, config: Dict = None) -> int:
        """Create a new project"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO projects (name, project_type, config)
                    VALUES (?, ?, ?)
                ''', (name, project_type, json.dumps(config or {})))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to create project: {str(e)}")
            return -1
    
    def get_projects(self, status: str = None) -> List[Dict[str, Any]]:
        """Get all projects"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute('SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC', (status,))
                else:
                    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
                
                return [self._row_to_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get projects: {str(e)}")
            return []
    
    def save_social_media_post(self, platform: str, content: str, scheduled_time: str = None) -> int:
        """Save social media post"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO social_media_posts (platform, content, scheduled_time)
                    VALUES (?, ?, ?)
                ''', (platform, content, scheduled_time))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to save social media post: {str(e)}")
            return -1
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        result = {}
        for key in row.keys():
            value = row[key]
            
            # Parse JSON fields
            if key in ['payload', 'result', 'config', 'metrics', 'metadata'] and value:
                try:
                    value = json.loads(value)
                except:
                    pass
            
            result[key] = value
        
        return result
