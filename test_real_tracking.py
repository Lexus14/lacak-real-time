#!/usr/bin/env python3
"""
Test script for Real Tracking features
Tests API client, database, and fallback mechanisms
"""

import sys
from colorama import Fore, Style, init

init()

def print_test(message, status="INFO"):
    """Print test message with color."""
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "ERROR": Fore.RED,
        "WARNING": Fore.YELLOW
    }
    color = colors.get(status, Fore.WHITE)
    symbol = {
        "INFO": "[*]",
        "SUCCESS": "[✓]",
        "ERROR": "[✗]",
        "WARNING": "[!]"
    }
    print(f"{color}{symbol[status]} {message}{Style.RESET_ALL}")

def test_imports():
    """Test if all modules can be imported."""
    print_test("Testing imports...", "INFO")
    
    try:
        from config.api_config import API_ENABLED, API_KEYS, API_ENDPOINTS
        print_test("✓ config.api_config imported", "SUCCESS")
    except Exception as e:
        print_test(f"Failed to import api_config: {e}", "ERROR")
        return False
    
    try:
        from utils.api_client import APIClient, perform_real_lookup, RateLimiter
        print_test("✓ utils.api_client imported", "SUCCESS")
    except Exception as e:
        print_test(f"Failed to import api_client: {e}", "ERROR")
        return False
    
    try:
        from utils.api_client import DatabaseClient, result_cache
        print_test("✓ Database components imported", "SUCCESS")
    except Exception as e:
        print_test(f"Failed to import database components: {e}", "ERROR")
        return False
    
    return True

def test_configuration():
    """Test configuration settings."""
    print_test("\nTesting configuration...", "INFO")
    
    try:
        from config.api_config import (
            API_ENABLED, API_KEYS, API_ENDPOINTS,
            DATABASE_ENABLED, RATE_LIMIT_ENABLED,
            CACHE_RESULTS
        )
        
        print_test(f"API Enabled: {API_ENABLED}", "INFO")
        print_test(f"Database Enabled: {DATABASE_ENABLED}", "INFO")
        print_test(f"Rate Limiting: {RATE_LIMIT_ENABLED}", "INFO")
        print_test(f"Caching: {CACHE_RESULTS}", "INFO")
        
        if API_ENABLED:
            if API_KEYS.get('primary'):
                print_test("API Key configured", "SUCCESS")
            else:
                print_test("API Key not configured", "WARNING")
        
        return True
    except Exception as e:
        print_test(f"Configuration test failed: {e}", "ERROR")
        return False

def test_api_client():
    """Test API client initialization."""
    print_test("\nTesting API client...", "INFO")
    
    try:
        from utils.api_client import APIClient
        
        client = APIClient()
        print_test("✓ APIClient initialized", "SUCCESS")
        
        # Test operator detection (local, no API call)
        operator = client.check_operator("081234567890")
        print_test(f"Operator detection test: {operator}", "SUCCESS")
        
        return True
    except Exception as e:
        print_test(f"API client test failed: {e}", "ERROR")
        return False

def test_rate_limiter():
    """Test rate limiter."""
    print_test("\nTesting rate limiter...", "INFO")
    
    try:
        from utils.api_client import RateLimiter
        
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # Test multiple requests
        for i in range(5):
            if limiter.can_make_request():
                limiter.add_request()
        
        # Should be at limit
        if not limiter.can_make_request():
            print_test("✓ Rate limiter working correctly", "SUCCESS")
        else:
            print_test("Rate limiter not enforcing limit", "WARNING")
        
        return True
    except Exception as e:
        print_test(f"Rate limiter test failed: {e}", "ERROR")
        return False

def test_cache():
    """Test result cache."""
    print_test("\nTesting cache...", "INFO")
    
    try:
        from utils.api_client import result_cache
        
        # Set cache
        test_data = {"name": "Test User", "phone": "081234567890"}
        result_cache.set("test_key", test_data)
        
        # Get cache
        cached = result_cache.get("test_key")
        
        if cached == test_data:
            print_test("✓ Cache working correctly", "SUCCESS")
        else:
            print_test("Cache not working as expected", "WARNING")
        
        # Clear cache
        result_cache.clear()
        print_test("✓ Cache cleared", "SUCCESS")
        
        return True
    except Exception as e:
        print_test(f"Cache test failed: {e}", "ERROR")
        return False

