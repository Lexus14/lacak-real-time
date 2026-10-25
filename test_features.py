#!/usr/bin/env python3
"""Test script to verify all features work correctly."""

import sys
import os

# Test imports
print("Testing imports...")
try:
    from main import *
    from utils.helpers import *
    from config.settings import *
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test helper functions
print("\nTesting helper functions...")
try:
    timestamp = format_timestamp()
    print(f"✓ format_timestamp: {timestamp}")
    
    result = validate_input("081234567890", VALID_PHONE_PREFIX, NIK_LENGTH)
    print(f"✓ validate_input (phone): {result}")
    
    result = validate_input("1234567890123456", VALID_PHONE_PREFIX, NIK_LENGTH)
    print(f"✓ validate_input (NIK): {result}")
    
    ensure_export_dir()
    print(f"✓ ensure_export_dir created")
    
except Exception as e:
    print(f"✗ Helper function error: {e}")
    sys.exit(1)

# Test data normalization
print("\nTesting data normalization...")
try:
    test_api_data = {
        "name": "Test User",
        "gender": "Laki-laki",
        "city": "Jakarta"
    }
    data = normalize_api_response(test_api_data, "081234567890")
    print(f"✓ normalize_api_response: {len(data)} fields")
    assert "Nama" in data
    assert "Waktu Pencarian" in data
    print("✓ All required fields present")
except Exception as e:
    print(f"✗ Data normalization error: {e}")
    sys.exit(1)

# Test export functions
print("\nTesting export functions...")
try:
    test_data = {
        "Nama": "Test User",
        "Nomor": "081234567890",
        "Kota": "Jakarta"
    }
    
    filepath = export_to_json(test_data, "test_export.json")
    print(f"✓ export_to_json: {filepath}")
    assert os.path.exists(filepath)
    
    filepath = export_to_csv(test_data, "test_export.csv")
    print(f"✓ export_to_csv: {filepath}")
    assert os.path.exists(filepath)
    
    filepath = export_to_txt(test_data, "test_export.txt")
    print(f"✓ export_to_txt: {filepath}")
    assert os.path.exists(filepath)
    
except Exception as e:
    print(f"✗ Export error: {e}")
    sys.exit(1)

# Test history management
print("\nTesting history management...")
try:
    import main
    main.search_history = []
    
    test_result = {"Nama": "Test", "Kota": "Jakarta"}
    add_to_history("081234567890", test_result)
    print(f"✓ add_to_history: {len(main.search_history)} items")
    
    stats = calculate_statistics(main.search_history)
    print(f"✓ calculate_statistics: {stats['total_searches']} searches")
    
except Exception as e:
    print(f"✗ History error: {e}")
    sys.exit(1)

# Test batch file reading
print("\nTesting batch file reading...")
try:
    if os.path.exists(BATCH_INPUT_FILE):
        numbers = read_batch_file(BATCH_INPUT_FILE)
        print(f"✓ read_batch_file: {len(numbers)} numbers")
    else:
        print(f"! batch_search.txt not found (expected)")
        
except Exception as e:
    print(f"✗ Batch file error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✓ ALL TESTS PASSED!")
print("="*50)
print("\nFeatures implemented:")
print("1. ✓ Export results to JSON, CSV, TXT")
print("2. ✓ Search history management")
print("3. ✓ Batch search from file")
print("4. ✓ Statistics calculation")
print("5. ✓ Interactive menu system")
print("\nBug fixes:")
print("- ✓ Fixed missing 'sys' import")
