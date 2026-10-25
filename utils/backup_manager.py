"""
Database Backup and Restore Manager
Handles backup and restore operations for database and history files
"""

import shutil
from datetime import datetime
import os
from colorama import Fore, Style

class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self):
        """Create backup of database and history"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backups_created = []
        
        # Backup local database
        if os.path.exists("data/local_database.db"):
            backup_path = f"{self.backup_dir}/database_backup_{timestamp}.db"
            shutil.copy2("data/local_database.db", backup_path)
            print_colored(f"[✓] Database backed up to: {backup_path}", "SUCCESS")
            backups_created.append(backup_path)
        
        # Backup history database
        if os.path.exists("data/app_data.db"):
            backup_path = f"{self.backup_dir}/history_backup_{timestamp}.db"
            shutil.copy2("data/app_data.db", backup_path)
            print_colored(f"[✓] History backed up to: {backup_path}", "SUCCESS")
            backups_created.append(backup_path)
        
        return backups_created
    
    def restore_backup(self, backup_file):
        """Restore from backup"""
        try:
            # Confirm from user
            confirm = input(f"{Fore.YELLOW}[!] Ini akan overwrite database saat ini. Lanjutkan? (y/n): {Style.RESET_ALL}")
            if confirm.lower() != 'y':
                return False
            
            if "database_backup" in backup_file:
                shutil.copy2(backup_file, "data/local_database.db")
                print_colored("[✓] Database restore berhasil!", "SUCCESS")
            elif "history_backup" in backup_file:
                shutil.copy2(backup_file, "data/app_data.db")
                print_colored("[✓] History restore berhasil!", "SUCCESS")
            
            return True
        except Exception as e:
            print_colored(f"[!] Restore gagal: {str(e)}", "ERROR")
            return False
    
    def list_backups(self):
        """List available backups"""
        backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.db')]
        backups.sort(reverse=True)
        
        print_colored("\n[📦] Backup Tersedia:", "INFO")
        for i, backup in enumerate(backups, 1):
            size = os.path.getsize(f"{self.backup_dir}/{backup}") / 1024
            print(f"{i}. {backup} ({size:.2f} KB)")
        
        return backups
    
    def auto_backup_schedule(self):
        """Auto backup every 7 days"""
        last_backup_file = f"{self.backup_dir}/.last_backup"
        
        if os.path.exists(last_backup_file):
            with open(last_backup_file, 'r') as f:
                last_backup = datetime.fromisoformat(f.read())
            
            if (datetime.now() - last_backup).days >= 7:
                self.create_backup()
                with open(last_backup_file, 'w') as f:
                    f.write(datetime.now().isoformat())
        else:
            # First time backup
            self.create_backup()
            with open(last_backup_file, 'w') as f:
                f.write(datetime.now().isoformat())

# Helper function for colored output
def print_colored(message, color_type="INFO"):
    """Helper function for colored output"""
    from colorama import Fore, Style
    from config.settings import COLORS
    
    color = getattr(Fore, COLORS.get(color_type, "WHITE").upper())
    print(f"{color}{message}{Style.RESET_ALL}")

# Global backup manager instance
backup_manager = BackupManager()