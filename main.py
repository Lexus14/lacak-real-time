import sys
import time
import random
from tqdm import tqdm
from colorama import init, Fore, Style

from config.settings import (
    ACTIVATION_PASSWORD, MAX_PASSWORD_ATTEMPTS,
    PROGRESS_BAR_WIDTH, LOADING_ANIMATION_DURATION,
    LOADING_ANIMATION_ITERATIONS, VALID_PHONE_PREFIX,
    NIK_LENGTH, MAX_HISTORY_ITEMS, BATCH_INPUT_FILE,
    MAX_BATCH_SIZE, QUICK_SEARCH_MODE, MAX_FAVORITES,
    PHONE_OPERATORS
)
from config.api_config import (
    API_ENABLED, REQUIRE_CONSENT,
    DATABASE_ENABLED, ENABLE_OPERATOR_CHECK
)
from utils.helpers import (
    clear_screen, print_colored, validate_input,
    format_timestamp, handle_exception, handle_keyboard_interrupt,
    export_to_json, export_to_csv, export_to_txt,
    read_batch_file, calculate_statistics, detect_operator,
    calculate_age, calculate_distance, generate_email,
    generate_social_media, draw_ascii_chart, filter_history_by_date,
    filter_history_by_location, filter_history_by_gender, export_to_report
)
from utils.api_client import perform_real_lookup, APIClient
from utils.history_manager import HistoryManager
from utils.logger import audit_logger
from utils.health_check import health_checker
from utils.input_validator import validator
from utils.backup_manager import backup_manager

# Import new advanced features
try:
    from managers.user_manager import UserManager
    from models.user import Permission
    USER_SYSTEM_AVAILABLE = True
except ImportError as e:
    USER_SYSTEM_AVAILABLE = False

try:
    from analytics.dashboard import AnalyticsDashboard
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

try:
    from ml.anomaly_detector import AnomalyDetector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from geo.geospatial_analyzer import GeospatialAnalyzer
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False

try:
    from reporting.advanced_exporter import AdvancedExporter, generate_professional_report
    REPORTING_AVAILABLE = True
except ImportError:
    REPORTING_AVAILABLE = False

try:
    from automation.scheduler import TaskScheduler, get_scheduler, start_scheduler, stop_scheduler
    from automation.scheduler import SCHEDULE_AVAILABLE
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    SCHEDULE_AVAILABLE = False

# Initialize colorama
init()

# Initialize managers
history_manager = HistoryManager()
audit_logger = audit_logger
health_checker = health_checker
validator = validator
backup_manager = backup_manager

# Initialize new managers
user_manager = UserManager() if USER_SYSTEM_AVAILABLE else None
dashboard = AnalyticsDashboard() if ANALYTICS_AVAILABLE else None
anomaly_detector = AnomalyDetector() if ML_AVAILABLE else None
geo_analyzer = GeospatialAnalyzer() if GEO_AVAILABLE else None

# Global variables
quick_mode = QUICK_SEARCH_MODE