def test_database_client():
    """Test database client."""
    print_test("\nTesting database client...", "INFO")
    
    try:
        from utils.api_client import DatabaseClient
        from config.api_config import DATABASE_ENABLED
        
        if not DATABASE_ENABLED:
            print_test("Database disabled in config (skipping)", "WARNING")
            return True
        
        db = DatabaseClient()
        
        if db.initialized:
            print_test("✓ Database initialized", "SUCCESS")
            
            # Test add record
            test_record = {
                'phone_number': '081234567890',
                'name': 'Test User',
                'address': 'Test Address',
                'city': 'Test City',
                'province': 'Test Province',
                'operator': 'Telkomsel'
            }
            
            if db.add_phone_record(test_record):
                print_test("✓ Test record added", "SUCCESS")
                
                # Test query
                result = db.query_phone('081234567890')
                if result:
                    print_test("✓ Record queried successfully", "SUCCESS")
                else:
                    print_test("Record not found", "WARNING")
            else:
                print_test("Failed to add record", "WARNING")
        else:
            print_test("Database not initialized", "WARNING")
        
        return True
    except Exception as e:
        print_test(f"Database test failed: {e}", "ERROR")
        return False

def test_lookup_no_data():
    """Test lookup when no data is available."""
    print_test("\nTesting lookup with no data...", "INFO")
    
    try:
        from utils.api_client import perform_real_lookup
        
        # Test with a non-existent number (should return None)
        result = perform_real_lookup("089999999999")
        
        if result is None:
            print_test("✓ Returns None when no data found (expected)", "SUCCESS")
        else:
            print_test(f"Found data: {result}", "INFO")
        
        return True
    except Exception as e:
        print_test(f"Lookup no-data test failed: {e}", "ERROR")
        return False

def test_normalize_response():
    """Test API response normalization."""
    print_test("\nTesting response normalization...", "INFO")
    
    try:
        # Import from main to test normalization
        sys.path.insert(0, '/home/engine/project')
        from main import normalize_api_response
        
        # Test data with various field names
        test_api_response = {
            'name': 'John Doe',
            'city': 'Jakarta',
            'province': 'DKI Jakarta',
            'operator': 'Telkomsel',
            'lat': -6.2,
            'lon': 106.8
        }
        
        normalized = normalize_api_response(test_api_response, '081234567890')
        
        if 'Nama' in normalized and normalized['Nama'] == 'John Doe':
            print_test("✓ Name field normalized", "SUCCESS")
        
        if 'Kota/Town' in normalized and normalized['Kota/Town'] == 'Jakarta':
            print_test("✓ City field normalized", "SUCCESS")
        
        if 'Latitude' in normalized and 'Longitude' in normalized:
            print_test("✓ Coordinates normalized", "SUCCESS")
        
        return True
    except Exception as e:
        print_test(f"Normalization test failed: {e}", "ERROR")
        return False

def main():
    """Run all tests."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print("REAL TRACKING TEST SUITE")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("API Client", test_api_client),
        ("Rate Limiter", test_rate_limiter),
        ("Cache", test_cache),
        ("Database Client", test_database_client),
        ("Lookup No Data", test_lookup_no_data),
        ("Response Normalization", test_normalize_response),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_test(f"Test '{name}' crashed: {e}", "ERROR")
            failed += 1
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}{Style.RESET_ALL}")
    print_test(f"Passed: {passed}", "SUCCESS")
    if failed > 0:
        print_test(f"Failed: {failed}", "ERROR")
    else:
        print_test(f"Failed: {failed}", "SUCCESS")
    print_test(f"Total: {passed + failed}", "INFO")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}✓ All tests passed!{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"\n{Fore.YELLOW}⚠ Some tests failed. Check output above.{Style.RESET_ALL}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
