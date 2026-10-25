# Changelog - Pegasus Lacak Nomor

## Version 2.0 - Bug Fixes and New Features

### 🐛 Bug Fixes

1. **Fixed missing `sys` import in main.py**
   - Error: `NameError: name 'sys' is not defined`
   - Impact: Program crashed when using `sys.exit()` and `sys.stdout`
   - Fix: Added `import sys` at the top of main.py
   - Files modified: `main.py`

### ✨ New Features

#### 1. Export Hasil Pencarian (Search Result Export)
- **Description**: Export search results to multiple file formats
- **Formats supported**:
  - JSON: Structured data format for integration
  - CSV: Spreadsheet format for analysis
  - TXT: Simple text format for documentation
- **Features**:
  - Automatic timestamp in filename
  - Auto-creates `exports/` directory
  - Clean formatting for each format
- **Files added/modified**:
  - `utils/helpers.py`: Added `export_to_json()`, `export_to_csv()`, `export_to_txt()`, `ensure_export_dir()`
  - `main.py`: Added `export_result()` function
  - `config/settings.py`: Added `EXPORT_DIR`, `EXPORT_FORMATS`

#### 2. History Pencarian (Search History)
- **Description**: Track and display search history within a session
- **Features**:
  - Stores up to 50 searches (configurable)
  - Displays target, timestamp, and key results
  - Shows total number of searches
  - FIFO (First In First Out) when limit reached
- **Files added/modified**:
  - `main.py`: Added `search_history` global, `add_to_history()`, `show_history()`
  - `config/settings.py`: Added `MAX_HISTORY_ITEMS`

#### 3. Pencarian Batch (Batch Search)
- **Description**: Search multiple phone numbers or NIKs from a file
- **Features**:
  - Read numbers from `batch_search.txt`
  - Process up to 100 numbers per batch (configurable)
  - Progress tracking for each number
  - Skip invalid numbers with error message
  - Auto-export all results to JSON
  - Add all results to history
- **Files added/modified**:
  - `utils/helpers.py`: Added `read_batch_file()`
  - `main.py`: Added `batch_search()` function
  - `config/settings.py`: Added `BATCH_INPUT_FILE`, `MAX_BATCH_SIZE`
  - `batch_search.txt`: Created sample batch file

#### 4. Statistik Dashboard (Statistics Dashboard)
- **Description**: Display comprehensive statistics about searches
- **Metrics displayed**:
  - Total searches performed
  - Number of phone number searches
  - Number of NIK searches
  - First search timestamp
  - Last search timestamp
- **Files added/modified**:
  - `utils/helpers.py`: Added `calculate_statistics()`
  - `main.py`: Added `show_statistics()` function

#### 5. Menu Interaktif (Interactive Menu)
- **Description**: User-friendly menu system for navigation
- **Features**:
  - 5 menu options: Single Search, Batch Search, History, Statistics, Exit
  - Clear menu display with colored output
  - Input validation
  - Easy navigation with numbers
  - Return to menu after each action
- **Files modified**:
  - `main.py`: Complete refactor of `main()`, added `show_menu()`, `single_search()`
  - Banner updated to v2.0

### 📁 Files Changed

#### New Files
- `batch_search.txt` - Sample batch input file
- `.gitignore` - Git ignore rules
- `test_features.py` - Automated test script
- `CHANGELOG.md` - This file

#### Modified Files
- `main.py` - Major refactor with new features
- `config/settings.py` - Added new configuration options
- `utils/helpers.py` - Added export, batch, and statistics functions
- `README.md` - Updated documentation with new features

### 🧪 Testing

All features have been tested with `test_features.py`:
- ✅ All imports successful
- ✅ Helper functions working
- ✅ Data generation working
- ✅ Export to JSON, CSV, TXT working
- ✅ History management working
- ✅ Statistics calculation working
- ✅ Batch file reading working

### 📊 Statistics

- **Lines of code added**: ~250+
- **New functions**: 10+
- **Configuration options added**: 6
- **File formats supported**: 3 (JSON, CSV, TXT)
- **Bug fixes**: 1 critical (missing sys import)

### 🔄 Migration Notes

For users upgrading from v1.0 to v2.0:
1. No breaking changes - all v1.0 functionality preserved
2. New dependencies: None (uses existing libraries)
3. New files created automatically: `exports/` directory
4. Optional: Create `batch_search.txt` for batch search feature
5. Password and settings remain the same

### 📝 Usage Examples

#### Export Example
```
After single search, choose 'y' to export
Select format: 1 (JSON), 2 (CSV), or 3 (TXT)
File saved to: exports/result_08123456_2025-10-28_22-09-39.json
```

#### Batch Search Example
```
Create batch_search.txt with:
081234567890
082345678901
1234567890123456

Select Menu 2 (Batch Search)
Program processes all numbers and exports results
```

#### History Example
```
Select Menu 3 (History)
View all searches with timestamps and basic info
Shows last 50 searches
```

#### Statistics Example
```
Select Menu 4 (Statistics)
View total searches, breakdown by type, and timestamps
```

### 🎯 Future Enhancements (Roadmap)

Potential features for v3.0:
- Persistent history (save to database/file)
- Advanced search filters
- Email/SMS notification
- API integration
- Multi-language support
- Custom data sources
- Advanced statistics and charts
- Search result comparison