def print_banner():
    """Print the application banner."""
    banner = f"""
    {Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗
    ║                         Z H A N G                          ║
    ║                     By : Muhammad Jeksen                       ║
    ║                          REAL TRACKING SYSTEM                             ║
    ║                     {Fore.GREEN}[API & DATABASE ENABLED]{Fore.CYAN}                      ║
    ╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)
    
    if REQUIRE_CONSENT:
        print_consent_disclaimer()

def print_consent_disclaimer():
    """Print privacy and consent disclaimer."""
    disclaimer = f"""
    {Fore.YELLOW}╔════════════════════════════════════════════════════════════════════════════╗
    ║                            DISCLAIMER & PRIVACY                           ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    [!] PENTING - HARAP DIBACA:
    
    1. Aplikasi ini menggunakan API eksternal untuk pelacakan real-time
    2. Pastikan Anda memiliki izin hukum untuk melacak nomor target
    3. Penyalahgunaan aplikasi ini dapat melanggar hukum privasi data
    4. Semua pencarian akan dicatat untuk keperluan audit
    5. Pengguna bertanggung jawab penuh atas penggunaan aplikasi ini
    
    Dengan melanjutkan, Anda menyetujui syarat dan ketentuan di atas.{Style.RESET_ALL}
    """
    print(disclaimer)
    
    consent = input(f"\n{Fore.YELLOW}Lanjutkan? (yes/no): {Style.RESET_ALL}")
    if consent.lower() not in ['yes', 'y']:
        print_colored("\n[!] Anda tidak menyetujui disclaimer. Program dihentikan.", "ERROR")
        sys.exit(0)
    print()

def check_password():
    """Check activation password."""
    attempts = 0
    
    while attempts < MAX_PASSWORD_ATTEMPTS:
        password = input(f"\n{Fore.YELLOW}[!] Masukkan Password Aktivasi: {Style.RESET_ALL}")
        if password == ACTIVATION_PASSWORD:
            print_colored("[✓] Password benar!", "SUCCESS")
            time.sleep(1)
            return True
        attempts += 1
        if attempts < MAX_PASSWORD_ATTEMPTS:
            print_colored(f"\n[!] Password salah! Sisa percobaan: {MAX_PASSWORD_ATTEMPTS - attempts}", "ERROR")
        else:
            print_colored("\n[!] Maksimal percobaan terlampaui. Program berhenti.", "ERROR")
            sys.exit(1)
    return False

def loading_animation():
    """Show loading animation."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for _ in range(LOADING_ANIMATION_ITERATIONS):
        for char in chars:
            sys.stdout.write(f"\r{Fore.CYAN}[{char}] Loading...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(LOADING_ANIMATION_DURATION)
    print("\r" + " " * 50 + "\r", end="")

def real_search(target):
    """Perform real tracking lookup via API or database."""
    print_colored("\n[INFO] Initiating Real-time Tracking...", "INFO")
    loading_animation()
    
    # Perform actual lookup
    result = perform_real_lookup(target)
    
    # Show progress
    for _ in tqdm(range(100), desc="Tracking", 
                 bar_format="{l_bar}█{bar}█{r_bar}",
                 colour="green", ncols=PROGRESS_BAR_WIDTH):
        time.sleep(0.02)
    
    return result

def normalize_api_response(api_data, target):
    """Normalize API response to standard format."""
    normalized = {
        "Waktu Pencarian": format_timestamp()
    }
    
    # Map common API fields to our format
    field_mapping = {
        'name': 'Nama',
        'full_name': 'Nama',
        'gender': 'Jenis Kelamin',
        'birth_date': 'Birthday',
        'birthdate': 'Birthday',
        'age': 'Umur',
        'email': 'Email',
        'street': 'Jalan',
        'address': 'Jalan',
        'city': 'Kota/Town',
        'province': 'Provinsi',
        'postal_code': 'Kode Pos',
        'zip_code': 'Kode Pos',
        'country': 'Negara',
        'latitude': 'Latitude',
        'lat': 'Latitude',
        'longitude': 'Longitude',
        'lon': 'Longitude',
        'lng': 'Longitude',
        'operator': 'Operator',
        'carrier': 'Operator',
        'card_type': 'Tipe Kartu',
        'social_media': 'Social Media'
    }
    
    for api_key, display_key in field_mapping.items():
        if api_key in api_data:
            normalized[display_key] = api_data[api_key]
    
    # Ensure required fields exist
    if 'Nama' not in normalized:
        normalized['Nama'] = api_data.get('name', 'Unknown')
    
    if 'Negara' not in normalized:
        normalized['Negara'] = 'Indonesia'
    
    # Calculate age if we have birthday
    if 'Birthday' in normalized and 'Umur' not in normalized:
        age = calculate_age(normalized['Birthday'])
        if age:
            normalized['Umur'] = f"{age} tahun"
    
    # Detect operator for phone numbers
    if target.startswith('08') and 'Operator' not in normalized:
        api_client = APIClient()
        operator = api_client.check_operator(target)
        if operator:
            normalized['Operator'] = operator
    
    # Generate missing fields if needed
    if 'Email' not in normalized and 'Nama' in normalized:
        normalized['Email'] = generate_email(normalized['Nama'])
    
    if 'Social Media' not in normalized and 'Nama' in normalized:
        normalized['Social Media'] = generate_social_media(normalized['Nama'])
    
    return normalized

def display_result(data):
    """Display search results."""
    print_colored("\nResult:", "SUCCESS")
    for key, value in data.items():
        if key == "Waktu Pencarian":
            print_colored(f"{key}: {value}", "WARNING")
        elif key == "Social Media":
            print_colored(f"\n{key}:", "INFO")
            for platform, handle in value.items():
                print_colored(f"  - {platform}: {handle}", "INFO")
        else:
            print_colored(f"{key}: {value}", "INFO")
    print_colored("\n[✔] Search Data complete!", "SUCCESS")

def add_to_history(target, result, note=""):
    """Add search to history."""
    # Use the new history manager
    history_manager.add_search(target, result, note)

def show_history():
    """Display search history."""
    # Get history from the new history manager
    search_history = history_manager.get_all_history()
    
    if not search_history:
        print_colored("\n[!] History kosong. Belum ada pencarian yang dilakukan.", "WARNING")
        return
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("HISTORY PENCARIAN", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    for i, entry in enumerate(search_history, 1):
        print_colored(f"\n[{i}] Target: {entry['target']}", "INFO")
        print_colored(f"    Waktu: {entry['timestamp']}", "WARNING")
        print_colored(f"    Nama: {entry['result']['Nama']}", "INFO")
        print_colored(f"    Kota: {entry['result']['Kota/Town']}", "INFO")
        if entry['note']:
            print_colored(f"    Catatan: {entry['note']}", "WARNING")
        if entry['is_favorite']:
            print_colored(f"    ⭐ FAVORIT", "SUCCESS")
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored(f"Total: {len(search_history)} pencarian", "SUCCESS")

def show_statistics():
    """Display search statistics."""
    # Get history from the new history manager
    search_history = history_manager.get_all_history()
    
    if not search_history:
        print_colored("\n[!] Belum ada data untuk statistik.", "WARNING")
        return
    
    # Calculate statistics
    total_searches = len(search_history)
    targets = [h['target'] for h in search_history]
    phone_numbers = sum(1 for t in targets if t.startswith('08'))
    niks = total_searches - phone_numbers
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("STATISTIK PENCARIAN", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    print_colored(f"Total Pencarian: {total_searches}", "INFO")
    print_colored(f"Nomor Telepon: {phone_numbers}", "INFO")
    print_colored(f"NIK: {niks}", "INFO")
    if search_history:
        print_colored(f"Pencarian Pertama: {search_history[-1]['timestamp']}", "WARNING")
        print_colored(f"Pencarian Terakhir: {search_history[0]['timestamp']}", "WARNING")
    print_colored(f"{'='*70}", "INFO")

def export_result(data, target):
    """Export search result to file."""
    print_colored("\n[?] Pilih format export:", "INFO")
    print("1. JSON")
    print("2. CSV")
    print("3. TXT")
    print("4. Batal")
    
    choice = input(f"\n{Fore.YELLOW}Pilih (1-4): {Style.RESET_ALL}")
    
    timestamp = format_timestamp().replace(' ', '_').replace(':', '-')
    filename_base = f"result_{target}_{timestamp}"
    
    try:
        if choice == '1':
            filepath = export_to_json(data, f"{filename_base}.json")
            print_colored(f"\n[✓] Data berhasil diexport ke: {filepath}", "SUCCESS")
        elif choice == '2':
            filepath = export_to_csv(data, f"{filename_base}.csv")
            print_colored(f"\n[✓] Data berhasil diexport ke: {filepath}", "SUCCESS")
        elif choice == '3':
            filepath = export_to_txt(data, f"{filename_base}.txt")
            print_colored(f"\n[✓] Data berhasil diexport ke: {filepath}", "SUCCESS")
        elif choice == '4':
            print_colored("\n[!] Export dibatalkan.", "WARNING")
        else:
            print_colored("\n[!] Pilihan tidak valid.", "ERROR")
    except Exception as e:
        print_colored(f"\n[!] Error saat export: {str(e)}", "ERROR")

def batch_search():
    """Search multiple numbers from file with real tracking."""
    print_colored(f"\n[INFO] Membaca file batch: {BATCH_INPUT_FILE}", "INFO")
    numbers = read_batch_file(BATCH_INPUT_FILE)
    
    if not numbers:
        print_colored("\n[!] Tidak ada nomor untuk dicari. Buat file batch_search.txt dengan nomor per baris.", "WARNING")
        time.sleep(3)
        return
    
    if len(numbers) > MAX_BATCH_SIZE:
        print_colored(f"\n[!] Jumlah nomor melebihi batas maksimal ({MAX_BATCH_SIZE}). Hanya {MAX_BATCH_SIZE} yang akan diproses.", "WARNING")
        numbers = numbers[:MAX_BATCH_SIZE]
    
    print_colored(f"\n[INFO] Ditemukan {len(numbers)} nomor untuk dicari.", "INFO")
    print_colored(f"[INFO] Mode: Real Tracking via API/Database", "SUCCESS")
    
    time.sleep(1)
    
    results = []
    for i, target in enumerate(numbers, 1):
        print_colored(f"\n[{i}/{len(numbers)}] Mencari: {target}", "INFO")
        
        # Use new input validator
        is_valid, target_type, result_or_error = validator.validate_target(target)
        
        if not is_valid:
            print_colored(f"[!] Melewati nomor tidak valid: {target}", "ERROR")
            continue
        
        # Cleaned target
        target = result_or_error
        
        result = None
        
        # Perform real tracking
        api_result = perform_real_lookup(target)
        if api_result:
            result = normalize_api_response(api_result, target)
            result["Source"] = "API/Database"
            
            # Log successful search
            audit_logger.log_search(target, "API/Database", True)
        else:
            print_colored(f"[!] Data tidak ditemukan untuk: {target}", "WARNING")
            
            # Log failed search
            audit_logger.log_search(target, "API/Database", False)
        
        if result:
            result['Target'] = target
            results.append(result)
            add_to_history(target, result)
            
            # Show brief result for batch
            print_colored(f"    Nama: {result.get('Nama', 'N/A')}", "INFO")
            print_colored(f"    Kota: {result.get('Kota/Town', 'N/A')}", "INFO")
            time.sleep(0.3)
    
    print_colored(f"\n[✓] Batch search selesai! {len(results)}/{len(numbers)} berhasil.", "SUCCESS")
    
    if results:
        choice = input(f"\n{Fore.YELLOW}[?] Export semua hasil? (y/n): {Style.RESET_ALL}")
        if choice.lower() == 'y':
            timestamp = format_timestamp().replace(' ', '_').replace(':', '-')
            filepath = export_to_json(results, f"batch_results_{timestamp}.json")
            print_colored(f"\n[✓] Semua hasil diexport ke: {filepath}", "SUCCESS")

def search_by_name():
    """Search by name (reverse lookup) - Requires API/Database support."""
    print_colored("\n[!] Fitur pencarian berdasarkan nama memerlukan API/Database yang mendukung reverse lookup.", "WARNING")
    print_colored("[!] Fitur ini telah dinonaktifkan karena memerlukan data real dari API.", "WARNING")
    time.sleep(3)

def search_by_location():
    """Search by location (city/province) - Requires API/Database support."""
    print_colored("\n[!] Fitur pencarian berdasarkan lokasi memerlukan API/Database yang mendukung location lookup.", "WARNING")
    print_colored("[!] Fitur ini telah dinonaktifkan karena memerlukan data real dari API.", "WARNING")
    time.sleep(3)

def advanced_filter_history():
    """Filter history with advanced options."""
    # Get history from the new history manager
    search_history = history_manager.get_all_history()
    
    if not search_history:
        print_colored("\n[!] History kosong.", "WARNING")
        return
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("FILTER HISTORY", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    print("1. Filter berdasarkan tanggal")
    print("2. Filter berdasarkan lokasi")
    print("3. Filter berdasarkan gender")
    print("4. Kembali")
    
    choice = input(f"\n{Fore.YELLOW}Pilih filter (1-4): {Style.RESET_ALL}")
    
    filtered = []
    if choice == '1':
        date = input(f"\n{Fore.YELLOW}Masukkan tanggal (YYYY-MM-DD): {Style.RESET_ALL}")
        filtered = filter_history_by_date(search_history, date)
    elif choice == '2':
        location = input(f"\n{Fore.YELLOW}Masukkan lokasi: {Style.RESET_ALL}")
        filtered = filter_history_by_location(search_history, location)
    elif choice == '3':
        gender = input(f"\n{Fore.YELLOW}Masukkan gender (Laki-laki/Perempuan): {Style.RESET_ALL}")
        filtered = filter_history_by_gender(search_history, gender)
    elif choice == '4':
        return
    else:
        print_colored("\n[!] Pilihan tidak valid!", "ERROR")
        return
    
    if not filtered:
        print_colored("\n[!] Tidak ada hasil yang sesuai filter.", "WARNING")
        return
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored(f"HASIL FILTER ({len(filtered)} item)", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    for i, entry in enumerate(filtered, 1):
        print_colored(f"\n[{i}] Target: {entry['target']}", "INFO")
        print_colored(f"    Waktu: {entry['timestamp']}", "WARNING")
        print_colored(f"    Nama: {entry['result']['Nama']}", "INFO")
        print_colored(f"    Lokasi: {entry['result']['Kota/Town']}, {entry['result']['Provinsi']}", "INFO")

def show_visual_statistics():
    """Display statistics with ASCII charts."""
    # Get history from the new history manager
    search_history = history_manager.get_all_history()
    
    if not search_history:
        print_colored("\n[!] Belum ada data untuk statistik.", "WARNING")
        return
    
    # Calculate statistics
    total_searches = len(search_history)
    targets = [h['target'] for h in search_history]
    phone_numbers = sum(1 for t in targets if t.startswith('08'))
    niks = total_searches - phone_numbers
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("STATISTIK VISUAL", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    search_types = {
        "Nomor Telepon": phone_numbers,
        "NIK": niks
    }
    draw_ascii_chart(search_types, "Tipe Pencarian")
    
    gender_count = {}
    for h in search_history:
        gender = h['result'].get('Jenis Kelamin', 'Unknown')
        gender_count[gender] = gender_count.get(gender, 0) + 1
    
    if gender_count:
        draw_ascii_chart(gender_count, "Distribusi Gender")
    
    city_count = {}
    for h in search_history:
        city = h['result'].get('Kota/Town', 'Unknown')
        city_count[city] = city_count.get(city, 0) + 1
    
    top_cities = dict(sorted(city_count.items(), key=lambda x: x[1], reverse=True)[:5])
    if top_cities:
        draw_ascii_chart(top_cities, "Top 5 Kota")

def calculate_distance_feature():
    """Calculate distance between two coordinates."""
    print_colored("\n[?] KALKULATOR JARAK", "SUCCESS")
    
    try:
        lat1 = float(input(f"\n{Fore.YELLOW}Latitude 1: {Style.RESET_ALL}"))
        lon1 = float(input(f"{Fore.YELLOW}Longitude 1: {Style.RESET_ALL}"))
        lat2 = float(input(f"{Fore.YELLOW}Latitude 2: {Style.RESET_ALL}"))
        lon2 = float(input(f"{Fore.YELLOW}Longitude 2: {Style.RESET_ALL}"))
        
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        print_colored(f"\n[✓] Jarak: {distance} km", "SUCCESS")
    except ValueError:
        print_colored("\n[!] Input tidak valid! Masukkan angka.", "ERROR")

def manage_favorites():
    """Manage favorite/bookmarked searches."""
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("FAVORIT", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    print("1. Tambah dari history")
    print("2. Lihat favorit")
    print("3. Hapus favorit")
    print("4. Kembali")
    
    choice = input(f"\n{Fore.YELLOW}Pilih (1-4): {Style.RESET_ALL}")
    
    if choice == '1':
        # Get history from the new history manager
        search_history = history_manager.get_all_history()
        
        if not search_history:
            print_colored("\n[!] History kosong.", "WARNING")
            return
        
        # Check if we have space (MAX_FAVORITES is still used for UI consistency)
        current_favorites = history_manager.get_favorites_count()
        if current_favorites >= MAX_FAVORITES:
            print_colored(f"\n[!] Favorit penuh (max {MAX_FAVORITES}).", "WARNING")
            return
        
        print_colored("\n[?] Pilih nomor dari history:", "INFO")
        for i, h in enumerate(search_history[-10:], 1):
            print(f"{i}. {h['target']} - {h['result']['Nama']}")
        
        idx = input(f"\n{Fore.YELLOW}Pilih nomor (1-{min(10, len(search_history))}): {Style.RESET_ALL}")
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(search_history[-10:]):
                selected_entry = search_history[-(10-idx)]
                # Add to favorites using history manager
                history_manager.add_favorite(
                    selected_entry['target'], 
                    selected_entry['result'], 
                    selected_entry.get('note', '')
                )
                print_colored("\n[✓] Ditambahkan ke favorit!", "SUCCESS")
            else:
                print_colored("\n[!] Nomor tidak valid!", "ERROR")
        except ValueError:
            print_colored("\n[!] Input tidak valid!", "ERROR")
    
    elif choice == '2':
        # Get favorites from the new history manager
        favorites = history_manager.get_all_favorites()
        
        if not favorites:
            print_colored("\n[!] Favorit kosong.", "WARNING")
            return
        
        print_colored(f"\n{'='*70}", "INFO")
        print_colored(f"DAFTAR FAVORIT ({len(favorites)})", "SUCCESS")
        print_colored(f"{'='*70}", "INFO")
        
        for i, fav in enumerate(favorites, 1):
            print_colored(f"\n[{i}] {fav['target']}", "INFO")
            print_colored(f"    Nama: {fav['result']['Nama']}", "INFO")
            print_colored(f"    Kota: {fav['result']['Kota/Town']}", "INFO")
            if fav['note']:
                print_colored(f"    Catatan: {fav['note']}", "WARNING")
    
    elif choice == '3':
        # Get favorites from the new history manager
        favorites = history_manager.get_all_favorites()
        
        if not favorites:
            print_colored("\n[!] Favorit kosong.", "WARNING")
            return
        
        for i, fav in enumerate(favorites, 1):
            print(f"{i}. {fav['target']} - {fav['result']['Nama']}")
        
        idx = input(f"\n{Fore.YELLOW}Pilih nomor untuk dihapus: {Style.RESET_ALL}")
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(favorites):
                selected_fav = favorites[idx]
                # Remove from favorites using history manager
                history_manager.remove_favorite(selected_fav['target'])
                print_colored("\n[✓] Dihapus dari favorit!", "SUCCESS")
            else:
                print_colored("\n[!] Nomor tidak valid!", "ERROR")
        except ValueError:
            print_colored("\n[!] Input tidak valid!", "ERROR")

def clear_history():
    """Clear search history."""
    # Get current history count
    history_count = history_manager.get_search_count()
    
    if history_count == 0:
        print_colored("\n[!] History sudah kosong.", "WARNING")
        return
    
    confirm = input(f"\n{Fore.YELLOW}[!] Hapus semua history? (y/n): {Style.RESET_ALL}")
    if confirm.lower() == 'y':
        history_manager.clear_history()
        print_colored("\n[✓] History berhasil dihapus!", "SUCCESS")
    else:
        print_colored("\n[!] Dibatalkan.", "WARNING")

def add_note_to_search():
    """Add note to a search in history."""
    # Get history from the new history manager
    search_history = history_manager.get_all_history()
    
    if not search_history:
        print_colored("\n[!] History kosong.", "WARNING")
        return
    
    print_colored("\n[?] Pilih pencarian untuk ditambahkan catatan:", "INFO")
    for i, h in enumerate(search_history[-10:], 1):
        note_text = f" - {h['note']}" if h.get('note') else ""
        print(f"{i}. {h['target']} - {h['result']['Nama']}{note_text}")
    
    idx = input(f"\n{Fore.YELLOW}Pilih nomor: {Style.RESET_ALL}")
    try:
        idx = int(idx) - 1
        if 0 <= idx < len(search_history[-10:]):
            selected_entry = search_history[-(10-idx)]
            note = input(f"{Fore.YELLOW}Masukkan catatan: {Style.RESET_ALL}")
            # Add note using history manager
            history_manager.add_note_to_search(selected_entry['target'], note)
            print_colored("\n[✓] Catatan ditambahkan!", "SUCCESS")
        else:
            print_colored("\n[!] Nomor tidak valid!", "ERROR")
    except ValueError:
        print_colored("\n[!] Input tidak valid!", "ERROR")

def toggle_quick_mode():
    """Toggle quick search mode."""
    global quick_mode
    quick_mode = not quick_mode
    status = "AKTIF" if quick_mode else "NONAKTIF"
    print_colored(f"\n[✓] Mode Cepat: {status}", "SUCCESS")
    time.sleep(1)

def generate_detailed_report():
    """Generate detailed report for last search."""
    if not search_history:
        print_colored("\n[!] Belum ada pencarian.", "WARNING")
        return
    
    last_search = search_history[-1]
    result = last_search['result'].copy()
    result['Target'] = last_search['target']
    result['Catatan'] = last_search.get('note', '-')
    
    timestamp = format_timestamp().replace(' ', '_').replace(':', '-')
    filepath = export_to_report(result, f"report_{timestamp}.txt")
    print_colored(f"\n[✓] Laporan lengkap dibuat: {filepath}", "SUCCESS")

def show_operator_info():
    """Show phone operator information."""
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("INFORMASI OPERATOR", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    operators = {}
    for prefix, op in PHONE_OPERATORS.items():
        if op not in operators:
            operators[op] = []
        operators[op].append(prefix)
    
    for op, prefixes in operators.items():
        print_colored(f"\n{op}:", "SUCCESS")
        print_colored(f"  Prefix: {', '.join(prefixes)}", "INFO")


def check_api_health():
    """Check API and database health."""
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("CEK KESEHATAN SISTEM", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    print_colored("\n[*] Memeriksa kesehatan API...", "INFO")
    api_healthy = health_checker.check_api_health()
    
    print_colored("\n[*] Memeriksa kesehatan database...", "INFO")
    db_healthy = health_checker.check_database_health()
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("HASIL CEK KESEHATAN", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    if api_healthy and db_healthy:
        print_colored("[✓] Semua sistem sehat dan siap digunakan!", "SUCCESS")
    else:
        print_colored("[!] Ada masalah dengan beberapa sistem.", "WARNING")
        if not api_healthy:
            print_colored("  - API: Tidak sehat", "ERROR")
        if not db_healthy:
            print_colored("  - Database: Tidak sehat", "ERROR")
    
    input(f"\n{Fore.YELLOW}[Enter untuk kembali ke menu]{Style.RESET_ALL}")


def backup_restore_menu():
    """Backup and restore menu."""
    while True:
        print_colored(f"\n{'='*70}", "INFO")
        print_colored("BACKUP & RESTORE", "SUCCESS")
        print_colored(f"{'='*70}", "INFO")
        print("1. Buat Backup")
        print("2. Restore Backup")
        print("3. Lihat Backup")
        print("4. Kembali")
        
        choice = input(f"\n{Fore.YELLOW}Pilih (1-4): {Style.RESET_ALL}")
        
        if choice == '1':
            print_colored("\n[*] Membuat backup...", "INFO")
            backup_manager.create_backup()
            print_colored("[✓] Backup selesai!", "SUCCESS")
        elif choice == '2':
            backups = backup_manager.list_backups()
            if backups:
                idx = input(f"\n{Fore.YELLOW}Pilih backup (1-{len(backups)}): {Style.RESET_ALL}")
                try:
                    idx = int(idx) - 1
                    if 0 <= idx < len(backups):
                        backup_file = f"{backup_manager.backup_dir}/{backups[idx]}"
                        backup_manager.restore_backup(backup_file)
                    else:
                        print_colored("[!] Nomor tidak valid!", "ERROR")
                except ValueError:
                    print_colored("[!] Input tidak valid!", "ERROR")
            else:
                print_colored("\n[!] Tidak ada backup tersedia.", "WARNING")
        elif choice == '3':
            backup_manager.list_backups()
        elif choice == '4':
            break
        else:
            print_colored("\n[!] Pilihan tidak valid!", "ERROR")
            time.sleep(1)


# ==================== ADVANCED FEATURES ====================

def login_screen():
    """User login screen for multi-user system."""
    if not USER_SYSTEM_AVAILABLE:
        print_colored("\n[!] Multi-user system not available.", "WARNING")
        time.sleep(2)
        return True
    
    print_colored("\n╔═══════════════════════════════════════╗", "INFO")
    print_colored("║         PEGASUS - USER LOGIN          ║", "SUCCESS")
    print_colored("╚═══════════════════════════════════════╝", "INFO")
    
    username = input(f"\n{Fore.YELLOW}Username: {Style.RESET_ALL}")
    
    # Use getpass for password if available
    try:
        import getpass
        password = getpass.getpass(f"{Fore.YELLOW}Password: {Style.RESET_ALL}")
    except:
        password = input(f"{Fore.YELLOW}Password: {Style.RESET_ALL}")
    
    if user_manager.authenticate(username, password):
        print_colored(f"\n[✓] Welcome, {username}!", "SUCCESS")
        print_colored(f"[i] Role: {user_manager.current_user.role.value}", "INFO")
        return True
    else:
        print_colored("\n[!] Invalid credentials", "ERROR")
        time.sleep(2)
        return False


def user_management_menu():
    """User management menu (admin only)."""
    if not USER_SYSTEM_AVAILABLE:
        print_colored("\n[!] Multi-user system not available.", "WARNING")
        time.sleep(2)
        return
    
    if not user_manager.current_user or not user_manager.current_user.has_permission(Permission.MANAGE_USERS):
        print_colored("\n[!] You don't have permission to manage users.", "ERROR")
        time.sleep(2)
        return
    
    while True:
        print_colored(f"\n{'='*70}", "INFO")
        print_colored("USER MANAGEMENT (Admin Only)", "SUCCESS")
        print_colored(f"{'='*70}", "INFO")
        print("1. List Users")
        print("2. Create User")
        print("3. Delete User")
        print("4. Change Password")
        print("5. Back")
        
        choice = input(f"\n{Fore.YELLOW}Pilih (1-5): {Style.RESET_ALL}")
        
        if choice == '1':
            try:
                users = user_manager.list_users()
                print_colored(f"\n{'='*70}", "INFO")
                print_colored("USERS LIST", "SUCCESS")
                print_colored(f"{'='*70}", "INFO")
                print(f"{'ID':<5} {'Username':<20} {'Role':<15} {'Active':<10}")
                print_colored("-" * 70, "INFO")
                for user in users:
                    print(f"{user['id']:<5} {user['username']:<20} {user['role']:<15} {'Yes' if user['is_active'] else 'No':<10}")
            except Exception as e:
                print_colored(f"\n[!] Error: {str(e)}", "ERROR")
        
        elif choice == '2':
            try:
                username = input(f"{Fore.YELLOW}New username: {Style.RESET_ALL}")
                password = input(f"{Fore.YELLOW}Password: {Style.RESET_ALL}")
                print("Roles: admin, operator, viewer, auditor")
                role = input(f"{Fore.YELLOW}Role: {Style.RESET_ALL}")
                
                user = user_manager.create_user(username, password, role)
                print_colored(f"\n[✓] User '{username}' created successfully!", "SUCCESS")
            except Exception as e:
                print_colored(f"\n[!] Error: {str(e)}", "ERROR")
        
        elif choice == '3':
            try:
                username = input(f"{Fore.YELLOW}Username to delete: {Style.RESET_ALL}")
                confirm = input(f"{Fore.YELLOW}Are you sure? (y/n): {Style.RESET_ALL}")
                if confirm.lower() == 'y':
                    user_manager.delete_user(username)
                    print_colored(f"\n[✓] User '{username}' deleted!", "SUCCESS")
            except Exception as e:
                print_colored(f"\n[!] Error: {str(e)}", "ERROR")
        
        elif choice == '4':
            try:
                username = input(f"{Fore.YELLOW}Username: {Style.RESET_ALL}")
                new_password = input(f"{Fore.YELLOW}New password: {Style.RESET_ALL}")
                user_manager.change_password(username, new_password)
                print_colored(f"\n[✓] Password changed!", "SUCCESS")
            except Exception as e:
                print_colored(f"\n[!] Error: {str(e)}", "ERROR")
        
        elif choice == '5':
            break
        
        input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")


def show_analytics_dashboard():
    """Display real-time analytics dashboard."""
    if not ANALYTICS_AVAILABLE:
        print_colored("\n[!] Analytics dashboard not available.", "WARNING")
        time.sleep(2)
        return
    
    while True:
        dashboard.display_dashboard()
        
        print(f"\n{Fore.YELLOW}[R] Refresh | [W] Weekly Report | [E] Export | [Q] Quit{Style.RESET_ALL}")
        choice = input("Command: ").lower()
        
        if choice == 'r':
            continue
        elif choice == 'w':
            dashboard.generate_weekly_report()
            input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")
        elif choice == 'e':
            try:
                import json
                stats = dashboard.get_realtime_stats()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"exports/analytics_{timestamp}.json"
                os.makedirs("exports", exist_ok=True)
                with open(filename, 'w') as f:
                    json.dump(stats, f, indent=2)
                print_colored(f"\n[✓] Analytics exported to: {filename}", "SUCCESS")
                time.sleep(2)
            except Exception as e:
                print_colored(f"\n[!] Export failed: {str(e)}", "ERROR")
                time.sleep(2)
        elif choice == 'q':
            break


def show_anomaly_detection():
    """Display anomaly detection report."""
    if not ML_AVAILABLE:
        print_colored("\n[!] Anomaly detection not available.", "WARNING")
        time.sleep(2)
        return
    
    print_colored("\n╔════════════════════════════════════════════╗", "INFO")
    print_colored("║      ANOMALY DETECTION REPORT              ║", "WARNING")
    print_colored("╚════════════════════════════════════════════╝", "INFO")
    
    # Train model if not trained
    if not anomaly_detector.is_trained:
        print_colored("\n[*] Training anomaly detection model...", "INFO")
        trained = anomaly_detector.train()
        if not trained:
            print_colored("[!] Not enough data to train model (need 50+ searches)", "WARNING")
            time.sleep(3)
            return
    
    # Generate report
    report = anomaly_detector.generate_report()
    
    if not report:
        print_colored("[!] Could not generate report", "ERROR")
        time.sleep(2)
        return
    
    print(f"\n{Fore.CYAN}RISK LEVEL: {report['risk_level']}{Style.RESET_ALL}")
    print(f"Anomalies Detected: {report['anomaly_count']}")
    print(f"High Confidence Anomalies: {report['high_confidence_anomalies']}")
    
    patterns = report['patterns']
    alerts = []
    
    if patterns.get('rapid_fire_searches'):
        alerts.append("⚠ Rapid-fire searches detected (potential abuse)")
    if patterns.get('unusual_times'):
        alerts.append("⚠ Unusual search times detected")
    if patterns.get('repeated_targets'):
        alerts.append("⚠ Repeated target searches (potential stalking)")
    if patterns.get('geographic_anomalies'):
        alerts.append("⚠ Geographic anomalies detected")
    if patterns.get('high_volume_user'):
        alerts.append("⚠ High volume usage detected")
    
    if alerts:
        print_colored("\n[!] ALERTS:", "ERROR")
        for alert in alerts:
            print_colored(f"  {alert}", "WARNING")
    else:
        print_colored("\n[✓] No anomalies detected", "SUCCESS")
    
    input(f"\n{Fore.YELLOW}[Enter untuk kembali]{Style.RESET_ALL}")


def show_geospatial_analysis():
    """Display geospatial analysis menu."""
    if not GEO_AVAILABLE:
        print_colored("\n[!] Geospatial analysis not available.", "WARNING")
        time.sleep(2)
        return
    
    search_history = history_manager.get_all_history(100)
    
    if not search_history:
        print_colored("\n[!] No search history available", "WARNING")
        time.sleep(2)
        return
    
    while True:
        print_colored(f"\n{'='*70}", "INFO")
        print_colored("GEOSPATIAL ANALYSIS", "SUCCESS")
        print_colored(f"{'='*70}", "INFO")
        print("1. Generate Heatmap")
        print("2. Generate Cluster Map")
        print("3. Detect Geographic Clusters")
        print("4. Calculate Search Radius")
        print("5. Location Statistics")
        print("6. Back")
        
        choice = input(f"\n{Fore.YELLOW}Pilih (1-6): {Style.RESET_ALL}")
        
        if choice == '1':
            geo_analyzer.create_heatmap_html()
            input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")
        elif choice == '2':
            geo_analyzer.create_cluster_map_html()
            input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")
        elif choice == '3':
            clusters = geo_analyzer.detect_geographic_clusters()
            print_colored(f"\n[i] Found {len(clusters)} geographic clusters", "INFO")
            for i, cluster in enumerate(clusters, 1):
                cities = set(loc['city'] for loc in cluster)
                print(f"  Cluster {i}: {len(cluster)} locations ({', '.join(cities)})")
            input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")
        elif choice == '4':
            radius = geo_analyzer.calculate_search_radius()
            print_colored(f"\n[i] Search radius: {radius:.2f} km", "INFO")
            input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")
        elif choice == '5':
            stats = geo_analyzer.get_location_statistics()
            print_colored(f"\n{'='*70}", "INFO")
            print_colored("LOCATION STATISTICS", "SUCCESS")
            print_colored(f"{'='*70}", "INFO")
            print(f"Total Locations: {stats.get('total_locations', 0)}")
            print(f"Unique Cities: {stats.get('unique_cities', 0)}")
            print(f"Unique Provinces: {stats.get('unique_provinces', 0)}")
            print(f"Search Radius: {stats.get('search_radius_km', 0):.2f} km")
            
            if stats.get('top_cities'):
                print(f"\n{Fore.CYAN}Top Cities:{Style.RESET_ALL}")
                for city, count in list(stats['top_cities'].items())[:5]:
                    print(f"  {city}: {count}")
            
            input(f"\n{Fore.YELLOW}[Enter untuk melanjutkan]{Style.RESET_ALL}")
        elif choice == '6':
            break


def advanced_reporting_menu():
    """Advanced reporting menu."""
    if not REPORTING_AVAILABLE:
        print_colored("\n[!] Advanced reporting not available.", "WARNING")
        time.sleep(2)
        return
    
    search_history = history_manager.get_all_history(100)
    
    if not search_history:
        print_colored("\n[!] No search history available", "WARNING")
        time.sleep(2)
        return
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("ADVANCED REPORTING", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    print("1. PDF Report")
    print("2. Excel Report (Advanced)")
    print("3. HTML Report")
    print("4. All Formats")
    print("5. Back")
    
    choice = input(f"\n{Fore.YELLOW}Choose format (1-5): {Style.RESET_ALL}")
    
    if choice == '1':
        generate_professional_report(search_history, 'pdf')
    elif choice == '2':
        generate_professional_report(search_history, 'excel')
    elif choice == '3':
        generate_professional_report(search_history, 'html')
    elif choice == '4':
        files = generate_professional_report(search_history, 'all')
        print_colored(f"\n[✓] Generated {len(files)} reports", "SUCCESS")
    elif choice == '5':
        return
    
    if choice in ['1', '2', '3', '4']:
        input(f"\n{Fore.YELLOW}[Enter untuk kembali]{Style.RESET_ALL}")


def automation_menu():
    """Automation and scheduler menu."""
    if not AUTOMATION_AVAILABLE:
        print_colored("\n[!] Automation not available.", "WARNING")
        if not SCHEDULE_AVAILABLE:
            print_colored("[i] Install schedule library: pip install schedule", "INFO")
        time.sleep(2)
        return
    
    scheduler = get_scheduler()
    
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("AUTOMATION & SCHEDULER", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    print(f"Status: {'Running' if scheduler.running else 'Stopped'}")
    print("\n1. Start Scheduler")
    print("2. Stop Scheduler")
    print("3. Run Backup Now")
    print("4. Run Report Now")
    print("5. Run Cleanup Now")
    print("6. Run Health Check Now")
    print("7. Back")
    
    choice = input(f"\n{Fore.YELLOW}Pilih (1-7): {Style.RESET_ALL}")
    
    if choice == '1':
        if not scheduler.running:
            start_scheduler()
        else:
            print_colored("[!] Scheduler is already running", "WARNING")
    elif choice == '2':
        if scheduler.running:
            stop_scheduler()
        else:
            print_colored("[!] Scheduler is not running", "WARNING")
    elif choice == '3':
        scheduler.run_task_now('backup')
    elif choice == '4':
        scheduler.run_task_now('report')
    elif choice == '5':
        scheduler.run_task_now('cleanup')
    elif choice == '6':
        scheduler.run_task_now('health')
    
    if choice in ['1', '2', '3', '4', '5', '6']:
        time.sleep(2)


def start_api_server_menu():
    """Start the API server."""
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("API SERVER", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    
    try:
        from api.server import start_api_server
        
        host = input(f"{Fore.YELLOW}Host (default 0.0.0.0): {Style.RESET_ALL}").strip() or "0.0.0.0"
        port = input(f"{Fore.YELLOW}Port (default 5000): {Style.RESET_ALL}").strip() or "5000"
        
        print_colored(f"\n[*] Starting API server on {host}:{port}...", "INFO")
        print_colored("[*] Press Ctrl+C to stop", "WARNING")
        
        try:
            start_api_server(host=host, port=int(port), debug=False)
        except KeyboardInterrupt:
            print_colored("\n[!] API server stopped", "WARNING")
    except ImportError as e:
        print_colored(f"\n[!] API server not available: {str(e)}", "ERROR")
        print_colored("[i] Install Flask: pip install flask flask-cors", "INFO")
        time.sleep(3)

def show_menu():
    """Display main menu."""
    print_colored(f"\n{'='*70}", "INFO")
    print_colored("MENU UTAMA", "SUCCESS")
    print_colored(f"{'='*70}", "INFO")
    print("1. Pencarian Tunggal")
    print("2. Pencarian Batch (dari file)")
    print("3. Pencarian Berdasarkan Nama")
    print("4. Pencarian Berdasarkan Lokasi")
    print("5. Lihat History")
    print("6. Filter History (Advanced)")
    print("7. Lihat Statistik")
    print("8. Statistik Visual (Chart)")
    print("9. Kalkulator Jarak")
    print("10. Kelola Favorit")
    print("11. Hapus History")
    print("12. Tambah Catatan")
    print("13. Mode Cepat (Toggle)")
    print("14. Generate Laporan Lengkap")
    print("15. Info Operator")
    print("16. Cek Kesehatan API")
    print("17. Backup & Restore")
    print_colored(f"{'='*70}", "INFO")
    print_colored("ADVANCED FEATURES", "WARNING")
    print_colored(f"{'='*70}", "INFO")
    print("18. User Management (Admin)")
    print("19. Analytics Dashboard")
    print("20. Anomaly Detection")
    print("21. Geospatial Analysis")
    print("22. Advanced Reporting")
    print("23. Automation & Scheduler")
    print("24. Start API Server")
    print("0. Keluar")
    print_colored(f"{'='*70}", "INFO")
    
    mode_status = "ON" if quick_mode else "OFF"
    print_colored(f"Mode Cepat: {mode_status}", "WARNING")

def single_search():
    """Perform single search with real tracking."""
    target = input(f"\n{Fore.YELLOW}[?] Masukkan Nomor Telepon (08xxx) atau NIK: {Style.RESET_ALL}")
    
    # Use new input validator
    is_valid, target_type, result_or_error = validator.validate_target(target)
    
    if not is_valid:
        print_colored(f"\n[!] {result_or_error}", "ERROR")
        time.sleep(2)
        return
    
    # Cleaned target
    target = result_or_error
    
    result = None
    
    # Perform real tracking
    if not quick_mode:
        api_result = real_search(target)
    else:
        print_colored("\n[INFO] Mode cepat aktif - query langsung", "WARNING")
        api_result = perform_real_lookup(target)
    
    if api_result:
        result = normalize_api_response(api_result, target)
        result["Source"] = "API/Database"
        print_colored("[✓] Data ditemukan dari sumber real!", "SUCCESS")
        
        # Log successful search
        audit_logger.log_search(target, "API/Database", True)
    else:
        print_colored("\n[!] Data tidak ditemukan. Pastikan API/Database dikonfigurasi dengan benar.", "ERROR")
        print_colored("[!] Atau nomor/NIK tidak ada dalam database.", "WARNING")
        
        # Log failed search
        audit_logger.log_search(target, "API/Database", False)
        time.sleep(3)
        return
    
    # Add to history using new history manager
    history_manager.add_search(target, result)
    display_result(result)
    
    choice = input(f"\n{Fore.YELLOW}[?] Export hasil? (y/n): {Style.RESET_ALL}")
    if choice.lower() == 'y':
        export_result(result, target)

def main():
    """Main program loop."""
    clear_screen()
    print_banner()
    
    # Check password first
    if not check_password():
        return
    
    # Login screen for multi-user system
    if USER_SYSTEM_AVAILABLE:
        if not login_screen():
            return
    
    while True:
        clear_screen()
        print_banner()
        
        # Show current user info if multi-user system
        if USER_SYSTEM_AVAILABLE and user_manager.current_user:
            print_colored(f"[i] Logged in as: {user_manager.current_user.username} ({user_manager.current_user.role.value})", "INFO")
        
        show_menu()
        
        choice = input(f"\n{Fore.YELLOW}[?] Pilih menu (0-24): {Style.RESET_ALL}")
        
        if choice == '1':
            single_search()
        elif choice == '2':
            batch_search()
        elif choice == '3':
            search_by_name()
        elif choice == '4':
            search_by_location()
        elif choice == '5':
            show_history()
        elif choice == '6':
            advanced_filter_history()
        elif choice == '7':
            show_statistics()
        elif choice == '8':
            show_visual_statistics()
        elif choice == '9':
            calculate_distance_feature()
        elif choice == '10':
            manage_favorites()
        elif choice == '11':
            clear_history()
        elif choice == '12':
            add_note_to_search()
        elif choice == '13':
            toggle_quick_mode()
        elif choice == '14':
            generate_detailed_report()
        elif choice == '15':
            show_operator_info()
        elif choice == '16':
            check_api_health()
        elif choice == '17':
            backup_restore_menu()
        elif choice == '18':
            user_management_menu()
        elif choice == '19':
            show_analytics_dashboard()
        elif choice == '20':
            show_anomaly_detection()
        elif choice == '21':
            show_geospatial_analysis()
        elif choice == '22':
            advanced_reporting_menu()
        elif choice == '23':
            automation_menu()
        elif choice == '24':
            start_api_server_menu()
        elif choice == '0':
            break
        else:
            print_colored("\n[!] Pilihan tidak valid!", "ERROR")
            time.sleep(1)
            continue
        
        # List of choices that need enter to continue
        enter_options = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 
                        '14', '15', '16', '18', '20', '22']
        if choice in enter_options:
            input(f"\n{Fore.YELLOW}[Enter untuk kembali ke menu]{Style.RESET_ALL}")
    
    # Stop scheduler on exit if running
    if AUTOMATION_AVAILABLE:
        stop_scheduler()
    
    print_colored("\n[!] Terima kasih telah menggunakan Pegasus Lacak Nomor!", "SUCCESS")
    time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_exception(e)
