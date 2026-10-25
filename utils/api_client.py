"""
API Client for Real Tracking
Handles communication with external APIs for phone number and NIK lookup
"""

import requests
import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from colorama import Fore, Style

from config.api_config import (
    API_ENABLED, API_TIMEOUT, MAX_API_RETRIES,
    API_ENDPOINTS, API_KEYS, DATABASE_ENABLED,
    DATABASE_PATH, RATE_LIMIT_ENABLED, MAX_REQUESTS_PER_MINUTE,
    REQUEST_DELAY, CACHE_RESULTS, CACHE_DURATION
)

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_requests, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self):
        now = time.time()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        return len(self.requests) < self.max_requests
    
    def add_request(self):
        self.requests.append(time.time())

# Global rate limiter instance
rate_limiter = RateLimiter(MAX_REQUESTS_PER_MINUTE, 60)

class ResultCache:
    """Cache for API results"""
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < CACHE_DURATION:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, data):
        self.cache[key] = (data, time.time())
    
    def clear(self):
        self.cache.clear()

# Global cache instance
result_cache = ResultCache()


class APIClient:
    """Client for interacting with tracking APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pegasus-Lacak-Nomor/3.0',
            'Accept': 'application/json'
        })
        if API_KEYS.get('primary'):
            self.session.headers.update({
                'Authorization': f'Bearer {API_KEYS["primary"]}'
            })
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        if RATE_LIMIT_ENABLED and not rate_limiter.can_make_request():
            print(f"{Fore.YELLOW}[!] Rate limit reached. Waiting...{Style.RESET_ALL}")
            time.sleep(REQUEST_DELAY * 2)
            return None
        
        for attempt in range(MAX_API_RETRIES):
            try:
                response = self.session.get(
                    endpoint,
                    params=params,
                    timeout=API_TIMEOUT
                )
                
                if response.status_code == 200:
                    rate_limiter.add_request()
                    time.sleep(REQUEST_DELAY)
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    wait_time = int(response.headers.get('Retry-After', REQUEST_DELAY * 2))
                    print(f"{Fore.YELLOW}[!] Rate limited. Waiting {wait_time}s...{Style.RESET_ALL}")
                    time.sleep(wait_time)
                elif response.status_code == 401:  # Unauthorized
                    print(f"{Fore.RED}[!] API authentication failed. Check your API key.{Style.RESET_ALL}")
                    return None
                else:
                    print(f"{Fore.YELLOW}[!] API returned status {response.status_code}{Style.RESET_ALL}")
                    
            except requests.exceptions.Timeout:
                print(f"{Fore.YELLOW}[!] Request timeout (attempt {attempt + 1}/{MAX_API_RETRIES}){Style.RESET_ALL}")
            except requests.exceptions.ConnectionError:
                print(f"{Fore.YELLOW}[!] Connection error (attempt {attempt + 1}/{MAX_API_RETRIES}){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
            
            if attempt < MAX_API_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))
        
        return None
    
    def lookup_phone(self, phone_number: str) -> Optional[Dict]:
        """Lookup phone number information"""
        # Check cache first
        if CACHE_RESULTS:
            cached = result_cache.get(f"phone_{phone_number}")
            if cached:
                print(f"{Fore.CYAN}[i] Using cached data{Style.RESET_ALL}")
                return cached
        
        if not API_ENABLED or not API_KEYS.get('primary'):
            print(f"{Fore.YELLOW}[!] API not configured. Use API_KEYS in config/api_config.py{Style.RESET_ALL}")
            return None
        
        endpoint = API_ENDPOINTS.get('phone_lookup')
        if not endpoint:
            return None
        
        print(f"{Fore.CYAN}[*] Querying API for phone: {phone_number}{Style.RESET_ALL}")
        
        params = {'phone': phone_number}
        result = self._make_request(endpoint, params)
        
        if result and CACHE_RESULTS:
            result_cache.set(f"phone_{phone_number}", result)
        
        return result
    
    def lookup_nik(self, nik: str) -> Optional[Dict]:
        """Lookup NIK information"""
        # Check cache first
        if CACHE_RESULTS:
            cached = result_cache.get(f"nik_{nik}")
            if cached:
                print(f"{Fore.CYAN}[i] Using cached data{Style.RESET_ALL}")
                return cached
        
        if not API_ENABLED or not API_KEYS.get('primary'):
            print(f"{Fore.YELLOW}[!] API not configured. Use API_KEYS in config/api_config.py{Style.RESET_ALL}")
            return None
        
        endpoint = API_ENDPOINTS.get('nik_lookup')
        if not endpoint:
            return None
        
        print(f"{Fore.CYAN}[*] Querying API for NIK: {nik[:6]}****{Style.RESET_ALL}")
        
        params = {'nik': nik}
        result = self._make_request(endpoint, params)
        
        if result and CACHE_RESULTS:
            result_cache.set(f"nik_{nik}", result)
        
        return result
    
    def check_operator(self, phone_number: str) -> Optional[str]:
        """Check phone operator using real API or local validation"""
        # Try local validation first (fast and accurate for Indonesia)
        local_operator = self._check_operator_local(phone_number)
        if local_operator:
            return local_operator
        
        # If API enabled, try remote check
        if API_ENABLED and API_KEYS.get('primary'):
            endpoint = API_ENDPOINTS.get('operator_check')
            if endpoint:
                params = {'phone': phone_number}
                result = self._make_request(endpoint, params)
                if result and 'operator' in result:
                    return result['operator']
        
        return "Unknown"
    
    def _check_operator_local(self, phone_number: str) -> Optional[str]:
        """Check operator using local prefix database"""
        from config.settings import PHONE_OPERATORS
        if phone_number.startswith('08'):
            prefix = phone_number[:4]
            return PHONE_OPERATORS.get(prefix)
        return None


class DatabaseClient:
    """Client for local database queries"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.initialized = False
        if DATABASE_ENABLED:
            self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phone_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE NOT NULL,
                    name TEXT,
                    address TEXT,
                    city TEXT,
                    province TEXT,
                    operator TEXT,
                    last_updated TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nik_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nik TEXT UNIQUE NOT NULL,
                    name TEXT,
                    birth_date TEXT,
                    gender TEXT,
                    address TEXT,
                    city TEXT,
                    province TEXT,
                    last_updated TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            self.initialized = True
            print(f"{Fore.GREEN}[✓] Database initialized{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Database initialization error: {str(e)}{Style.RESET_ALL}")
            self.initialized = False
    
    def query_phone(self, phone_number: str) -> Optional[Dict]:
        """Query phone number from local database"""
        if not self.initialized:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM phone_records WHERE phone_number = ?',
                (phone_number,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'phone_number': row[1],
                    'name': row[2],
                    'address': row[3],
                    'city': row[4],
                    'province': row[5],
                    'operator': row[6],
                    'last_updated': row[7]
                }
        except Exception as e:
            print(f"{Fore.RED}[!] Database query error: {str(e)}{Style.RESET_ALL}")
        
        return None
    
    def query_nik(self, nik: str) -> Optional[Dict]:
        """Query NIK from local database"""
        if not self.initialized:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM nik_records WHERE nik = ?',
                (nik,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'nik': row[1],
                    'name': row[2],
                    'birth_date': row[3],
                    'gender': row[4],
                    'address': row[5],
                    'city': row[6],
                    'province': row[7],
                    'last_updated': row[8]
                }
        except Exception as e:
            print(f"{Fore.RED}[!] Database query error: {str(e)}{Style.RESET_ALL}")
        
        return None
    
    def add_phone_record(self, data: Dict) -> bool:
        """Add phone record to database"""
        if not self.initialized:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO phone_records 
                (phone_number, name, address, city, province, operator, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('phone_number'),
                data.get('name'),
                data.get('address'),
                data.get('city'),
                data.get('province'),
                data.get('operator'),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Error adding record: {str(e)}{Style.RESET_ALL}")
            return False


def perform_real_lookup(target: str, lookup_type: str = "auto") -> Optional[Dict]:
    """
    Perform real lookup using API or database
    
    Args:
        target: Phone number or NIK to lookup
        lookup_type: "phone", "nik", or "auto"
    
    Returns:
        Dict with result data or None if not found
    """
    api_client = APIClient()
    db_client = DatabaseClient()
    
    result = None
    
    # Determine lookup type
    if lookup_type == "auto":
        if target.startswith('08'):
            lookup_type = "phone"
        elif len(target) == 16:
            lookup_type = "nik"
        else:
            print(f"{Fore.RED}[!] Cannot determine lookup type{Style.RESET_ALL}")
            return None
    
    # Try database first (faster)
    if DATABASE_ENABLED:
        print(f"{Fore.CYAN}[*] Checking local database...{Style.RESET_ALL}")
        if lookup_type == "phone":
            result = db_client.query_phone(target)
        elif lookup_type == "nik":
            result = db_client.query_nik(target)
        
        if result:
            print(f"{Fore.GREEN}[✓] Found in local database{Style.RESET_ALL}")
            return result
    
    # Try API if database didn't return results
    if API_ENABLED and API_KEYS.get('primary'):
        print(f"{Fore.CYAN}[*] Querying remote API...{Style.RESET_ALL}")
        if lookup_type == "phone":
            result = api_client.lookup_phone(target)
        elif lookup_type == "nik":
            result = api_client.lookup_nik(target)
        
        if result:
            print(f"{Fore.GREEN}[✓] Found via API{Style.RESET_ALL}")
            return result
    
    # No results found
    if not result:
        print(f"{Fore.YELLOW}[!] No results from API or database{Style.RESET_ALL}")
    
    return result
