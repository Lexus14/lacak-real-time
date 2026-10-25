"""
Machine Learning - Anomaly Detection
Detect suspicious patterns, fraud attempts, atau unusual behavior menggunakan machine learning.
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
import math

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import print_colored


class SimpleAnomalyDetector:
    """
    Simple anomaly detector using rule-based and statistical methods
    (Lightweight alternative to sklearn for minimal dependencies)
    """
    
    def __init__(self):
        self.db_path = "data/app_data.db"
        self.is_trained = False
        self.baseline_stats = {}
    
    def get_search_history(self, limit=100):
        """Get recent search history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT target, timestamp, result_json FROM search_history ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                try:
                    result = json.loads(row[2]) if row[2] else {}
                except:
                    result = {}
                
                history.append({
                    'target': row[0],
                    'timestamp': row[1],
                    'result': result
                })
            
            return history
        except Exception as e:
            print_colored(f"[!] Error getting search history: {str(e)}", "ERROR")
            return []
    
    def train(self, search_history=None):
        """Train anomaly detection model (establish baselines)"""
        if search_history is None:
            search_history = self.get_search_history(200)
        
        if len(search_history) < 50:
            print_colored("[!] Need at least 50 searches to train model", "WARNING")
            return False
        
        # Calculate baseline statistics
        self.baseline_stats = {
            'avg_hourly_searches': self._calculate_avg_hourly_searches(search_history),
            'peak_hours': self._calculate_peak_hours(search_history),
            'common_targets': self._calculate_common_targets(search_history),
            'avg_target_length': self._calculate_avg_target_length(search_history)
        }
        
        self.is_trained = True
        print_colored("[✓] Anomaly detection model trained", "SUCCESS")
        return True
    
    def _calculate_avg_hourly_searches(self, history):
        """Calculate average searches per hour"""
        if not history:
            return 0
        
        # Group by hour
        hourly_counts = {}
        for entry in history:
            try:
                hour = datetime.fromisoformat(entry['timestamp']).hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            except:
                continue
        
        if not hourly_counts:
            return 0
        
        return sum(hourly_counts.values()) / len(hourly_counts)
    
    def _calculate_peak_hours(self, history):
        """Calculate peak hours (top 5)"""
        if not history:
            return []
        
        hourly_counts = {}
        for entry in history:
            try:
                hour = datetime.fromisoformat(entry['timestamp']).hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            except:
                continue
        
        # Get top 5 hours
        sorted_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:5]]
    
    def _calculate_common_targets(self, history):
        """Calculate most common targets"""
        target_counts = {}
        for entry in history:
            target = entry['target']
            target_counts[target] = target_counts.get(target, 0) + 1
        
        return target_counts
    
    def _calculate_avg_target_length(self, history):
        """Calculate average target length"""
        if not history:
            return 0
        
        lengths = [len(entry['target']) for entry in history]
        return sum(lengths) / len(lengths)
    
    def detect_anomaly(self, search_entry):
        """Detect if search is anomalous"""
        if not self.is_trained:
            return False, 0.0
        
        anomaly_score = 0.0
        reasons = []
        
        # Check unusual time
        try:
            hour = datetime.fromisoformat(search_entry['timestamp']).hour
            if hour not in self.baseline_stats.get('peak_hours', []):
                unusual_hours = [2, 3, 4, 5]  # Very unusual hours
                if hour in unusual_hours:
                    anomaly_score += 30
                    reasons.append(f"Unusual hour: {hour}:00")
        except:
            pass
        
        # Check rapid search pattern
        if self._is_rapid_search(search_entry):
            anomaly_score += 40
            reasons.append("Rapid search pattern")
        
        # Check repeated target
        target = search_entry['target']
        common_targets = self.baseline_stats.get('common_targets', {})
        if target in common_targets and common_targets[target] > 5:
            anomaly_score += 25
            reasons.append(f"Repeated target ({common_targets[target]} times)")
        
        # Check target length anomaly
        target_len = len(target)
        avg_len = self.baseline_stats.get('avg_target_length', 12)
        if abs(target_len - avg_len) > 5:
            anomaly_score += 10
            reasons.append("Unusual target length")
        
        is_anomaly = anomaly_score >= 50
        confidence = min(anomaly_score, 100)
        
        return is_anomaly, confidence, reasons
    
    def _is_rapid_search(self, search_entry):
        """Check if this is part of rapid search pattern"""
        try:
            current_time = datetime.fromisoformat(search_entry['timestamp'])
            
            # Get recent searches (last 10 minutes)
            recent_history = self.get_search_history(20)
            
            # Filter searches within last 10 minutes
            recent_count = 0
            for entry in recent_history:
                try:
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if (current_time - entry_time).total_seconds() < 600:  # 10 minutes
                        recent_count += 1
                except:
                    continue
            
            # If more than 10 searches in 10 minutes
            return recent_count > 10
        except:
            return False
    
    def analyze_patterns(self, search_history=None):
        """Analyze search patterns dan detect suspicious behavior"""
        if search_history is None:
            search_history = self.get_search_history(100)
        
        if not search_history:
            return {}
        
        patterns = {
            'rapid_fire_searches': self._detect_rapid_fire(search_history),
            'unusual_times': self._detect_unusual_times(search_history),
            'geographic_anomalies': self._detect_geo_anomalies(search_history),
            'repeated_targets': self._detect_repeated_targets(search_history),
            'high_volume_user': self._detect_high_volume(search_history)
        }
        
        return patterns
    
    def _detect_rapid_fire(self, history):
        """Detect rapid consecutive searches (potential abuse)"""
        if len(history) < 10:
            return False
        
        # Check if > 10 searches dalam 1 menit
        recent = history[:10]
        if len(recent) < 10:
            return False
        
        try:
            first_time = datetime.fromisoformat(recent[0]['timestamp'])
            last_time = datetime.fromisoformat(recent[-1]['timestamp'])
            duration = (first_time - last_time).total_seconds()
            
            return duration < 60  # Less than 1 minute
        except:
            return False
    
    def _detect_unusual_times(self, history):
        """Detect searches at unusual hours (e.g., 2-5 AM)"""
        unusual_hours = [2, 3, 4, 5]
        recent = history[:50]
        
        unusual_count = 0
        for entry in recent:
            try:
                hour = datetime.fromisoformat(entry['timestamp']).hour
                if hour in unusual_hours:
                    unusual_count += 1
            except:
                continue
        
        return unusual_count > 5  # More than 5 searches at unusual hours
    
    def _detect_geo_anomalies(self, history):
        """Detect geographic anomalies (e.g., sudden location jumps)"""
        # Get recent searches with location data
        locations = []
        for entry in history[:20]:
            city = entry['result'].get('Kota/Town')
            province = entry['result'].get('Provinsi')
            if city and province:
                locations.append((city, province))
        
        if len(locations) < 5:
            return False
        
        # Check for too many different locations (possible VPN/proxy usage)
        unique_locations = set(locations)
        return len(unique_locations) > 10  # More than 10 unique locations in 20 searches
    
    def _detect_repeated_targets(self, history):
        """Detect repeated searches for same target (stalking?)"""
        targets = [entry['target'] for entry in history[:50]]
        target_counts = {}
        
        for target in targets:
            target_counts[target] = target_counts.get(target, 0) + 1
        
        # Flag if any target searched > 5 times
        return any(count > 5 for count in target_counts.values())
    
    def _detect_high_volume(self, history):
        """Detect high volume user"""
        # Check if user has done > 100 searches in last 24 hours
        day_ago = (datetime.now() - timedelta(days=1)).isoformat()
        
        recent_count = 0
        for entry in history:
            try:
                if entry['timestamp'] > day_ago:
                    recent_count += 1
            except:
                continue
        
        return recent_count > 100
    
    def generate_report(self):
        """Generate anomaly detection report"""
        if not self.is_trained:
            trained = self.train()
            if not trained:
                return None
        
        history = self.get_search_history(100)
        patterns = self.analyze_patterns(history)
        
        # Count anomalies in recent searches
        anomaly_count = 0
        high_confidence_anomalies = 0
        
        for entry in history[:20]:
            is_anomaly, confidence, reasons = self.detect_anomaly(entry)
            if is_anomaly:
                anomaly_count += 1
                if confidence > 70:
                    high_confidence_anomalies += 1
        
        return {
            'patterns': patterns,
            'anomaly_count': anomaly_count,
            'high_confidence_anomalies': high_confidence_anomalies,
            'total_checked': min(20, len(history)),
            'risk_level': self._calculate_risk_level(patterns, anomaly_count)
        }
    
    def _calculate_risk_level(self, patterns, anomaly_count):
        """Calculate overall risk level"""
        risk_score = 0
        
        if patterns.get('rapid_fire_searches'):
            risk_score += 30
        if patterns.get('unusual_times'):
            risk_score += 20
        if patterns.get('repeated_targets'):
            risk_score += 25
        if patterns.get('geographic_anomalies'):
            risk_score += 15
        if patterns.get('high_volume_user'):
            risk_score += 10
        
        risk_score += anomaly_count * 5
        
        if risk_score >= 70:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"


# For compatibility with code expecting sklearn-based detector
class AnomalyDetector(SimpleAnomalyDetector):
    """Alias for SimpleAnomalyDetector"""
    pass
