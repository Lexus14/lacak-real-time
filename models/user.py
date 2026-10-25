"""
User model with Role-Based Access Control (RBAC)
Implements multi-user system with granular permissions
"""

from enum import Enum
import hashlib
import secrets
from datetime import datetime


class UserRole(Enum):
    """User roles in the system"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class Permission(Enum):
    """Granular permissions for the system"""
    SEARCH_PHONE = "search_phone"
    SEARCH_NIK = "search_nik"
    EXPORT_DATA = "export_data"
    VIEW_HISTORY = "view_history"
    DELETE_HISTORY = "delete_history"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOG = "view_audit_log"
    CONFIGURE_API = "configure_api"


# Role to Permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [p for p in Permission],  # All permissions
    UserRole.OPERATOR: [
        Permission.SEARCH_PHONE,
        Permission.SEARCH_NIK,
        Permission.EXPORT_DATA,
        Permission.VIEW_HISTORY
    ],
    UserRole.VIEWER: [
        Permission.VIEW_HISTORY,
        Permission.VIEW_AUDIT_LOG
    ],
    UserRole.AUDITOR: [
        Permission.VIEW_HISTORY,
        Permission.VIEW_AUDIT_LOG,
        Permission.EXPORT_DATA
    ]
}


class User:
    """User model with authentication and authorization"""
    
    def __init__(self, username, role, password_hash=None, user_id=None):
        self.id = user_id
        self.username = username
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.password_hash = password_hash
        self.session_token = None
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True
    
    @staticmethod
    def hash_password(password):
        """Hash password dengan salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password):
        """Verify password"""
        if not self.password_hash or '$' not in self.password_hash:
            return False
        try:
            salt, stored_hash = self.password_hash.split('$')
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return pwd_hash.hex() == stored_hash
        except ValueError:
            return False
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        if isinstance(permission, str):
            permission = Permission(permission)
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def generate_session_token(self):
        """Generate session token"""
        self.session_token = secrets.token_urlsafe(32)
        self.last_login = datetime.now()
        return self.session_token
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
