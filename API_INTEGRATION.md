# API Integration Guide

## Overview

Pegasus Lacak Nomor v3.0 sekarang mendukung integrasi dengan API eksternal untuk real tracking. Dokumen ini menjelaskan cara mengintegrasikan aplikasi dengan berbagai API provider.

## Architecture

```
┌─────────────────┐
│   Main App      │
│   (main.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Client     │ ◄─── Rate Limiter
│(api_client.py)  │ ◄─── Result Cache
└────────┬────────┘
         │
         ├─────────► External API (HTTP/HTTPS)
         │
         └─────────► Local Database (SQLite)
```

## Quick Start

### 1. Enable Real Tracking

Edit `config/api_config.py`:

```python
API_ENABLED = True
API_KEYS = {
    "primary": "your_api_key_here"
}
```

### 2. Configure Endpoints

```python
API_ENDPOINTS = {
    "phone_lookup": "https://api.yourprovider.com/phone",
    "nik_lookup": "https://api.yourprovider.com/nik"
}
```

### 3. Test Connection

```python
from utils.api_client import APIClient

client = APIClient()
result = client.lookup_phone("081234567890")
print(result)
```

## Supported API Providers

### 1. Truecaller API

**Provider**: Truecaller  
**Pricing**: Paid (contact for pricing)  
**Rate Limit**: Varies by plan  

```python
API_ENDPOINTS = {
    "phone_lookup": "https://search5-noneu.truecaller.com/v2/search",
}
API_KEYS = {
    "primary": "truecaller_api_key"
}
```

**Response Format**:
```json
{
  "data": [{
    "name": "John Doe",
    "phones": [{"e164Format": "+6281234567890"}],
    "addresses": [{"city": "Jakarta"}]
  }]
}
```

### 2. Numverify API

**Provider**: APILayer (Numverify)  
**Pricing**: Free tier available  
**Rate Limit**: 250 requests/month (free)  

```python
API_ENDPOINTS = {
    "phone_lookup": "http://apilayer.net/api/validate",
}
API_KEYS = {
    "primary": "numverify_access_key"
}
```

**Response Format**:
```json
{
  "valid": true,
  "number": "81234567890",
  "country_code": "ID",
  "country_name": "Indonesia",
  "location": "Jakarta",
  "carrier": "Telkomsel",
  "line_type": "mobile"
}
```

### 3. Custom Self-Hosted API

Build your own API using Flask, FastAPI, or Django.

**Example using Flask**:

```python
# api_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/v1/phone/lookup', methods=['GET'])
def phone_lookup():
    phone = request.args.get('phone')
    auth = request.headers.get('Authorization')
    
    # Validate API key
    if auth != 'Bearer your_secret_key':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Query your database
    result = query_database(phone)
    
    return jsonify({
        'name': result.name,
        'phone': phone,
        'city': result.city,
        'province': result.province,
        'operator': result.operator
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Client Configuration**:
```python
API_ENDPOINTS = {
    "phone_lookup": "http://localhost:5000/v1/phone/lookup",
}
API_KEYS = {
    "primary": "your_secret_key"
}
```

## API Request Flow

### Standard Request Flow

1. **Check Cache** - Cek apakah data sudah ada di cache
2. **Rate Limit Check** - Pastikan tidak exceed rate limit
3. **Make Request** - Kirim HTTP request ke API
4. **Parse Response** - Normalize response format
5. **Update Cache** - Simpan hasil ke cache
6. **Return Data** - Return ke aplikasi

### Error Handling Flow

1. **Connection Error** → Retry (max 3x)
2. **Timeout** → Retry with exponential backoff
3. **401 Unauthorized** → Return error (check API key)
4. **429 Rate Limited** → Wait and retry
5. **All Failed** → Fallback to simulation (if enabled)

## Response Format Mapping

Aplikasi ini normalize berbagai format response API ke format standar.

### Standard Format (Output)

```python
{
    "Nama": str,
    "Jenis Kelamin": str,
    "Birthday": str,  # YYYY-MM-DD
    "Umur": str,  # "25 tahun"
    "Email": str,
    "Jalan": str,
    "Kota/Town": str,
    "Provinsi": str,
    "Kode Pos": str,
    "Negara": str,
    "Latitude": str,
    "Longitude": str,
    "Operator": str,
    "Tipe Kartu": str,
    "Social Media": dict,
    "Waktu Pencarian": str,
    "Source": str  # "API/Database" or "Simulation"
}
```

### API Format (Input)

Format yang diterima dari API (akan dinormalize otomatis):

```python
{
    "name": "John",  # → Nama
    "full_name": "John Doe",  # → Nama
    "gender": "Male",  # → Jenis Kelamin
    "birth_date": "1990-01-01",  # → Birthday
    "birthdate": "1990-01-01",  # → Birthday
    "age": 33,  # → Umur
    "email": "john@example.com",  # → Email
    "street": "Main St",  # → Jalan
    "address": "123 Main St",  # → Jalan
    "city": "Jakarta",  # → Kota/Town
    "province": "DKI Jakarta",  # → Provinsi
    "postal_code": "10110",  # → Kode Pos
    "zip_code": "10110",  # → Kode Pos
    "country": "Indonesia",  # → Negara
    "latitude": -6.2,  # → Latitude
    "lat": -6.2,  # → Latitude
    "longitude": 106.8,  # → Longitude
    "lon": 106.8,  # → Longitude
    "lng": 106.8,  # → Longitude
    "operator": "Telkomsel",  # → Operator
    "carrier": "Telkomsel",  # → Operator
}
```

## Rate Limiting

### Default Configuration

```python
RATE_LIMIT_ENABLED = True
MAX_REQUESTS_PER_MINUTE = 10
REQUEST_DELAY = 1  # seconds
```

### Custom Rate Limiter

```python
from utils.api_client import RateLimiter

