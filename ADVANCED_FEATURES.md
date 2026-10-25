# Pegasus Lacak Nomor - Advanced Features

This document describes the advanced features implemented in Pegasus Lacak Nomor v3.0.

## Table of Contents

1. [Multi-User System with RBAC](#1-multi-user-system-with-rbac)
2. [Real-Time Analytics Dashboard](#2-real-time-analytics-dashboard)
3. [Machine Learning Anomaly Detection](#3-machine-learning-anomaly-detection)
4. [Geospatial Analysis & Visualization](#4-geospatial-analysis--visualization)
5. [Web API & REST Interface](#5-web-api--rest-interface)
6. [Scheduled Tasks & Automation](#6-scheduled-tasks--automation)
7. [Advanced Export & Reporting](#7-advanced-export--reporting)

---

## 1. Multi-User System with RBAC

Transformasi dari single-user app menjadi multi-user platform dengan granular permissions.

### Features
- **User Roles**: Admin, Operator, Viewer, Auditor
- **Granular Permissions**: Setiap role memiliki permission set yang berbeda
- **Secure Authentication**: Password hashing dengan salt (PBKDF2)
- **Session Management**: Token-based authentication

### User Roles

| Role | Permissions |
|------|-------------|
| Admin | All permissions (MANAGE_USERS, CONFIGURE_API, dll) |
| Operator | SEARCH_PHONE, SEARCH_NIK, EXPORT_DATA, VIEW_HISTORY |
| Viewer | VIEW_HISTORY, VIEW_AUDIT_LOG |
| Auditor | VIEW_HISTORY, VIEW_AUDIT_LOG, EXPORT_DATA |

### Default Credentials
- Username: `admin`
- Password: `user5354`

### Menu Access
**Menu**: 18. User Management (Admin)

### Usage
```python
from managers.user_manager import UserManager
from models.user import UserRole

user_manager = UserManager()

# Login
user_manager.authenticate("admin", "user5354")

# Create new user (admin only)
user_manager.create_user("operator1", "password", UserRole.OPERATOR)

# Check permission
if user_manager.current_user.has_permission(Permission.SEARCH_PHONE):
    # Perform search
    pass
```

---

## 2. Real-Time Analytics Dashboard

Dashboard interaktif untuk monitoring search activities, API usage, dan trends secara real-time.

### Features
- **Real-time Metrics**: Searches per hour/day, success rates
- **Visual Charts**: ASCII trend charts and bar charts
- **Location Analytics**: Top searched cities
- **Operator Distribution**: Search distribution by telecom operator
- **Weekly Reports**: Comprehensive weekly analytics

### Menu Access
**Menu**: 19. Analytics Dashboard

### Key Metrics
- Total searches (last hour, today, all time)
- Unique targets
- API success rate
- Phone vs NIK search distribution
- Top cities and operators

### Usage
```python
from analytics.dashboard import AnalyticsDashboard

dashboard = AnalyticsDashboard()

# Display dashboard
dashboard.display_dashboard()

# Get stats
stats = dashboard.get_realtime_stats()

# Generate weekly report
dashboard.generate_weekly_report()
```

---

## 3. Machine Learning Anomaly Detection

Detect suspicious patterns, fraud attempts, atau unusual behavior menggunakan machine learning.

### Features
- **Pattern Detection**: Rapid-fire searches, unusual times, repeated targets
- **Geographic Anomalies**: Sudden location jumps
- **Risk Level Assessment**: MINIMAL, LOW, MEDIUM, HIGH
- **Rule-based Detection**: Lightweight alternative to sklearn

### Anomaly Patterns Detected
1. **Rapid-fire searches**: >10 searches dalam 1 menit
2. **Unusual times**: Searches between 2-5 AM
3. **Repeated targets**: Same target searched >5 times
4. **Geographic anomalies**: Too many different locations
5. **High volume**: >100 searches dalam 24 jam

### Menu Access
**Menu**: 20. Anomaly Detection

### Usage
```python
from ml.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()

# Train model (need 50+ searches)
detector.train()

# Detect anomaly in search
is_anomaly, confidence, reasons = detector.detect_anomaly(search_entry)

# Generate report
report = detector.generate_report()
print(f"Risk Level: {report['risk_level']}")
```

---

## 4. Geospatial Analysis & Visualization

Visualisasi lokasi searches pada map, heat maps, clustering, dan geographic insights.

### Features
- **Heatmap Generation**: Visual density map of search locations
- **Cluster Map**: Grouped markers for better visualization
- **Geographic Clustering**: DBSCAN-based clustering
- **Search Radius Calculation**: Geographic coverage analysis
- **Location Statistics**: City/province distribution

### Output Formats
- **HTML Heatmap**: Interactive Leaflet heatmap
- **HTML Cluster Map**: Marker cluster visualization
- **Statistics Report**: Console-based location stats

### Menu Access
**Menu**: 21. Geospatial Analysis

### Usage
```python
from geo.geospatial_analyzer import GeospatialAnalyzer

analyzer = GeospatialAnalyzer()

# Create heatmap
analyzer.create_heatmap_html("exports/heatmap.html")

# Create cluster map
analyzer.create_cluster_map_html("exports/cluster_map.html")

# Detect clusters
clusters = analyzer.detect_geographic_clusters()

# Calculate search radius
radius = analyzer.calculate_search_radius()
```

---

## 5. Web API & REST Interface

Expose aplikasi functionality via REST API untuk integration dengan systems lain.

### Features
- **JWT-like Authentication**: Token-based auth
- **Role-based Access Control**: Permission checking per endpoint
- **Multiple Endpoints**: Search, history, analytics, users
- **CORS Support**: Cross-origin requests enabled
- **Health Check**: System status endpoint

### API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/health` | GET | Health check | No |
| `/api/v1/auth/login` | POST | User login | No |
| `/api/v1/search/phone` | POST | Search by phone | Yes |
| `/api/v1/search/nik` | POST | Search by NIK | Yes |
| `/api/v1/history` | GET | Get search history | Yes |
| `/api/v1/analytics/stats` | GET | Real-time stats | Yes |
| `/api/v1/analytics/trends` | GET | Hourly trends | Yes |
| `/api/v1/analytics/anomalies` | GET | Anomaly report | Yes |
| `/api/v1/users` | GET | List users | Admin only |
| `/api/v1/users` | POST | Create user | Admin only |

### Menu Access
**Menu**: 24. Start API Server

### Usage

Start server:
```bash
python api/server.py
```

Or from menu:
1. Select menu 24
2. Enter host (default: 0.0.0.0)
3. Enter port (default: 5000)

API Example:
```bash
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "user5354"}'

# Search phone
curl -X POST http://localhost:5000/api/v1/search/phone \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "081234567890"}'

# Get stats
curl -X GET http://localhost:5000/api/v1/analytics/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Installation
```bash
pip install flask flask-cors
```

---

## 6. Scheduled Tasks & Automation

Automated tasks seperti scheduled reports, data cleanup, backups, dan monitoring.

### Features
- **Daily Backup**: Automated at 2:00 AM
- **Weekly Report**: Generated every Monday at 9:00 AM
- **Hourly Health Check**: Continuous monitoring
- **Data Cleanup**: Remove old data (90+ days) at 3:00 AM
- **Manual Trigger**: Run tasks on demand

### Schedule

| Task | Frequency | Time |
|------|-----------|------|
| Daily Backup | Daily | 02:00 |
| Weekly Report | Weekly (Monday) | 09:00 |
| Health Check | Hourly | Every hour |
| Data Cleanup | Daily | 03:00 |

### Menu Access
**Menu**: 23. Automation & Scheduler

### Usage

From menu:
1. Select menu 23
2. Choose action (Start/Stop scheduler or run tasks)

From code:
```python
from automation.scheduler import TaskScheduler

scheduler = TaskScheduler()
scheduler.start()

# Run task manually
scheduler.run_task_now('backup')
scheduler.run_task_now('report')
scheduler.run_task_now('cleanup')
```

### Installation
```bash
pip install schedule
```

---

## 7. Advanced Export & Reporting

Professional reports dengan charts, graphs, PDF generation, Excel dengan formulas.

### Features
- **PDF Reports**: Professional formatted documents
- **Excel Reports**: Charts, formulas, multiple sheets
- **HTML Reports**: Interactive web-based reports
- **Visual Charts**: Bar charts, pie charts
- **Statistics Summary**: Comprehensive metrics

### Report Formats

| Format | Features | Dependencies |
|--------|----------|--------------|
| PDF | Tables, professional layout | reportlab |
| Excel | Charts, formulas, styling | openpyxl |
| HTML | Interactive, styled | None |

### Menu Access
**Menu**: 22. Advanced Reporting

### Usage
```python
from reporting.advanced_exporter import AdvancedExporter

exporter = AdvancedExporter()

# Export to PDF
exporter.export_to_pdf(search_history, "report.pdf")

# Export to Excel
exporter.export_to_excel_advanced(search_history, "report.xlsx")

# Export to HTML
exporter.export_to_html_report(search_history, "report.html")

# Generate all formats
from reporting.advanced_exporter import generate_professional_report
generate_professional_report(search_history, 'all')
```

### Installation
```bash
# For PDF support
pip install reportlab

# For Excel support
pip install openpyxl

# For charts
pip install matplotlib

# Install all
pip install reportlab openpyxl matplotlib
```

---

## Installation

### Basic Installation (Core Features)
```bash
pip install -r requirements.txt
```

### Advanced Installation (All Features)
```bash
pip install -r requirements-advanced.txt
```

### Optional Dependencies (Selective)
```bash
# API Server
pip install flask flask-cors

# Scheduled Tasks
pip install schedule

# Advanced Reporting
pip install reportlab openpyxl

# Charts
pip install matplotlib

# Geospatial
pip install folium
```

---

## Configuration

### Multi-User System
- Database: `data/users.db`
- Default admin: `admin/user5354`

### Analytics Dashboard
- Uses existing search history database: `data/app_data.db`

### API Server
- Default host: `0.0.0.0`
- Default port: `5000`

### Scheduler
- Runs in background thread
- Tasks persist until application exit

---

## Security Notes

1. **Change Default Password**: Immediately change admin password after first login
2. **API Keys**: Store API keys securely, don't commit to version control
3. **User Permissions**: Follow principle of least privilege
4. **Audit Logging**: All searches and user actions are logged
5. **Session Tokens**: Tokens are generated per-login and not persisted

---

## Troubleshooting

### Feature Not Available
If you see "[!] Feature not available", install the required dependencies:
```bash
pip install -r requirements-advanced.txt
```

### API Server Won't Start
Make sure Flask is installed:
```bash
pip install flask flask-cors
```

### Scheduler Not Working
Install schedule library:
```bash
pip install schedule
```

### PDF/Excel Export Fails
Install reporting libraries:
```bash
pip install reportlab openpyxl
```

---

## License

This project is for educational and authorized tracking purposes only. Ensure compliance with local privacy laws and regulations.
