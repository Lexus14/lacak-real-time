# Quick Start Guide - Pegasus Lacak Nomor v2.0

## 🚀 Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the program
python main.py

# 3. Login with password
Password: Sobri
```

## 📋 Menu Options

After login, you'll see 5 menu options:

### 1️⃣ Pencarian Tunggal (Single Search)
- Search one phone number or NIK
- View detailed results
- Option to export results

**Example**:
```
Enter: 081234567890
or
Enter: 1234567890123456
```

### 2️⃣ Pencarian Batch (Batch Search)
- Search multiple numbers at once
- Create `batch_search.txt` with one number per line
- Auto-export all results

**Example batch_search.txt**:
```
081234567890
082345678901
1234567890123456
```

### 3️⃣ Lihat History (View History)
- See all searches from current session
- Shows target, timestamp, and basic info
- Maximum 50 entries

### 4️⃣ Lihat Statistik (View Statistics)
- Total searches
- Phone vs NIK breakdown
- First and last search timestamps

### 5️⃣ Keluar (Exit)
- Exit the program

## 💾 Export Formats

After single search, choose export format:

| Format | Use Case | Location |
|--------|----------|----------|
| JSON | API integration, data processing | exports/result_*.json |
| CSV | Excel/spreadsheet analysis | exports/result_*.csv |
| TXT | Simple documentation | exports/result_*.txt |

## 📁 File Structure

```
pegasus-lacak-nomor/
├── main.py              # ⭐ Main program (run this)
├── batch_search.txt     # 📝 Batch input (edit this)
├── exports/             # 💾 Export results (auto-created)
├── config/
│   └── settings.py      # ⚙️ Configuration
├── data/
│   └── sample_data.py   # 📊 Sample data
└── utils/
    └── helpers.py       # 🔧 Helper functions
```

## ⚙️ Configuration

Edit `config/settings.py` to customize:

```python
ACTIVATION_PASSWORD = "Sobri"    # Change password
MAX_HISTORY_ITEMS = 50           # History limit
MAX_BATCH_SIZE = 100             # Batch size limit
EXPORT_DIR = "exports"           # Export directory
```

## 🎯 Common Tasks

### Search a Single Number
```
1. Run: python main.py
2. Enter password: Sobri
3. Select: 1
4. Enter number: 081234567890
5. View results
6. Export if needed (y/n)
```

### Batch Search Multiple Numbers
```
1. Edit batch_search.txt:
   081234567890
   082345678901
   083456789012
2. Run: python main.py
3. Enter password: Sobri
4. Select: 2
5. Wait for processing
6. All results auto-exported
```

### View Your Search History
```
1. Run: python main.py
2. Enter password: Sobri
3. Select: 3
4. View all past searches
```

### Check Statistics
```
1. Run: python main.py
2. Enter password: Sobri
3. Select: 4
4. View statistics
```

## 🧪 Testing

Run the test suite:
```bash
python test_features.py
```

Should show:
```
✓ ALL TESTS PASSED!
```

## ❓ Troubleshooting

### Problem: Module not found
**Solution**: 
```bash
pip install -r requirements.txt
```

### Problem: Permission denied on exports/
**Solution**: 
```bash
chmod 755 exports/
```

### Problem: Can't find batch_search.txt
**Solution**: 
```bash
# Create the file in project root
touch batch_search.txt
echo "081234567890" > batch_search.txt
```

### Problem: Wrong password
**Solution**: Default password is "Sobri" (case-sensitive)

## 🆕 What's New in v2.0

✨ **5 New Features**:
1. Export results (JSON/CSV/TXT)
2. Search history tracking
3. Batch search from file
4. Statistics dashboard
5. Interactive menu system

🐛 **Bug Fixes**:
- Fixed missing `sys` import

## 📞 Support

- Check README.md for detailed documentation
- See CHANGELOG.md for version history
- Run test_features.py to verify installation

## ⚠️ Important Notes

1. This is a demonstration tool
2. Data displayed is randomly generated
3. For educational purposes only
4. Password: "Sobri" (case-sensitive)

## 🎓 Quick Examples

**Search phone number**:
```
Menu: 1
Input: 081234567890
Export: y
Format: 1 (JSON)
```

**Batch search**:
```
Menu: 2
(Will process batch_search.txt)
Export all: y
```

**View stats**:
```
Menu: 4
(Shows all statistics)
```

---

**Version**: 2.0  
**Last Updated**: October 2025  
**Author**: Letda Kes dr. Sobri
