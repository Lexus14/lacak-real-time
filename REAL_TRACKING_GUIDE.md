# Panduan Real Tracking - Pegasus Lacak Nomor v3.0

## 🔍 Overview

Aplikasi ini sekarang mendukung **real tracking** dengan kemampuan untuk terhubung ke API eksternal dan database lokal. Mode tracking dapat dikonfigurasi antara simulasi dan pelacakan real.

## ⚙️ Konfigurasi

### 1. Mengaktifkan Real Tracking

Edit file `config/api_config.py`:

```python
# Aktifkan API
API_ENABLED = True

# Masukkan API Key Anda
API_KEYS = {
    "primary": "YOUR_API_KEY_HERE",  # Ganti dengan API key Anda
    "secondary": ""  # Backup API key (optional)
}

# Konfigurasi API Endpoints
API_ENDPOINTS = {
    "phone_lookup": "https://your-api.com/v1/phone/lookup",
    "nik_lookup": "https://your-api.com/v1/nik/lookup",
    "operator_check": "https://your-api.com/v1/operator/check",
    "location_lookup": "https://your-api.com/v1/location/lookup"
}
```

### 2. Mode Simulasi (Default)

Jika Anda tidak memiliki akses API, aplikasi akan tetap bekerja dalam mode simulasi:

```python
API_ENABLED = False  # Gunakan mode simulasi
USE_FALLBACK_DATA = True  # Fallback ke data simulasi jika API gagal
```

### 3. Database Lokal

Untuk menggunakan database lokal (jika Anda memiliki data sendiri):

```python
DATABASE_ENABLED = True
DATABASE_PATH = "data/local_database.db"
```

Database SQLite akan dibuat otomatis dengan struktur:
- Tabel `phone_records` untuk data nomor telepon
- Tabel `nik_records` untuk data NIK

## 🌐 API Integration

### Format Response API

Aplikasi mendukung berbagai format response dari API. Berikut contoh format yang didukung:

#### Response untuk Phone Lookup:
```json
{
  "name": "John Doe",
  "phone": "081234567890",
  "operator": "Telkomsel",
  "address": "Jl. Sudirman No. 123",
  "city": "Jakarta",
  "province": "DKI Jakarta",
  "postal_code": "10110",
  "latitude": -6.200000,
  "longitude": 106.816666,
  "email": "john.doe@example.com"
}
```

#### Response untuk NIK Lookup:
```json
{
  "nik": "3174010101900001",
  "name": "Jane Smith",
  "birth_date": "1990-01-01",
  "gender": "Perempuan",
  "address": "Jl. Thamrin No. 45",
  "city": "Jakarta",
  "province": "DKI Jakarta"
}
```

### Contoh API Providers

Beberapa API yang bisa digunakan (perlu registrasi dan API key):

1. **Truecaller API** - Untuk lookup nomor telepon
2. **Numverify API** - Validasi dan info nomor telepon
3. **Custom API** - Buat API sendiri dengan data Anda

## 🔐 Keamanan & Privacy

### Disclaimer Otomatis

Saat real tracking diaktifkan, aplikasi akan menampilkan disclaimer:

```
[!] PENTING - HARAP DIBACA:

1. Aplikasi ini menggunakan API eksternal untuk pelacakan real-time
2. Pastikan Anda memiliki izin hukum untuk melacak nomor target
3. Penyalahgunaan aplikasi ini dapat melanggar hukum privasi data
4. Semua pencarian akan dicatat untuk keperluan audit
5. Pengguna bertanggung jawab penuh atas penggunaan aplikasi ini
```

Untuk menonaktifkan disclaimer:
```python
REQUIRE_CONSENT = False  # di config/api_config.py
```

### Rate Limiting

Aplikasi memiliki built-in rate limiting untuk melindungi API:

```python
RATE_LIMIT_ENABLED = True
MAX_REQUESTS_PER_MINUTE = 10
REQUEST_DELAY = 1  # detik antar request
```

### Caching

Untuk mengurangi jumlah API calls:

```python
CACHE_RESULTS = True
CACHE_DURATION = 3600  # seconds (1 jam)
```

## 📊 Fitur Real Tracking

