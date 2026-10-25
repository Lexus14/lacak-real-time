"""
API Health Check and Monitoring
Checks API availability and provides uptime statistics
"""

import requests
import time
from datetime import datetime
from colorama import Fore, Style

from config.api_config import API_ENABLED, API_ENDPOINTS

class APIHealthChecker:
    def __init__(self):
        self.last_check = None
        self.status = {}
    
    def check_api_health(self, silent=False):
        """Check if API is reachable"""
        if not API_ENABLED:
            if not silent:
                print_colored("[INFO] API disabled - using database only", "INFO")
            return True
        
        endpoint = API_ENDPOINTS.get('phone_lookup')
        if not endpoint:
            if not silent:
                print_colored("[!] No API endpoint configured", "ERROR")
            return False
        
        try:
            # Ping endpoint (HEAD request faster than GET)
            response = requests.head(endpoint, timeout=5)
            is_healthy = response.status_code < 500
            
            self.status = {
                'healthy': is_healthy,
                'status_code': response.status_code,
                'last_check': time.time()
            }
            
            if not silent:
                if is_healthy:
                    print_colored("[✓] API Status: Healthy", "SUCCESS")
                else:
                    print_colored(f"[!] API Status: Unhealthy (Code: {response.status_code})", "ERROR")
            
            return is_healthy
            
        except requests.exceptions.ConnectionError:
            if not silent:
                print_colored("[!] API Status: Cannot connect", "ERROR")
            return False
        except requests.exceptions.Timeout:
            if not silent:
                print_colored("[!] API Status: Timeout", "WARNING")
            return False
        except Exception as e:
            if not silent:
                print_colored(f"[!] API Status: Error - {str(e)}", "ERROR")
            return False
    
    def get_uptime_stats(self):
        """Get API uptime statistics"""
        # This would query audit logs to calculate uptime
        # For now, return basic info
        if not self.status:
            return {
                'last_check': None,
                'healthy': False,
                'message': 'No health check performed yet'
            }
        
        return {
            'last_check': datetime.fromtimestamp(self.status['last_check']).strftime('%Y-%m-%d %H:%M:%S'),
            'healthy': self.status['healthy'],
            'status_code': self.status.get('status_code')
        }
    
    def check_database_health(self):
        """Check if database is accessible"""
        try:
            import sqlite3
            from config.api_config import DATABASE_ENABLED, DATABASE_PATH
            
            if not DATABASE_ENABLED:
                return True
            
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Test query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                print_colored("[✓] Database Status: Healthy", "SUCCESS")
                return True
            else:
                print_colored("[!] Database Status: Unhealthy", "ERROR")
                return False
                
        except Exception as e:
            print_colored(f"[!] Database Status: Error - {str(e)}", "ERROR")
            return False

# Helper function to use in main.py
def print_colored(message, color_type="INFO"):
    """Helper function for colored output"""
    from colorama import Fore, Style
    from config.settings import COLORS
    
    color = getattr(Fore, COLORS.get(color_type, "WHITE").upper())
    print(f"{color}{message}{Style.RESET_ALL}")

# Global health checker instance
health_checker = APIHealthChecker()