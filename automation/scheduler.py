"""
Scheduled Tasks & Automation
Automated tasks seperti scheduled reports, data cleanup, backups, dan monitoring.
"""

import os
import sys
import threading
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import print_colored

# Try to import schedule library
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Schedule library not installed. Scheduler will use simple timing.")


class TaskScheduler:
    """Task scheduler for automated maintenance and reporting"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.tasks = []
        self.last_run = {}
    
    def start(self):
        """Start scheduler dalam background thread"""
        if self.running:
            print_colored("[!] Scheduler is already running", "WARNING")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print_colored("[✓] Task scheduler started", "SUCCESS")
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print_colored("[✓] Task scheduler stopped", "SUCCESS")
    
    def _run_scheduler(self):
        """Run scheduler loop"""
        if SCHEDULE_AVAILABLE:
            self._setup_schedule_tasks()
            
            # Run scheduler
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        else:
            # Simple timing-based scheduler
            self._run_simple_scheduler()
    
    def _setup_schedule_tasks(self):
        """Setup scheduled tasks using schedule library"""
        # Daily backup at 2 AM
        schedule.every().day.at("02:00").do(self.daily_backup)
        
        # Weekly report every Monday at 9 AM
        schedule.every().monday.at("09:00").do(self.weekly_report)
        
        # Hourly health check
        schedule.every().hour.do(self.health_check)
        
        # Daily cleanup at 3 AM
        schedule.every().day.at("03:00").do(self.cleanup_old_data)
    
    def _run_simple_scheduler(self):
        """Run simple timing-based scheduler"""
        while self.running:
            now = datetime.now()
            
            # Daily backup at 2 AM
            if now.hour == 2 and now.minute == 0:
                self._run_if_not_run_today('daily_backup', self.daily_backup)
            
            # Weekly report every Monday at 9 AM
            if now.weekday() == 0 and now.hour == 9 and now.minute == 0:
                self._run_if_not_run_today('weekly_report', self.weekly_report)
            
            # Hourly health check
            if now.minute == 0:
                self._run_if_not_run_this_hour('health_check', self.health_check)
            
            # Daily cleanup at 3 AM
            if now.hour == 3 and now.minute == 0:
                self._run_if_not_run_today('cleanup', self.cleanup_old_data)
            
            time.sleep(60)  # Check every minute
    
    def _run_if_not_run_today(self, task_name, task_func):
        """Run task if not already run today"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_run.get(task_name) != today:
            try:
                task_func()
                self.last_run[task_name] = today
            except Exception as e:
                print_colored(f"[!] Error in {task_name}: {str(e)}", "ERROR")
    
    def _run_if_not_run_this_hour(self, task_name, task_func):
        """Run task if not already run this hour"""
        this_hour = datetime.now().strftime("%Y-%m-%d %H")
        if self.last_run.get(task_name) != this_hour:
            try:
                task_func()
                self.last_run[task_name] = this_hour
            except Exception as e:
                print_colored(f"[!] Error in {task_name}: {str(e)}", "ERROR")
    
    def daily_backup(self):
        """Daily automated backup"""
        print_colored("[*] Running scheduled backup...", "INFO")
        try:
            from utils.backup_manager import BackupManager
            backup_manager = BackupManager()
            backup_manager.create_backup()
            
            from utils.logger import audit_logger
            audit_logger.log_info("Scheduled backup completed")
            print_colored("[✓] Scheduled backup completed", "SUCCESS")
        except Exception as e:
            print_colored(f"[!] Backup failed: {str(e)}", "ERROR")
    
    def weekly_report(self):
        """Weekly automated report"""
        print_colored("[*] Generating weekly report...", "INFO")
        try:
            from analytics.dashboard import AnalyticsDashboard
            dashboard = AnalyticsDashboard()
            report = dashboard.generate_weekly_report()
            
            # Export report to file
            if report:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"exports/weekly_report_{timestamp}.json"
                
                import json
                os.makedirs("exports", exist_ok=True)
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                
                print_colored(f"[✓] Weekly report saved to: {filename}", "SUCCESS")
            
            from utils.logger import audit_logger
            audit_logger.log_info("Weekly report generated")
        except Exception as e:
            print_colored(f"[!] Report generation failed: {str(e)}", "ERROR")
    
    def health_check(self):
        """Hourly health check"""
        try:
            from utils.health_check import health_checker
            is_healthy = health_checker.check_api_health(silent=True)
            
            if not is_healthy:
                print_colored("[!] Health check: API is unhealthy", "WARNING")
                from utils.logger import audit_logger
                audit_logger.log_error("health_check", "API is unhealthy")
            else:
                # Only log periodically to avoid noise
                if datetime.now().minute == 0:
                    print_colored("[✓] Health check passed", "SUCCESS")
        except Exception as e:
            print_colored(f"[!] Health check failed: {str(e)}", "ERROR")
    
    def cleanup_old_data(self):
        """Clean up old data"""
        print_colored("[*] Cleaning up old data...", "INFO")
        try:
            import sqlite3
            conn = sqlite3.connect("data/app_data.db")
            cursor = conn.cursor()
            
            # Delete searches older than 90 days (but keep favorites)
            ninety_days_ago = (datetime.now() - timedelta(days=90)).isoformat()
            cursor.execute(
                "DELETE FROM search_history WHERE timestamp < ? AND is_favorite = 0",
                (ninety_days_ago,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print_colored(f"[✓] Cleaned up {deleted_count} old records", "SUCCESS")
            
            from utils.logger import audit_logger
            audit_logger.log_info(f"Cleanup completed: {deleted_count} records deleted")
        except Exception as e:
            print_colored(f"[!] Cleanup failed: {str(e)}", "ERROR")
    
    def run_task_now(self, task_name):
        """Run a specific task immediately"""
        tasks = {
            'backup': self.daily_backup,
            'report': self.weekly_report,
            'health': self.health_check,
            'cleanup': self.cleanup_old_data
        }
        
        if task_name in tasks:
            print_colored(f"[*] Running task: {task_name}", "INFO")
            tasks[task_name]()
        else:
            print_colored(f"[!] Unknown task: {task_name}", "ERROR")
            print_colored(f"[i] Available tasks: {', '.join(tasks.keys())}", "INFO")


# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
