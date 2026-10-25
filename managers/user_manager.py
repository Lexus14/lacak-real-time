"""
User Manager - Handles user authentication and management
Implements multi-user system with RBAC
"""

import sqlite3
import os
from datetime import datetime
from functools import wraps

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User, UserRole, Permission
from utils.helpers import print_colored


class UserManager:
    """Manager for user authentication and management"""
    
    def __init__(self):
        self.db_path = "data/users.db"
        self._init_db()
        self.current_user = None
    
    def _init_db(self):
        """Initialize users database"""
        try:
            os.makedirs("data", exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Create default admin if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                admin = User("admin", UserRole.ADMIN)
                admin_password = os.getenv("PEGASUS_ADMIN_PASSWORD")
                if not admin_password:
                    raise RuntimeError("PEGASUS_ADMIN_PASSWORD is not set")
                admin.password_hash = User.hash_password(admin_password)
                self._save_user(admin, conn)
                print_colored("[i] Default admin user created", "INFO")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing users database: {str(e)}")
    
    def _save_user(self, user, conn=None):
        """Save user to database"""
        should_close = False
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            should_close = True
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at, is_active) VALUES (?, ?, ?, ?, ?)",
            (user.username, user.password_hash, user.role.value, 
             user.created_at.isoformat(), 1 if user.is_active else 0)
        )
        
        if should_close:
            conn.commit()
            conn.close()
    
    def _load_user(self, username):
        """Load user from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, password_hash, role, created_at, last_login, is_active FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = User(
                    user_id=row[0],
                    username=row[1],
                    role=UserRole(row[3]),
                    password_hash=row[2]
                )
                user.created_at = datetime.fromisoformat(row[4]) if row[4] else None
                user.last_login = datetime.fromisoformat(row[5]) if row[5] else None
                user.is_active = bool(row[6])
                return user
            return None
        except Exception as e:
            print(f"Error loading user: {str(e)}")
            return None
    
    def _update_last_login(self, user):
        """Update last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (datetime.now().isoformat(), user.username)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating last login: {str(e)}")
    
    def authenticate(self, username, password):
        """Authenticate user"""
        user = self._load_user(username)
        if user and user.is_active and user.verify_password(password):
            user.generate_session_token()
            self.current_user = user
            self._update_last_login(user)
            return True
        return False
    
    def create_user(self, username, password, role):
        """Create new user (admin only)"""
        if not self.current_user or not self.current_user.has_permission(Permission.MANAGE_USERS):
            raise PermissionError("You don't have permission to create users")
        
        # Check if username exists
        if self._load_user(username):
            raise ValueError(f"Username '{username}' already exists")
        
        if isinstance(role, str):
            role = UserRole(role)
        
        user = User(username, role)
        user.password_hash = User.hash_password(password)
        self._save_user(user)
        return user
    
    def delete_user(self, username):
        """Delete user (admin only)"""
        if not self.current_user or not self.current_user.has_permission(Permission.MANAGE_USERS):
            raise PermissionError("You don't have permission to delete users")
        
        if username == "admin":
            raise ValueError("Cannot delete default admin user")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")
    
    def list_users(self):
        """List all users (admin only)"""
        if not self.current_user or not self.current_user.has_permission(Permission.MANAGE_USERS):
            raise PermissionError("You don't have permission to list users")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, role, created_at, last_login, is_active FROM users")
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'created_at': row[3],
                    'last_login': row[4],
                    'is_active': bool(row[5])
                })
            
            return users
        except Exception as e:
            print(f"Error listing users: {str(e)}")
            return []
    
    def change_password(self, username, new_password):
        """Change user password"""
        if not self.current_user:
            raise PermissionError("Not authenticated")
        
        # Users can change their own password, admins can change any password
        if self.current_user.username != username and not self.current_user.has_permission(Permission.MANAGE_USERS):
            raise PermissionError("You don't have permission to change this user's password")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_hash = User.hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (new_hash, username)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            raise Exception(f"Error changing password: {str(e)}")
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, password_hash, role, created_at, last_login, is_active FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = User(
                    user_id=row[0],
                    username=row[1],
                    role=UserRole(row[3]),
                    password_hash=row[2]
                )
                user.created_at = datetime.fromisoformat(row[4]) if row[4] else None
                user.last_login = datetime.fromisoformat(row[5]) if row[5] else None
                user.is_active = bool(row[6])
                return user
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def require_permission(self, permission):
        """Decorator untuk check permission"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.current_user:
                    raise PermissionError("Not authenticated")
                if not self.current_user.has_permission(permission):
                    raise PermissionError(f"Missing permission: {permission.value if isinstance(permission, Permission) else permission}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