### 1. Single Search
- Koneksi ke API/database secara real-time
- Fallback otomatis ke simulasi jika tidak ada data
- Indikator sumber data (API/Database/Simulation)

### 2. Batch Search
- Batch lookup dari file
- Optimasi dengan caching
- Rate limiting otomatis
- Export hasil batch

### 3. Operator Detection
- Deteksi operator real-time (jika API mendukung)
- Fallback ke deteksi lokal berdasarkan prefix
- Database prefix operator Indonesia lengkap

### 4. Database Integration
- Query data dari SQLite lokal
- Import data sendiri ke database
- Caching otomatis untuk performa

## 🛠️ Troubleshooting

### API Tidak Merespon

Jika API tidak merespon:
1. Cek koneksi internet
2. Verifikasi API key valid
3. Cek endpoint URL benar
4. Lihat logs untuk detail error

Aplikasi akan otomatis fallback ke mode simulasi.

### Rate Limit Exceeded

Jika terkena rate limit:
```
[!] Rate limit reached. Waiting...
```

Solusi:
- Tunggu beberapa saat
- Kurangi `MAX_REQUESTS_PER_MINUTE`
- Aktifkan caching untuk mengurangi API calls

### Database Error

Jika error database:
1. Pastikan folder `data/` ada
2. Cek permission write
3. Hapus `local_database.db` untuk reset

## 📝 Contoh Penggunaan

### Mode Real Tracking (dengan API)

```bash
python main.py

# 1. Masukkan password aktivasi
# 2. Setujui disclaimer (jika aktif)
# 3. Pilih menu: Pencarian Tunggal
# 4. Masukkan nomor: 081234567890
# 5. Aplikasi akan query API real-time
# 6. Hasil ditampilkan dengan sumber data
```

### Mode Simulasi

```bash
# Edit config/api_config.py
API_ENABLED = False

python main.py
# Aplikasi berjalan dalam mode simulasi
```

### Dengan Database Lokal

```bash
# Edit config/api_config.py
DATABASE_ENABLED = True

# Aplikasi akan cek database dulu, baru API
python main.py
```

## 🔄 Migration dari Simulasi ke Real

Untuk migrasi dari mode simulasi ke real tracking:

1. **Backup history Anda** (jika ada)
2. **Setup API credentials** di `config/api_config.py`
3. **Test dengan satu nomor** dulu (single search)
4. **Verifikasi response** sesuai format
5. **Aktifkan untuk production**

## 📚 API Development

Jika Anda ingin membuat API sendiri:

### Endpoint Requirements

#### GET /v1/phone/lookup
- **Parameter**: `phone` (string)
- **Response**: JSON dengan data nomor
- **Auth**: Bearer token di header

#### GET /v1/nik/lookup
- **Parameter**: `nik` (string)
- **Response**: JSON dengan data NIK
- **Auth**: Bearer token di header

### Contoh API Simple (Flask):

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/v1/phone/lookup', methods=['GET'])
def phone_lookup():
    phone = request.args.get('phone')
    auth = request.headers.get('Authorization')
    
    # Validasi auth token
    if not auth or auth != 'Bearer YOUR_SECRET_KEY':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Query database Anda
    data = query_phone_from_your_db(phone)
    
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(port=5000)
```

## ⚖️ Legal & Compliance

**PENTING**: 

1. **Pastikan Anda memiliki hak legal** untuk melakukan tracking nomor telepon atau NIK
2. **Patuhi UU Perlindungan Data Pribadi** Indonesia (UU No. 27 Tahun 2022)
3. **Hanya gunakan untuk tujuan legal** seperti:
   - Verifikasi identitas dengan consent
   - Investigasi dengan warrant
   - Research dengan approval etik
4. **Jangan menyalahgunakan** untuk:
   - Stalking atau harassment
   - Penipuan atau fraud
   - Pelanggaran privasi

**Pengguna bertanggung jawab penuh** atas penggunaan aplikasi ini.

## 📞 Support

Untuk pertanyaan atau bantuan:
- Email: support@pegasus-lacak-nomor.com
- GitHub Issues: [Link to repo]

---

**Created by: Letda Kes dr. Sobri**  
**Version: 3.0 - Real Tracking Edition**
