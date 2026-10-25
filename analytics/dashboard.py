"""
Real-Time Analytics Dashboard
Dashboard interaktif untuk monitoring search activities, API usage, dan trends secara real-time.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import print_colored, clear_screen
from colorama import Fore, Style


class AnalyticsDashboard:
    """Real-time analytics dashboard for monitoring search activities"""
    
    def __init__(self):
        self.db_path = "data/app_data.db"
    
    def get_realtime_stats(self):
        """Get real-time statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Searches in last hour
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) FROM search_history WHERE timestamp > ?",
                (one_hour_ago,)
            )
            searches_last_hour = cursor.fetchone()[0]
            
            # Most searched locations (today)
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT json_extract(result_json, '$.Kota/Town') as city, COUNT(*) as count
                FROM search_history
                WHERE timestamp LIKE ? AND json_extract(result_json, '$.Kota/Town') IS NOT NULL
                GROUP BY city
                ORDER BY count DESC
                LIMIT 10
            """, (f"{today}%",))
            top_locations = cursor.fetchall()
            
            # API success rate (based on results found)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN json_extract(result_json, '$.Source') = 'API/Database' THEN 1 ELSE 0 END) as successful
                FROM search_history
                WHERE timestamp > ?
            """, (one_hour_ago,))
            total, successful = cursor.fetchone()
            success_rate = (successful / total * 100) if total > 0 else 0
            
            # Total searches today
            cursor.execute(
                "SELECT COUNT(*) FROM search_history WHERE timestamp LIKE ?",
                (f"{today}%",)
            )
            searches_today = cursor.fetchone()[0]
            
            # Total searches all time
            cursor.execute("SELECT COUNT(*) FROM search_history")
            total_searches = cursor.fetchone()[0]
            
            # Unique targets
            cursor.execute("SELECT COUNT(DISTINCT target) FROM search_history")
            unique_targets = cursor.fetchone()[0]
            
            # Phone vs NIK searches
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN target LIKE '08%' THEN 1 ELSE 0 END) as phone_count,
                    SUM(CASE WHEN target NOT LIKE '08%' THEN 1 ELSE 0 END) as nik_count
                FROM search_history
            """)
            phone_count, nik_count = cursor.fetchone()
            
            conn.close()
            
            return {
                'searches_last_hour': searches_last_hour,
                'searches_today': searches_today,
                'total_searches': total_searches,
                'unique_targets': unique_targets,
                'top_locations': top_locations,
                'api_success_rate': success_rate,
                'phone_count': phone_count or 0,
                'nik_count': nik_count or 0
            }
        except Exception as e:
            print_colored(f"[!] Error getting realtime stats: {str(e)}", "ERROR")
            return {
                'searches_last_hour': 0,
                'searches_today': 0,
                'total_searches': 0,
                'unique_targets': 0,
                'top_locations': [],
                'api_success_rate': 0,
                'phone_count': 0,
                'nik_count': 0
            }
    
    def get_hourly_trend(self, hours=24):
        """Get hourly search counts for trend chart"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hourly_counts = []
            for i in range(hours, 0, -1):
                hour_start = (datetime.now() - timedelta(hours=i)).strftime("%Y-%m-%d %H:00:00")
                hour_end = (datetime.now() - timedelta(hours=i-1)).strftime("%Y-%m-%d %H:00:00")
                
                cursor.execute(
                    "SELECT COUNT(*) FROM search_history WHERE timestamp BETWEEN ? AND ?",
                    (hour_start, hour_end)
                )
                count = cursor.fetchone()[0]
                hourly_counts.append(count)
            
            conn.close()
            return hourly_counts
        except Exception as e:
            print_colored(f"[!] Error getting hourly trend: {str(e)}", "ERROR")
            return [0] * hours
    
    def get_operator_distribution(self):
        """Get distribution of searches by operator"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT json_extract(result_json, '$.Operator') as operator, COUNT(*) as count
                FROM search_history
                WHERE json_extract(result_json, '$.Operator') IS NOT NULL
                GROUP BY operator
                ORDER BY count DESC
            """)
            
            operators = cursor.fetchall()
            conn.close()
            
            return {op: count for op, count in operators if op}
        except Exception as e:
            print_colored(f"[!] Error getting operator distribution: {str(e)}", "ERROR")
            return {}
    
    def get_gender_distribution(self):
        """Get distribution of searches by gender"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT json_extract(result_json, '$.Jenis Kelamin') as gender, COUNT(*) as count
                FROM search_history
                WHERE json_extract(result_json, '$.Jenis Kelamin') IS NOT NULL
                GROUP BY gender
                ORDER BY count DESC
            """)
            
            genders = cursor.fetchall()
            conn.close()
            
            return {g: count for g, count in genders if g}
        except Exception as e:
            print_colored(f"[!] Error getting gender distribution: {str(e)}", "ERROR")
            return {}
    
    def display_dashboard(self):
        """Display real-time dashboard"""
        stats = self.get_realtime_stats()
        
        clear_screen()
        print_colored("╔════════════════════════════════════════════════════════════════════╗", "INFO")
        print_colored("║              PEGASUS - REAL-TIME ANALYTICS DASHBOARD               ║", "SUCCESS")
        print_colored("╚════════════════════════════════════════════════════════════════════╝", "INFO")
        
        print(f"\n{Fore.CYAN}📊 KEY METRICS (Last Hour){Style.RESET_ALL}")
        print_colored("─" * 70, "INFO")
        
        # Searches
        print(f"🔍 Total Searches (Last Hour): {Fore.GREEN}{stats['searches_last_hour']}{Style.RESET_ALL}")
        print(f"📅 Total Searches (Today): {Fore.GREEN}{stats['searches_today']}{Style.RESET_ALL}")
        print(f"📈 Total Searches (All Time): {Fore.GREEN}{stats['total_searches']}{Style.RESET_ALL}")
        print(f"🎯 Unique Targets: {Fore.GREEN}{stats['unique_targets']}{Style.RESET_ALL}")
        
        # Success Rate
        rate = stats['api_success_rate']
        color = Fore.GREEN if rate > 90 else Fore.YELLOW if rate > 70 else Fore.RED
        print(f"✓ API Success Rate: {color}{rate:.1f}%{Style.RESET_ALL}")
        
        # Search Type Distribution
        print(f"\n{Fore.CYAN}📱 SEARCH TYPE DISTRIBUTION{Style.RESET_ALL}")
        print_colored("─" * 70, "INFO")
        total = stats['phone_count'] + stats['nik_count']
        if total > 0:
            phone_pct = (stats['phone_count'] / total) * 100
            nik_pct = (stats['nik_count'] / total) * 100
            print(f"  Phone Numbers: {Fore.GREEN}{stats['phone_count']}{Style.RESET_ALL} ({phone_pct:.1f}%)")
            print(f"  NIK: {Fore.GREEN}{stats['nik_count']}{Style.RESET_ALL} ({nik_pct:.1f}%)")
        
        # Top Locations
        if stats['top_locations']:
            print(f"\n{Fore.CYAN}📍 TOP LOCATIONS (Today){Style.RESET_ALL}")
            print_colored("─" * 70, "INFO")
            max_count = max([count for _, count in stats['top_locations']]) if stats['top_locations'] else 1
            for i, (city, count) in enumerate(stats['top_locations'][:5], 1):
                bar_length = int((count / max_count) * 30)
                bar = "█" * bar_length
                print(f"{i}. {city:20} {bar} {count}")
        
        # Operator Distribution
        operators = self.get_operator_distribution()
        if operators:
            print(f"\n{Fore.CYAN}📡 TOP OPERATORS{Style.RESET_ALL}")
            print_colored("─" * 70, "INFO")
            max_count = max(operators.values())
            for op, count in sorted(operators.items(), key=lambda x: x[1], reverse=True)[:5]:
                bar_length = int((count / max_count) * 30)
                bar = "█" * bar_length
                print(f"  {op:15} {bar} {count}")
        
        # Trend Chart (last 24 hours)
        print(f"\n{Fore.CYAN}📈 SEARCH TREND (24 Hours){Style.RESET_ALL}")
        print_colored("─" * 70, "INFO")
        self._display_trend_chart()
    
    def _display_trend_chart(self):
        """Display ASCII trend chart"""
        hourly_counts = self.get_hourly_trend(24)
        
        if not hourly_counts or all(c == 0 for c in hourly_counts):
            print_colored("  [No data available]", "WARNING")
            return
        
        max_count = max(hourly_counts) if hourly_counts else 1
        chart_height = 10
        
        for level in range(chart_height, 0, -1):
            line = ""
            for count in hourly_counts:
                normalized = (count / max_count) * chart_height if max_count > 0 else 0
                if normalized >= level:
                    line += "█"
                else:
                    line += " "
            print(f"{level:2} │ {line}")
        
        print("   └" + "─" * 24)
        print("     " + "".join([str(i % 10) for i in range(24)]))
        print("     Hours ago →")
    
    def generate_weekly_report(self):
        """Generate comprehensive weekly report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            # Total searches
            cursor.execute(
                "SELECT COUNT(*) FROM search_history WHERE timestamp > ?",
                (week_ago,)
            )
            total_searches = cursor.fetchone()[0]
            
            # Unique targets
            cursor.execute("""
                SELECT COUNT(DISTINCT target) 
                FROM search_history 
                WHERE timestamp > ?
            """, (week_ago,))
            unique_targets = cursor.fetchone()[0]
            
            # Peak hours
            cursor.execute("""
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM search_history
                WHERE timestamp > ?
                GROUP BY hour
                ORDER BY count DESC
                LIMIT 5
            """, (week_ago,))
            peak_hours = cursor.fetchall()
            
            # Most common operators
            cursor.execute("""
                SELECT json_extract(result_json, '$.Operator') as operator, COUNT(*) as count
                FROM search_history
                WHERE timestamp > ? AND json_extract(result_json, '$.Operator') IS NOT NULL
                GROUP BY operator
                ORDER BY count DESC
            """, (week_ago,))
            top_operators = cursor.fetchall()
            
            # Daily breakdown
            cursor.execute("""
                SELECT strftime('%Y-%m-%d', timestamp) as day, COUNT(*) as count
                FROM search_history
                WHERE timestamp > ?
                GROUP BY day
                ORDER BY day
            """, (week_ago,))
            daily_breakdown = cursor.fetchall()
            
            conn.close()
            
            report = {
                'period': 'Last 7 Days',
                'total_searches': total_searches,
                'unique_targets': unique_targets,
                'avg_searches_per_day': total_searches / 7 if total_searches > 0 else 0,
                'peak_hours': peak_hours,
                'top_operators': top_operators,
                'daily_breakdown': daily_breakdown
            }
            
            self._display_weekly_report(report)
            return report
        except Exception as e:
            print_colored(f"[!] Error generating weekly report: {str(e)}", "ERROR")
            return None
    
    def _display_weekly_report(self, report):
        """Display weekly report"""
        print_colored("\n╔════════════════════════════════════════════════════════════════════╗", "INFO")
        print_colored("║                    WEEKLY ANALYTICS REPORT                         ║", "SUCCESS")
        print_colored("╚════════════════════════════════════════════════════════════════════╝", "INFO")
        
        print(f"\n{Fore.CYAN}📅 Period: {report['period']}{Style.RESET_ALL}\n")
        
        print(f"Total Searches: {Fore.GREEN}{report['total_searches']}{Style.RESET_ALL}")
        print(f"Unique Targets: {Fore.GREEN}{report['unique_targets']}{Style.RESET_ALL}")
        print(f"Avg per Day: {Fore.GREEN}{report['avg_searches_per_day']:.1f}{Style.RESET_ALL}")
        
        if report['daily_breakdown']:
            print(f"\n{Fore.CYAN}📅 Daily Breakdown:{Style.RESET_ALL}")
            for day, count in report['daily_breakdown']:
                print(f"  {day}: {count} searches")
        
        if report['peak_hours']:
            print(f"\n{Fore.CYAN}⏰ Peak Hours:{Style.RESET_ALL}")
            for hour, count in report['peak_hours']:
                print(f"  {hour}:00 - {int(hour)+1:02d}:00 → {count} searches")
        
        if report['top_operators']:
            print(f"\n{Fore.CYAN}📱 Top Operators:{Style.RESET_ALL}")
            for operator, count in report['top_operators']:
                print(f"  {operator}: {count} searches")
