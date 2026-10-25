"""
Geospatial Analysis & Visualization
Visualisasi lokasi searches pada map, heat maps, clustering, dan geographic insights.
"""

import sqlite3
import os
import json
import math
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import print_colored


class GeospatialAnalyzer:
    """Geospatial analysis for search locations"""
    
    def __init__(self):
        self.db_path = "data/app_data.db"
        self.coordinates_cache = {}
        
        # Approximate coordinates for major Indonesian cities
        # In production, this would use a geocoding service
        self.city_coordinates = {
            'jakarta': (-6.2088, 106.8456),
            'surabaya': (-7.2575, 112.7521),
            'bandung': (-6.9175, 107.6191),
            'medan': (3.5952, 98.6722),
            'bekasi': (-6.2349, 106.9896),
            'tangerang': (-6.1783, 106.6319),
            'depok': (-6.4025, 106.7942),
            'semarang': (-7.0051, 110.4381),
            'palembang': (-2.9761, 104.7754),
            'makassar': (-5.1477, 119.4327),
            'south jakarta': (-6.2615, 106.8106),
            'north jakarta': (-6.1383, 106.8639),
            'west jakarta': (-6.1683, 106.7588),
            'east jakarta': (-6.2250, 106.9004),
            'central jakarta': (-6.1865, 106.8341),
            'yogyakarta': (-7.7971, 110.3688),
            'malang': (-7.9666, 112.6326),
            'samarinda': (-0.4948, 117.1436),
            'padang': (-0.9471, 100.4172),
            'denpasar': (-8.6705, 115.2126),
            'bogor': (-6.5944, 106.7892),
            'batam': (1.0828, 104.0305),
            'pekanbaru': (0.5071, 101.4478),
            'bandar lampung': (-5.3971, 105.2668),
            'sukabumi': (-6.9194, 106.9272),
            'cirebon': (-6.7320, 108.5523),
            'tasikmalaya': (-7.3274, 108.2207),
            'purwokerto': (-7.4244, 109.2301),
            'tegal': (-6.8797, 109.1256),
            'kendari': (-3.9985, 122.5129),
            'manado': (1.4748, 124.8421),
            'jayapura': (-2.5916, 140.6690),
            'sorong': (-0.8763, 131.2558),
            'ambon': (-3.6387, 128.1689),
            'ternate': (0.7953, 127.3844),
            'mataram': (-8.5833, 116.1167),
            'kupang': (-10.1772, 123.6070),
            'banda aceh': (5.5483, 95.3238),
            'lhokseumawe': (5.1880, 97.1404),
            'binjai': (3.5978, 98.4814),
            'pematangsiantar': (2.9700, 99.0682),
            'tanjungpinang': (0.9176, 104.4665),
            'batu': (-7.8671, 112.5239),
            'mojokerto': (-7.4707, 112.4407),
            'madiun': (-7.6311, 111.5300),
            'kediri': (-7.8232, 112.0150),
            'blitar': (-8.0955, 112.1602),
            'pasuruan': (-7.6469, 112.8990),
            'probolinggo': (-7.7764, 113.2037),
            'surakarta': (-7.5755, 110.8243),
            'salatiga': (-7.3305, 110.5084),
            'pekalongan': (-6.8896, 109.6750),
            'cilacap': (-7.6984, 109.0235),
            'kebumen': (-7.6681, 109.6525),
            'magelang': (-7.4797, 110.2177),
            'temanggung': (-7.3167, 110.1667),
            'wonosobo': (-7.3622, 109.8996),
            'banjarnegara': (-7.4021, 109.6811),
            'purbalingga': (-7.3881, 109.3650),
            'banyumas': (-7.5158, 109.2942),
            'cilacap': (-7.6984, 109.0235),
            'brebes': (-6.8703, 109.0500),
            'tegal': (-6.8797, 109.1256),
            'pemalang': (-6.8878, 109.3806),
            'kendal': (-6.9194, 110.2506),
            'batang': (-6.9123, 109.7289),
            'jepara': (-6.5596, 110.6720),
            'kudus': (-6.8041, 110.8382),
            'demak': (-6.8939, 110.6377),
            'grobogan': (-7.0216, 110.9619),
            'sragen': (-7.4264, 111.0214),
            'ngawi': (-7.3899, 111.4619),
            'magetan': (-7.6497, 111.3380),
            'ponorogo': (-7.8720, 111.4615),
            'trenggalek': (-8.0583, 111.7156),
            'tulungagung': (-8.0667, 111.9000),
            'nganjuk': (-7.6029, 111.9014),
            'jombang': (-7.5468, 112.2265),
            'lamongan': (-7.1258, 112.4149),
            'gresik': (-7.1567, 112.6555),
            'bangkalan': (-7.0300, 112.7500),
            'sampang': (-7.1877, 113.2394),
            'pamekasan': (-7.1619, 113.4733),
            'sumenep': (-6.9254, 113.9066),
            'sidoarjo': (-7.4530, 112.7183),
            'mojokerto': (-7.4707, 112.4407),
            'jombang': (-7.5468, 112.2265),
            'nganjuk': (-7.6029, 111.9014),
            'madiun': (-7.6311, 111.5300),
            'magetan': (-7.6497, 111.3380),
            'ngawi': (-7.3899, 111.4619),
            'bojonegoro': (-7.1502, 111.8810),
            'tuban': (-6.8980, 112.0530),
            'lamongan': (-7.1258, 112.4149),
        }
    
    def get_search_history_with_locations(self, limit=100):
        """Get search history with location data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT target, timestamp, result_json 
                FROM search_history 
                WHERE json_extract(result_json, '$.Kota/Town') IS NOT NULL
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            locations = []
            for row in rows:
                try:
                    result = json.loads(row[2]) if row[2] else {}
                except:
                    result = {}
                
                city = result.get('Kota/Town')
                province = result.get('Provinsi')
                
                if city:
                    locations.append({
                        'target': row[0],
                        'timestamp': row[1],
                        'city': city,
                        'province': province,
                        'result': result
                    })
            
            return locations
        except Exception as e:
            print_colored(f"[!] Error getting locations: {str(e)}", "ERROR")
            return []
    
    def geocode_location(self, city, province=None):
        """Convert city/province to lat/lon"""
        location_key = city.lower()
        
        if location_key in self.coordinates_cache:
            return self.coordinates_cache[location_key]
        
        # Check in known cities
        if location_key in self.city_coordinates:
            coords = self.city_coordinates[location_key]
            self.coordinates_cache[location_key] = coords
            return coords
        
        # Try partial match
        for known_city, coords in self.city_coordinates.items():
            if location_key in known_city or known_city in location_key:
                self.coordinates_cache[location_key] = coords
                return coords
        
        return None
    
    def create_heatmap_data(self, search_history=None):
        """Create heatmap data from search locations"""
        if search_history is None:
            search_history = self.get_search_history_with_locations(100)
        
        # Extract coordinates
        locations = []
        for entry in search_history:
            city = entry.get('city')
            province = entry.get('province')
            
            if city:
                coords = self.geocode_location(city, province)
                if coords:
                    locations.append({
                        'coords': coords,
                        'city': city,
                        'target': entry.get('target')
                    })
        
        return locations
    
    def create_heatmap_html(self, output_file="exports/heatmap.html"):
        """Create heatmap HTML file"""
        locations = self.create_heatmap_data()
        
        if not locations:
            print_colored("[!] No geocodable locations found", "WARNING")
            return None
        
        # Create HTML with Leaflet
        html_content = self._generate_heatmap_html(locations)
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print_colored(f"[✓] Heatmap saved to: {output_file}", "SUCCESS")
        return output_file
    
    def _generate_heatmap_html(self, locations):
        """Generate HTML for heatmap"""
        # Calculate center
        avg_lat = sum(loc['coords'][0] for loc in locations) / len(locations)
        avg_lon = sum(loc['coords'][1] for loc in locations) / len(locations)
        
        # Generate points for heatmap
        points_js = ",\n            ".join([f"[{loc['coords'][0]}, {loc['coords'][1]}, 0.8]" for loc in locations])
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Pegasus - Search Heatmap</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <style>
        #map {{ height: 100vh; width: 100%; }}
        body {{ margin: 0; padding: 0; }}
        .info {{
            padding: 6px 8px;
            font: 14px/16px Arial, Helvetica, sans-serif;
            background: white;
            background: rgba(255,255,255,0.8);
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{avg_lat}, {avg_lon}], 6);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        var heatData = [
            {points_js}
        ];
        
        var heat = L.heatLayer(heatData, {{
            radius: 25,
            blur: 15,
            maxZoom: 10,
            max: 1.0
        }}).addTo(map);
        
        // Add markers for each location
        var markers = L.layerGroup();
        """
        
        # Add markers
        for loc in locations:
            html += f"""
        L.marker([{loc['coords'][0]}, {loc['coords'][1]}])
            .bindPopup("<b>{loc['city']}</b><br>Target: {loc['target']}")
            .addTo(markers);
        """
        
        html += """
        markers.addTo(map);
        
        // Add legend
        var legend = L.control({position: 'bottomright'});
        legend.onAdd = function (map) {{
            var div = L.DomUtil.create('div', 'info legend');
            div.innerHTML = '<h4>Pegasus Search Heatmap</h4><p>""" + heatData.length + """ locations</p>';
            return div;
        }};
        legend.addTo(map);
    </script>
</body>
</html>"""
        
        return html
    
    def create_cluster_map_html(self, output_file="exports/cluster_map.html"):
        """Create cluster map HTML file"""
        locations = self.create_heatmap_data()
        
        if not locations:
            print_colored("[!] No geocodable locations found", "WARNING")
            return None
        
        # Calculate center
        avg_lat = sum(loc['coords'][0] for loc in locations) / len(locations)
        avg_lon = sum(loc['coords'][1] for loc in locations) / len(locations)
        
        # Generate HTML
        html_content = self._generate_cluster_map_html(locations, avg_lat, avg_lon)
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print_colored(f"[✓] Cluster map saved to: {output_file}", "SUCCESS")
        return output_file
    
    def _generate_cluster_map_html(self, locations, center_lat, center_lon):
        """Generate HTML for cluster map"""
        # Generate markers JS
        markers_js = ",\n            ".join([f"[{loc['coords'][0]}, {loc['coords'][1]}, \"<b>{loc['city']}</b><br>Target: {loc['target']}\"]" for loc in locations])
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Pegasus - Cluster Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <style>
        #map {{ height: 100vh; width: 100%; }}
        body {{ margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{center_lat}, {center_lon}], 6);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        var markers = L.markerClusterGroup();
        
        var locations = [
            {markers_js}
        ];
        
        for (var i = 0; i < locations.length; i++) {{
            var marker = L.marker([locations[i][0], locations[i][1]]);
            marker.bindPopup(locations[i][2]);
            markers.addLayer(marker);
        }}
        
        map.addLayer(markers);
    </script>