# Custom rate limiter: 100 requests per hour
limiter = RateLimiter(max_requests=100, time_window=3600)

if limiter.can_make_request():
    # Make API call
    limiter.add_request()
else:
    print("Rate limit exceeded")
```

## Caching

### Enable Caching

```python
CACHE_RESULTS = True
CACHE_DURATION = 3600  # 1 hour
```

### Manual Cache Management

```python
from utils.api_client import result_cache

# Get cached data
cached_data = result_cache.get("phone_081234567890")

# Set cache
result_cache.set("phone_081234567890", data)

# Clear all cache
result_cache.clear()
```

## Database Integration

### Initialize Database

```python
python utils/database_manager.py
# Choose option 1: Initialize Database
```

### Import Data

```python
# From JSON
python utils/database_manager.py
# Choose option 2: Import from JSON
# Enter file path: data/sample_database.json

# From CSV
# Prepare CSV with columns: phone_number, name, address, city, province, operator
python utils/database_manager.py
# Choose option 3: Import from CSV
```

### Query Priority

1. **Cache** (fastest)
2. **Local Database** (fast)
3. **External API** (slower, costs money)
4. **Simulation** (fallback)

## Security Best Practices

### 1. Protect API Keys

```bash
# Never commit api_config.py with real keys
echo "config/api_config.py" >> .gitignore

# Use environment variables (optional)
export API_KEY="your_secret_key"
```

```python
import os
API_KEYS = {
    "primary": os.getenv("API_KEY", "")
}
```

### 2. Use HTTPS

Always use HTTPS endpoints for production:
```python
# ✓ Good
"https://api.example.com/lookup"

# ✗ Bad (except localhost)
"http://api.example.com/lookup"
```

### 3. Validate Input

API client already validates input, but add extra validation if needed:

```python
import re

def validate_phone(phone):
    pattern = r'^08\d{8,11}$'
    return re.match(pattern, phone) is not None
```

### 4. Log Searches (for audit)

```python
LOG_SEARCHES = True  # in api_config.py
```

## Testing

### Test API Connection

```python
# test_api.py
from utils.api_client import APIClient

def test_connection():
    client = APIClient()
    
    # Test phone lookup
    result = client.lookup_phone("081234567890")
    assert result is not None
    assert 'name' in result or 'Nama' in result
    
    print("✓ API connection test passed")

if __name__ == "__main__":
    test_connection()
```

### Test with Mock Data

```python
# For development without real API
API_ENABLED = False
USE_FALLBACK_DATA = True
```

## Troubleshooting

### Common Issues

#### 1. "API authentication failed"
**Solution**: Check your API key in `config/api_config.py`

#### 2. "Connection timeout"
**Solution**: 
- Check internet connection
- Increase `API_TIMEOUT` in config
- Verify API endpoint is correct

#### 3. "Rate limit exceeded"
**Solution**:
- Wait for rate limit to reset
- Reduce `MAX_REQUESTS_PER_MINUTE`
- Enable caching to reduce API calls

#### 4. "No results from API"
**Solution**:
- Check if phone number exists in API database
- Verify response format matches expected format
- Enable `USE_FALLBACK_DATA` for demo data

### Debug Mode

Enable debug output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### 1. Enable Caching
Reduce API calls by 70-90%:
```python
CACHE_RESULTS = True
CACHE_DURATION = 3600
```

### 2. Use Database for Frequent Queries
Store frequently accessed data locally:
```python
DATABASE_ENABLED = True
```

### 3. Batch Processing
Use batch search for multiple numbers:
```bash
# Create batch_search.txt with phone numbers
python main.py
# Choose option 2: Pencarian Batch
```

### 4. Quick Mode
Skip animations for faster results:
```bash
# In app, choose option 13 to toggle Quick Mode
```

## API Cost Estimation

### Example Costs

| Provider | Free Tier | Paid Plans | Cost per 1000 requests |
|----------|-----------|------------|------------------------|
| Numverify | 250/month | From $9.99/month | ~$0.04 |
| Truecaller | No free tier | Custom pricing | Contact vendor |
| Custom API | Unlimited | Server costs | Variable |

### Cost Optimization Tips

1. **Enable caching** to reduce repeat queries
2. **Use local database** for known contacts
3. **Batch processing** is more efficient than single queries
4. **Rate limiting** prevents accidental overuse

## Compliance & Legal

### Data Protection

- Implement data retention policies
- Anonymize logs if required
- Secure API keys and database
- Comply with local privacy laws

### Indonesia Specific

- UU No. 27 Tahun 2022 (Perlindungan Data Pribadi)
- Peraturan Menkominfo terkait data pribadi
- Izin dari pemilik data (consent)

## Support & Resources

### Documentation
- [Main README](README.md)
- [Real Tracking Guide](REAL_TRACKING_GUIDE.md)
- [Feature Documentation](NEW_FEATURES.md)

### Code Examples
- `config/api_config.example.py` - Configuration example
- `data/sample_database.json` - Sample data format
- `utils/api_client.py` - API client implementation

### Community
- GitHub Issues: [Report bugs or request features]
- Email: support@example.com

---

**Last Updated**: 2024  
**Version**: 3.0  
**Author**: Letda Kes dr. Sobri
