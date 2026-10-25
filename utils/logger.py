"""
Audit Logger for Compliance and Troubleshooting
Handles logging of search activities and API calls
"""

import logging
from logging.handlers import RotatingFileHandler
import json
import os
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('PegasusAudit')
        self.logger.setLevel(logging.INFO)
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Rotating file handler (max 10MB, keep 5 backups)
        handler = RotatingFileHandler(
            'logs/audit.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_search(self, target, source, success=True):
        """Log a search action"""
        self.logger.info(json.dumps({
            'action': 'search',
            'target': target[:6] + '****',  # Anonymize for privacy
            'source': source,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }))
    
    def log_api_call(self, endpoint, status_code):
        """Log an API call"""
        self.logger.info(json.dumps({
            'action': 'api_call',
            'endpoint': endpoint,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }))
    
    def log_error(self, error_type, message):
        """Log an error"""
        self.logger.error(json.dumps({
            'action': 'error',
            'type': error_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }))
    
    def log_database_operation(self, operation, table, success=True):
        """Log database operations"""
        self.logger.info(json.dumps({
            'action': 'database_operation',
            'operation': operation,
            'table': table,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }))

# Global audit logger instance
audit_logger = AuditLogger()