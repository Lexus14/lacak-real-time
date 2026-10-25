"""
Web API & REST Interface
Expose aplikasi functionality via REST API untuk integration dengan systems lain.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from functools import wraps

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import Flask
try:
    from flask import Flask, request, jsonify, make_response
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. API server will not be available.")

from managers.user_manager import UserManager
from models.user import Permission
from utils.api_client import perform_real_lookup
from utils.input_validator import validator
from utils.helpers import normalize_api_response, print_colored
from analytics.dashboard import AnalyticsDashboard
from ml.anomaly_detector import AnomalyDetector


class APIServer:
    """REST API Server for Pegasus Lacak Nomor"""
    
    def __init__(self, host='0.0.0.0', port=5000, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        self.app = None
        self.user_manager = UserManager()
        self.anomaly_detector = AnomalyDetector()
        
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)
            self.app.config['SECRET_KEY'] = os.urandom(24)
            self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        # Health check endpoint
        @self.app.route('/api/v1/health', methods=['GET'])
        def api_health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '3.0',
                'api_version': 'v1'
            }), 200
        
        # Authentication endpoint
        @self.app.route('/api/v1/auth/login', methods=['POST'])
        def api_login():
            """API endpoint untuk authentication"""
            data = request.get_json() or {}
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            if self.user_manager.authenticate(username, password):
                # Generate simple session token
                import secrets
                token = secrets.token_urlsafe(32)
                
                return jsonify({
                    'success': True,
                    'token': token,
                    'user': {
                        'username': username,
                        'role': self.user_manager.current_user.role.value
                    }
                }), 200
            else:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Phone search endpoint
        @self.app.route('/api/v1/search/phone', methods=['POST'])
        def api_search_phone():
            """API endpoint untuk phone search"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get current user (simplified - in production use JWT)
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if not self.user_manager.current_user.has_permission(Permission.SEARCH_PHONE):
                return jsonify({'error': 'Permission denied'}), 403
            
            data = request.get_json() or {}
            phone = data.get('phone')
            
            if not phone:
                return jsonify({'error': 'Phone number required'}), 400
            
            # Validate input
            is_valid, target_type, result_or_error = validator.validate_target(phone)
            
            if not is_valid:
                return jsonify({'error': result_or_error}), 400
            
            # Cleaned target
            phone = result_or_error
            
            # Perform search
            api_result = perform_real_lookup(phone)
            
            if api_result:
                normalized = self._normalize_api_response(api_result, phone)
                
                # Check for anomaly
                search_entry = {
                    'target': phone,
                    'timestamp': datetime.now().isoformat(),
                    'result': normalized
                }
                
                if self.anomaly_detector.is_trained:
                    is_anomaly, confidence, reasons = self.anomaly_detector.detect_anomaly(search_entry)
                    if is_anomaly:
                        normalized['anomaly_warning'] = {
                            'detected': True,
                            'confidence': confidence,
                            'reasons': reasons
                        }
                
                return jsonify({
                    'success': True,
                    'data': normalized
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Not found'
                }), 404
        
        # NIK search endpoint
        @self.app.route('/api/v1/search/nik', methods=['POST'])
        def api_search_nik():
            """API endpoint untuk NIK search"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get current user
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if not self.user_manager.current_user.has_permission(Permission.SEARCH_NIK):
                return jsonify({'error': 'Permission denied'}), 403
            
            data = request.get_json() or {}
            nik = data.get('nik')
            
            if not nik:
                return jsonify({'error': 'NIK required'}), 400
            
            # Validate input
            is_valid, target_type, result_or_error = validator.validate_target(nik)
            
            if not is_valid:
                return jsonify({'error': result_or_error}), 400
            
            # Cleaned target
            nik = result_or_error
            
            # Perform search
            api_result = perform_real_lookup(nik)
            
            if api_result:
                normalized = self._normalize_api_response(api_result, nik)
                
                return jsonify({
                    'success': True,
                    'data': normalized
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Not found'
                }), 404
        
        # Get history endpoint
        @self.app.route('/api/v1/history', methods=['GET'])
        def api_get_history():
            """API endpoint untuk get search history"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if not self.user_manager.current_user.has_permission(Permission.VIEW_HISTORY):
                return jsonify({'error': 'Permission denied'}), 403
            
            # Get query parameters
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            from utils.history_manager import HistoryManager
            history_manager = HistoryManager()
            history = history_manager.get_all_history(limit=limit)
            
            return jsonify({
                'success': True,
                'data': history,
                'total': len(history)
            }), 200
        
        # Analytics stats endpoint
        @self.app.route('/api/v1/analytics/stats', methods=['GET'])
        def api_get_stats():
            """API endpoint untuk analytics stats"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            dashboard = AnalyticsDashboard()
            stats = dashboard.get_realtime_stats()
            
            return jsonify({
                'success': True,
                'data': stats
            }), 200
        
        # Analytics trends endpoint
        @self.app.route('/api/v1/analytics/trends', methods=['GET'])
        def api_get_trends():
            """API endpoint untuk analytics trends"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            hours = request.args.get('hours', 24, type=int)
            
            dashboard = AnalyticsDashboard()
            trend = dashboard.get_hourly_trend(hours)
            
            return jsonify({
                'success': True,
                'data': {
                    'hours': hours,
                    'trend': trend
                }
            }), 200
        
        # Anomaly detection endpoint
        @self.app.route('/api/v1/analytics/anomalies', methods=['GET'])
        def api_get_anomalies():
            """API endpoint untuk get anomaly report"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if not self.anomaly_detector.is_trained:
                self.anomaly_detector.train()
            
            report = self.anomaly_detector.generate_report()
            
            return jsonify({
                'success': True,
                'data': report
            }), 200
        
        # Users list endpoint (admin only)
        @self.app.route('/api/v1/users', methods=['GET'])
        def api_get_users():
            """API endpoint untuk list users (admin only)"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if not self.user_manager.current_user.has_permission(Permission.MANAGE_USERS):
                return jsonify({'error': 'Permission denied'}), 403
            
            try:
                users = self.user_manager.list_users()
                return jsonify({
                    'success': True,
                    'data': users
                }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Create user endpoint (admin only)
        @self.app.route('/api/v1/users', methods=['POST'])
        def api_create_user():
            """API endpoint untuk create user (admin only)"""
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not self.user_manager.current_user:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if not self.user_manager.current_user.has_permission(Permission.MANAGE_USERS):
                return jsonify({'error': 'Permission denied'}), 403
            
            data = request.get_json() or {}
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            
            if not all([username, password, role]):
                return jsonify({'error': 'Username, password, and role required'}), 400
            
            try:
                user = self.user_manager.create_user(username, password, role)
                return jsonify({
                    'success': True,
                    'data': user.to_dict()
                }), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 400
    
    def _normalize_api_response(self, api_data, target):
        """Normalize API response to standard format"""
        from utils.helpers import format_timestamp, calculate_age, generate_email, generate_social_media
        
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
        
        # Generate missing fields if needed
        if 'Email' not in normalized and 'Nama' in normalized:
            normalized['Email'] = generate_email(normalized['Nama'])
        
        if 'Social Media' not in normalized and 'Nama' in normalized:
            normalized['Social Media'] = generate_social_media(normalized['Nama'])
        
        normalized['Source'] = 'API/Database'
        normalized['Target'] = target
        
        return normalized
    
    def run(self):
        """Run the API server"""
        if not FLASK_AVAILABLE:
            print_colored("[!] Flask is not installed. Cannot start API server.", "ERROR")
            print_colored("[i] Install with: pip install flask flask-cors", "INFO")
            return False
        
        print_colored(f"[*] Starting Pegasus API Server...", "INFO")
        print_colored(f"[*] Host: {self.host}:{self.port}", "INFO")
        print_colored(f"[*] Access: http://{self.host}:{self.port}", "INFO")
        print_colored(f"[*] Health Check: http://{self.host}:{self.port}/api/v1/health", "INFO")
        
        self.app.run(host=self.host, port=self.port, debug=self.debug)
        return True


def start_api_server(host='0.0.0.0', port=5000, debug=False):
    """Start the API server"""
    server = APIServer(host=host, port=port, debug=debug)
    return server.run()


if __name__ == '__main__':
    start_api_server()
