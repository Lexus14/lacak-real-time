import os
import sys
import json
import csv
from datetime import datetime
from colorama import Fore, Style
from config.settings import COLORS, EXPORT_DIR

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(message, color_type="INFO"):
    """Print a colored message to the console."""
    color = getattr(Fore, COLORS.get(color_type, "WHITE").upper())
    print(f"{color}{message}{Style.RESET_ALL}")

def validate_input(target, valid_prefix, nik_length):
    """Validate phone number or NIK input."""
    if not target:
        print_colored("\n[!] Input tidak boleh kosong!", "ERROR")
        return False
        
    if not (target.startswith(valid_prefix) or len(target) == nik_length):
        print_colored("\n[!] Format nomor telepon atau NIK tidak valid!", "ERROR")
        return False
        
    return True

def format_timestamp():
    """Get current timestamp in formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def handle_exception(e):
    """Handle exceptions and print error message."""
    print_colored(f"\n[!] Terjadi kesalahan: {str(e)}", "ERROR")
    sys.exit(1)

def handle_keyboard_interrupt():
    """Handle keyboard interrupt (Ctrl+C)."""
    print_colored("\n\n[!] Program dihentikan oleh pengguna.", "WARNING")
    sys.exit(0)

def export_to_json(data, filename):
    """Export search result to JSON file."""
    ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filepath

def export_to_csv(data, filename):
    """Export search result to CSV file."""
    ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Field', 'Value'])
        for key, value in data.items():
            writer.writerow([key, value])
    return filepath

def export_to_txt(data, filename):
    """Export search result to TXT file."""
    ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("PEGASUS LACAK NOMOR - HASIL PENCARIAN\n")
        f.write("=" * 50 + "\n\n")
        for key, value in data.items():
            f.write(f"{key}: {value}\n")
        f.write("\n" + "=" * 50 + "\n")
    return filepath

def ensure_export_dir():
    """Ensure export directory exists."""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

def read_batch_file(filepath):
    """Read numbers from batch file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except FileNotFoundError:
        print_colored(f"\n[!] File {filepath} tidak ditemukan!", "ERROR")
        return []
    except Exception as e:
        print_colored(f"\n[!] Error membaca file: {str(e)}", "ERROR")
        return []

def calculate_statistics(history):
    """Calculate statistics from search history."""
    if not history:
        return {}
    
    total_searches = len(history)
    targets = [h['target'] for h in history]
    phone_numbers = sum(1 for t in targets if t.startswith('08'))
    niks = total_searches - phone_numbers
    
    return {
        'total_searches': total_searches,
        'phone_numbers': phone_numbers,
        'niks': niks,
        'first_search': history[0]['timestamp'] if history else None,
        'last_search': history[-1]['timestamp'] if history else None
    }

def detect_operator(phone_number):
    """Detect phone operator from phone number."""
    from config.settings import PHONE_OPERATORS
    if phone_number.startswith('08'):
        prefix = phone_number[:4]
        return PHONE_OPERATORS.get(prefix, "Unknown")
    return "N/A"

def calculate_age(birth_date_str):
    """Calculate age from birth date string."""
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    import math
    R = 6371
    
    lat1_rad = math.radians(float(lat1))
    lat2_rad = math.radians(float(lat2))
    delta_lat = math.radians(float(lat2) - float(lat1))
    delta_lon = math.radians(float(lon2) - float(lon1))
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return round(distance, 2)

def generate_email(name):
    """Generate email address from name."""
    import random
    from config.settings import EMAIL_DOMAINS
    clean_name = name.lower().replace(' ', '.')
    domain = random.choice(EMAIL_DOMAINS)
    return f"{clean_name}@{domain}"

def generate_social_media(name):
    """Generate social media handles."""
    import random
    from config.settings import SOCIAL_MEDIA_PLATFORMS
    clean_name = name.lower().replace(' ', '_')
    handles = {}
    for platform in SOCIAL_MEDIA_PLATFORMS:
        handles[platform] = f"@{clean_name}{random.randint(10, 999)}"
    return handles

def draw_ascii_chart(data, title="Chart"):
    """Draw simple ASCII bar chart."""
    if not data:
        return
    
    max_value = max(data.values()) if data else 0
    if max_value == 0:
        return
    
    print_colored(f"\n{title}", "SUCCESS")
    print_colored("=" * 50, "INFO")
    
    for label, value in data.items():
        bar_length = int((value / max_value) * 30)
        bar = "█" * bar_length
        print(f"{label:15} | {bar} {value}")
    
    print_colored("=" * 50, "INFO")

def filter_history_by_date(history, date_str):
    """Filter history by date."""
    filtered = [h for h in history if h['timestamp'].startswith(date_str)]
    return filtered

def filter_history_by_location(history, location):
    """Filter history by city or province."""
    filtered = [h for h in history if 
                location.lower() in h['result'].get('Kota/Town', '').lower() or
                location.lower() in h['result'].get('Provinsi', '').lower()]
    return filtered

def filter_history_by_gender(history, gender):
    """Filter history by gender."""
    filtered = [h for h in history if 
                h['result'].get('Jenis Kelamin', '').lower() == gender.lower()]
    return filtered

def export_to_report(data, filename):
    """Export detailed report to TXT file."""
    ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("╔" + "═" * 70 + "╗\n")
        f.write("║" + " " * 15 + "PEGASUS LACAK NOMOR - LAPORAN LENGKAP" + " " * 16 + "║\n")
        f.write("╚" + "═" * 70 + "╝\n\n")
        f.write(f"Generated: {format_timestamp()}\n\n")
        f.write("=" * 72 + "\n")
        f.write("INFORMASI DASAR\n")
        f.write("=" * 72 + "\n")
        for key, value in data.items():
            if not isinstance(value, dict):
                f.write(f"{key:25} : {value}\n")
        
        if 'Social Media' in data:
            f.write("\n" + "=" * 72 + "\n")
            f.write("SOCIAL MEDIA\n")
            f.write("=" * 72 + "\n")
            for platform, handle in data['Social Media'].items():
                f.write(f"{platform:25} : {handle}\n")
        
        f.write("\n" + "=" * 72 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 72 + "\n")
    return filepath
