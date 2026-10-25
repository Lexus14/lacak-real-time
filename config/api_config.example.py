# API Configuration Example for Real Tracking
# Copy this file to api_config.py and fill in your API credentials

# ============================================================================
# MODE SELECTION
# ============================================================================

# Set to True untuk mengaktifkan Real Tracking dengan API
# Set to False untuk mode simulasi (default)
API_ENABLED = False  # Ubah ke True untuk real tracking

# ============================================================================
# API CREDENTIALS
# ============================================================================

# Masukkan API key Anda di sini
# Contoh providers:
# - Truecaller API
# - Numverify API
# - Custom API Anda sendiri
API_KEYS = {
    "primary": "",  # Masukkan API key utama Anda
    "secondary": ""  # API key backup (optional)
}

# ============================================================================
# API ENDPOINTS
# ============================================================================

# Ganti dengan endpoint API Anda
# Format: "https://api.example.com/path"
API_ENDPOINTS = {
    "phone_lookup": "https://api.example.com/v1/phone/lookup",
    "nik_lookup": "https://api.example.com/v1/nik/lookup",
    "operator_check": "https://api.example.com/v1/operator/check",
    "location_lookup": "https://api.example.com/v1/location/lookup"
}

# ============================================================================
# CONNECTION SETTINGS
# ============================================================================

API_TIMEOUT = 10  # seconds - timeout untuk request
MAX_API_RETRIES = 3  # jumlah retry jika request gagal

# ============================================================================
# DATABASE SETTINGS (Local Data)
# ============================================================================

# Set ke True jika ingin menggunakan database lokal
DATABASE_ENABLED = False
DATABASE_PATH = "data/local_database.db"

# ============================================================================
# FEATURE TOGGLES
# ============================================================================

# Aktifkan/nonaktifkan fitur tertentu
ENABLE_OPERATOR_CHECK = True  # Cek operator via API
ENABLE_LOCATION_SERVICES = True  # Lookup lokasi via API
ENABLE_SOCIAL_MEDIA_SCAN = False  # Scan social media (requires special API)

# ============================================================================
# RATE LIMITING
# ============================================================================

# Untuk melindungi API dari overload
RATE_LIMIT_ENABLED = True
MAX_REQUESTS_PER_MINUTE = 10  # maksimal 10 request per menit
REQUEST_DELAY = 1  # jeda antar request (seconds)

# ============================================================================
# CACHING
# ============================================================================

# Cache hasil untuk mengurangi API calls
CACHE_RESULTS = True
CACHE_DURATION = 3600  # cache selama 1 jam (3600 seconds)

# ============================================================================
# PRIVACY & COMPLIANCE
# ============================================================================

# Tampilkan disclaimer sebelum pencarian
REQUIRE_CONSENT = True  # user harus menyetujui disclaimer

# Logging untuk audit
LOG_SEARCHES = True  # log semua pencarian
ANONYMIZE_LOGS = False  # anonymize data dalam logs

# ============================================================================
# CUSTOM API EXAMPLES
# ============================================================================

# Contoh 1: Truecaller-like API
"""
API_ENDPOINTS = {
    "phone_lookup": "https://api.truecaller.com/v1/search",
    "operator_check": "https://api.truecaller.com/v1/carrier"
}
API_KEYS = {
    "primary": "your_truecaller_api_key"
}
"""

# Contoh 2: Numverify API
"""
API_ENDPOINTS = {
    "phone_lookup": "http://apilayer.net/api/validate",
    "operator_check": "http://apilayer.net/api/validate"
}
API_KEYS = {
    "primary": "your_numverify_api_key"
}
"""

# Contoh 3: Custom Self-hosted API
"""
API_ENDPOINTS = {
    "phone_lookup": "http://localhost:5000/api/phone",
    "nik_lookup": "http://localhost:5000/api/nik"
}
API_KEYS = {
    "primary": "your_custom_api_key"
}
"""

# ============================================================================
# NOTES
# ============================================================================

"""
IMPORTANT:

1. Pastikan Anda memiliki izin legal untuk menggunakan API tracking
2. Simpan API key dengan aman, jangan commit ke public repository
3. Patuhi rate limits dari provider API Anda
4. Baca dokumentasi API provider untuk format response yang tepat
5. Test dengan satu nomor dulu sebelum batch processing

QUICK START:

1. Copy file ini ke api_config.py:
   cp config/api_config.example.py config/api_config.py

2. Edit api_config.py dan isi API_KEYS dan API_ENDPOINTS

3. Set API_ENABLED = True

4. Run aplikasi:
   python main.py

5. Test dengan single search dulu untuk verifikasi

TROUBLESHOOTING:

- Jika API tidak merespon, aplikasi akan fallback ke simulasi
- Cek logs untuk detail error
- Verifikasi API key dan endpoints valid
- Pastikan koneksi internet stabil
"""
