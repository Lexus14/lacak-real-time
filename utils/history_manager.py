"""
History Manager for Persistent Storage
Handles SQLite database storage for search history and favorites
"""

import sqlite3
import json
from datetime import datetime
import os

class HistoryManager:
    def __init__(self):
        self.db_path = "data/app_data.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables if they don't exist"""
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create search_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    note TEXT,
                    is_favorite INTEGER DEFAULT 0
                )
            ''')
            
            # Create favorites table (separate for easier management)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    note TEXT,
                    added_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing history database: {str(e)}")
    
    def add_search(self, target, result, note=""):
        """Add a search to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO search_history (target, timestamp, result_json, note) VALUES (?, ?, ?, ?)",
                (target, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), json.dumps(result), note)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding search to history: {str(e)}")
            return False
    
    def get_all_history(self, limit=50):
        """Get all search history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM search_history ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'target': row[1],
                    'timestamp': row[2],
                    'result': json.loads(row[3]),
                    'note': row[4],
                    'is_favorite': bool(row[5])
                })
            
            return history
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return []
    
    def add_favorite(self, target, result, note=""):
        """Add a search to favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if already in favorites
            cursor.execute("SELECT id FROM favorites WHERE target = ?", (target,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing favorite
                cursor.execute(
                    "UPDATE favorites SET timestamp = ?, result_json = ?, note = ? WHERE target = ?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), json.dumps(result), note, target)
                )
            else:
                # Add new favorite
                cursor.execute(
                    "INSERT INTO favorites (target, timestamp, result_json, note, added_at) VALUES (?, ?, ?, ?, ?)",
                    (target, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), json.dumps(result), note, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
            
            # Also mark as favorite in search_history
            cursor.execute(
                "UPDATE search_history SET is_favorite = 1 WHERE target = ?",
                (target,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding favorite: {str(e)}")
            return False
    
    def get_all_favorites(self):
        """Get all favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM favorites ORDER BY added_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            favorites = []
            for row in rows:
                favorites.append({
                    'id': row[0],
                    'target': row[1],
                    'timestamp': row[2],
                    'result': json.loads(row[3]),
                    'note': row[4],
                    'added_at': row[5]
                })
            
            return favorites
        except Exception as e:
            print(f"Error getting favorites: {str(e)}")
            return []
    
    def remove_favorite(self, target):
        """Remove a favorite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM favorites WHERE target = ?", (target,))
            
            # Also unmark as favorite in search_history
            cursor.execute(
                "UPDATE search_history SET is_favorite = 0 WHERE target = ?",
                (target,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing favorite: {str(e)}")
            return False
    
    def add_note_to_search(self, target, note):
        """Add a note to a search in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE search_history SET note = ? WHERE target = ?",
                (note, target)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding note: {str(e)}")
            return False
    
    def clear_history(self):
        """Clear all search history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM search_history")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing history: {str(e)}")
            return False
    
    def get_search_count(self):
        """Get total search count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM search_history")
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
        except Exception as e:
            print(f"Error getting search count: {str(e)}")
            return 0
    
    def get_favorites_count(self):
        """Get total favorites count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM favorites")
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
        except Exception as e:
            print(f"Error getting favorites count: {str(e)}")
            return 0