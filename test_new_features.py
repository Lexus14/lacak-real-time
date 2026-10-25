#!/usr/bin/env python3
"""
Test script for new features
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/home/engine/project')

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")
    
    try:
        from utils.history_manager import HistoryManager
        print("✓ HistoryManager imported successfully")
    except Exception as e:
        print(f"✗ HistoryManager import failed: {e}")
        return False
    
    try:
        from utils.logger import audit_logger
        print("✓ AuditLogger imported successfully")
    except Exception as e:
        print(f"✗ AuditLogger import failed: {e}")
        return False
    
    try:
        from utils.health_check import health_checker
        print("✓ HealthChecker imported successfully")
    except Exception as e:
        print(f"⚠ HealthChecker import failed (expected if requests not installed): {e}")
        # This is expected if requests is not installed, so don't fail the test
    
    try:
        from utils.input_validator import validator
        print("✓ InputValidator imported successfully")
    except Exception as e:
        print(f"✗ InputValidator import failed: {e}")
        return False
    
    try:
        from utils.backup_manager import backup_manager
        print("✓ BackupManager imported successfully")
    except Exception as e:
        print(f"⚠ BackupManager import failed (expected if colorama not installed): {e}")
        # This is expected if colorama is not installed, so don't fail the test
    
    return True

def test_history_manager():
    """Test HistoryManager functionality"""
    print("\nTesting HistoryManager...")
    
    from utils.history_manager import HistoryManager
    
    try:
        # Initialize
        hm = HistoryManager()
        print("✓ HistoryManager initialized")
        
        # Test add_search
        test_data = {"name": "Test User", "phone": "081234567890"}
        result = hm.add_search("081234567890", test_data, "Test note")
        if result:
            print("✓ add_search works")
        else:
            print("✗ add_search failed")
            return False
        
        # Test get_all_history
        history = hm.get_all_history()
        if len(history) > 0:
            print("✓ get_all_history works")
        else:
            print("✗ get_all_history returned empty")
            return False
        
        # Test add_favorite
        result = hm.add_favorite("081234567890", test_data, "Test favorite")
        if result:
            print("✓ add_favorite works")
        else:
            print("✗ add_favorite failed")
            return False
        
        # Test get_all_favorites
        favorites = hm.get_all_favorites()
        if len(favorites) > 0:
            print("✓ get_all_favorites works")
        else:
            print("✗ get_all_favorites returned empty")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ HistoryManager test failed: {e}")
        return False

def test_input_validator():
    """Test InputValidator functionality"""
    print("\nTesting InputValidator...")
    
    from utils.input_validator import validator
    
    try:
        # Test phone validation
        is_valid, target_type, result = validator.validate_target("081234567890")
        if is_valid and target_type == "phone":
            print("✓ Phone validation works")
        else:
            print("✗ Phone validation failed")
            return False
        
        # Test NIK validation
        is_valid, target_type, result = validator.validate_target("1234567890123456")
        if is_valid and target_type == "nik":
            print("✓ NIK validation works")
        else:
            print("✗ NIK validation failed")
            return False
        
        # Test invalid input
        is_valid, target_type, result = validator.validate_target("invalid")
        if not is_valid:
            print("✓ Invalid input detection works")
        else:
            print("✗ Invalid input detection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ InputValidator test failed: {e}")
        return False

def test_audit_logger():
    """Test AuditLogger functionality"""
    print("\nTesting AuditLogger...")
    
    from utils.logger import audit_logger
    
    try:
        # Test log_search
        audit_logger.log_search("081234567890", "API", True)
        print("✓ log_search works")
        
        # Test log_error
        audit_logger.log_error("TestError", "This is a test error")
        print("✓ log_error works")
        
        return True
        
    except Exception as e:
        print(f"✗ AuditLogger test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running tests for new features...\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test individual components
    if not test_history_manager():
        all_passed = False
    
    if not test_input_validator():
        all_passed = False
    
    if not test_audit_logger():
        all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print(f"{'='*50}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)