</body>
</html>"""
        
        return html
    
    def detect_geographic_clusters(self, search_history=None):
        """Detect geographic clusters using simple distance-based clustering"""
        if search_history is None:
            search_history = self.get_search_history_with_locations(100)
        
        # Extract coordinates
        coordinates = []
        location_data = []
        
        for entry in search_history:
            city = entry.get('city')
            province = entry.get('province')
            
            if city:
                coords = self.geocode_location(city, province)
                if coords:
                    coordinates.append(coords)
                    location_data.append({
                        'coords': coords,
                        'city': city,
                        'target': entry.get('target')
                    })
        
        if len(coordinates) < 3:
            return []
        
        # Simple distance-based clustering
        # Group points within 0.5 degrees (approx 55km)
        eps = 0.5
        clusters = []
        visited = set()
        
        for i, coord1 in enumerate(coordinates):
            if i in visited:
                continue
            
            cluster = [location_data[i]]
            visited.add(i)
            
            for j, coord2 in enumerate(coordinates[i+1:], i+1):
                if j in visited:
                    continue
                
                distance = self._haversine_distance(coord1, coord2)
                if distance <= eps:
                    cluster.append(location_data[j])
                    visited.add(j)
            
            if len(cluster) >= 3:  # Minimum cluster size
                clusters.append(cluster)
        
        return clusters
    
    def _haversine_distance(self, coord1, coord2):
        """Calculate distance between two coordinates in degrees"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Simple Euclidean distance in degrees (sufficient for clustering)
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
    
    def calculate_search_radius(self, search_history=None):
        """Calculate geographic radius of searches"""
        if search_history is None:
            search_history = self.get_search_history_with_locations(100)
        
        coordinates = []
        for entry in search_history:
            city = entry.get('city')
            province = entry.get('province')
            
            if city:
                coords = self.geocode_location(city, province)
                if coords:
                    coordinates.append(coords)
        
        if len(coordinates) < 2:
            return 0
        
        # Calculate center point
        center_lat = sum(c[0] for c in coordinates) / len(coordinates)
        center_lon = sum(c[1] for c in coordinates) / len(coordinates)
        center = (center_lat, center_lon)
        
        # Calculate max distance from center (in km)
        max_distance = max(self._haversine_distance_km(center, coord) for coord in coordinates)
        
        return max_distance
    
    def _haversine_distance_km(self, coord1, coord2):
        """Calculate distance between two coordinates in km"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def get_location_statistics(self):
        """Get statistics about locations in search history"""
        locations = self.get_search_history_with_locations(100)
        
        if not locations:
            return {}
        
        # Count by city
        city_counts = defaultdict(int)
        province_counts = defaultdict(int)
        
        for loc in locations:
            city_counts[loc['city']] += 1
            if loc['province']:
                province_counts[loc['province']] += 1
        
        # Calculate center
        coordinates = []
        for loc in locations:
            coords = self.geocode_location(loc['city'], loc.get('province'))
            if coords:
                coordinates.append(coords)
        
        center = None
        if coordinates:
            center = {
                'lat': sum(c[0] for c in coordinates) / len(coordinates),
                'lon': sum(c[1] for c in coordinates) / len(coordinates)
            }
        
        return {
            'total_locations': len(locations),
            'unique_cities': len(city_counts),
            'unique_provinces': len(province_counts),
            'top_cities': dict(sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_provinces': dict(sorted(province_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'center': center,
            'search_radius_km': self.calculate_search_radius(locations)
        }
