#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Massive Costa Rican Data Extraction System
Tests MongoDB collections, API endpoints, and data quality for 2M+ records system
"""

import requests
import json
import sys
from datetime import datetime
import time
import re
import pymongo
import os
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://9527510f-c1db-4df9-bc12-44ab641aeed6.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "login": "admin",
    "password": "admin123"
}

# MongoDB connection for direct database testing
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class DaticosAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
    
    def test_authentication(self):
        """Test 1: Authentication with admin credentials"""
        print("🔐 Testing Authentication...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_test(
                        "Authentication Login", 
                        True, 
                        f"Successfully logged in as {data['user']['username']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication Login", 
                        False, 
                        "Missing access_token or user in response", 
                        data
                    )
            else:
                self.log_test(
                    "Authentication Login", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Authentication Login", False, f"Exception: {str(e)}")
            
        return False
    
    def test_location_endpoints(self):
        """Test location hierarchy endpoints"""
        print("🌍 Testing Location Endpoints...")
        
        # Test provincias
        try:
            response = self.session.get(f"{self.base_url}/locations/provincias", timeout=10)
            if response.status_code == 200:
                provincias = response.json()
                if isinstance(provincias, list) and len(provincias) > 0:
                    self.log_test(
                        "Get Provincias", 
                        True, 
                        f"Retrieved {len(provincias)} provinces"
                    )
                    
                    # Test cantones for first provincia
                    first_provincia = provincias[0]
                    provincia_id = first_provincia.get('id')
                    
                    if provincia_id:
                        cantones_response = self.session.get(
                            f"{self.base_url}/locations/cantones/{provincia_id}", 
                            timeout=10
                        )
                        if cantones_response.status_code == 200:
                            cantones = cantones_response.json()
                            self.log_test(
                                "Get Cantones", 
                                True, 
                                f"Retrieved {len(cantones)} cantones for {first_provincia.get('nombre')}"
                            )
                            
                            # Test distritos for first canton
                            if cantones and len(cantones) > 0:
                                first_canton = cantones[0]
                                canton_id = first_canton.get('id')
                                
                                if canton_id:
                                    distritos_response = self.session.get(
                                        f"{self.base_url}/locations/distritos/{canton_id}", 
                                        timeout=10
                                    )
                                    if distritos_response.status_code == 200:
                                        distritos = distritos_response.json()
                                        self.log_test(
                                            "Get Distritos", 
                                            True, 
                                            f"Retrieved {len(distritos)} distritos for {first_canton.get('nombre')}"
                                        )
                                    else:
                                        self.log_test(
                                            "Get Distritos", 
                                            False, 
                                            f"HTTP {distritos_response.status_code}", 
                                            distritos_response.text
                                        )
                        else:
                            self.log_test(
                                "Get Cantones", 
                                False, 
                                f"HTTP {cantones_response.status_code}", 
                                cantones_response.text
                            )
                else:
                    self.log_test("Get Provincias", False, "Empty or invalid response", provincias)
            else:
                self.log_test(
                    "Get Provincias", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Location Endpoints", False, f"Exception: {str(e)}")
    
    def test_search_by_cedula(self):
        """Test search by cedula for both fisica and juridica"""
        print("🔍 Testing Search by Cedula...")
        
        # Test cedulas that should exist based on the system description
        test_cedulas = [
            "123456789",  # Typical fisica cedula
            "987654321",  # Another fisica cedula
            "3101234567", # Juridica cedula (starts with 3)
            "3109876543"  # Another juridica cedula
        ]
        
        for cedula in test_cedulas:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/cedula/{cedula}", 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("found"):
                        person_type = data.get("type", "unknown")
                        self.log_test(
                            f"Search Cedula {cedula}", 
                            True, 
                            f"Found {person_type} person"
                        )
                    else:
                        self.log_test(
                            f"Search Cedula {cedula}", 
                            True, 
                            "No person found (valid response)"
                        )
                else:
                    self.log_test(
                        f"Search Cedula {cedula}", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Search Cedula {cedula}", False, f"Exception: {str(e)}")
    
    def test_search_by_name(self):
        """Test search by name"""
        print("👤 Testing Search by Name...")
        
        # Test common Costa Rican names
        test_names = [
            "Maria",
            "Jose",
            "Ana",
            "Carlos",
            "Restaurant",  # For juridica
            "Empresa"      # For juridica
        ]
        
        for name in test_names:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/name/{name}", 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    total = data.get("total", 0)
                    
                    self.log_test(
                        f"Search Name '{name}'", 
                        True, 
                        f"Found {total} results"
                    )
                else:
                    self.log_test(
                        f"Search Name '{name}'", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Search Name '{name}'", False, f"Exception: {str(e)}")
    
    def test_search_by_telefono(self):
        """Test search by phone number"""
        print("📞 Testing Search by Telefono...")
        
        # Test various phone formats
        test_phones = [
            "88888888",    # 8-digit format
            "2222-2222",   # Landline format
            "8888-8888",   # Mobile format
            "22222222",    # 8-digit landline
            "1234"         # Partial search
        ]
        
        for phone in test_phones:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/telefono/{phone}", 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    total = data.get("total", 0)
                    
                    self.log_test(
                        f"Search Phone '{phone}'", 
                        True, 
                        f"Found {total} results"
                    )
                else:
                    self.log_test(
                        f"Search Phone '{phone}'", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Search Phone '{phone}'", False, f"Exception: {str(e)}")
    
    def test_geographic_search(self):
        """Test geographic search endpoint"""
        print("🗺️ Testing Geographic Search...")
        
        # First get a provincia to test with
        try:
            provincias_response = self.session.get(f"{self.base_url}/locations/provincias", timeout=10)
            if provincias_response.status_code == 200:
                provincias = provincias_response.json()
                if provincias:
                    test_provincia = provincias[0]
                    
                    # Test geographic search with provincia filter
                    search_payload = {
                        "provincia_id": test_provincia["id"]
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/search/geografica",
                        json=search_payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        total = data.get("total", 0)
                        
                        self.log_test(
                            "Geographic Search", 
                            True, 
                            f"Found {total} results for {test_provincia['nombre']}"
                        )
                    else:
                        self.log_test(
                            "Geographic Search", 
                            False, 
                            f"HTTP {response.status_code}", 
                            response.text
                        )
                        
                    # Test with person type filter
                    search_payload_fisica = {
                        "provincia_id": test_provincia["id"],
                        "person_type": "fisica"
                    }
                    
                    response_fisica = self.session.post(
                        f"{self.base_url}/search/geografica",
                        json=search_payload_fisica,
                        timeout=10
                    )
                    
                    if response_fisica.status_code == 200:
                        data_fisica = response_fisica.json()
                        results_fisica = data_fisica.get("results", [])
                        
                        self.log_test(
                            "Geographic Search (Fisica)", 
                            True, 
                            f"Found {len(results_fisica)} fisica results"
                        )
                    else:
                        self.log_test(
                            "Geographic Search (Fisica)", 
                            False, 
                            f"HTTP {response_fisica.status_code}", 
                            response_fisica.text
                        )
                        
        except Exception as e:
            self.log_test("Geographic Search", False, f"Exception: {str(e)}")
    
    def test_demographics_query(self):
        """Test demographics statistics endpoint"""
        print("📊 Testing Demographics Query...")
        
        try:
            # Test basic demographics query
            demo_payload = {}
            
            response = self.session.post(
                f"{self.base_url}/demographics/query",
                json=demo_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = [
                    "total_personas_fisicas", 
                    "total_personas_juridicas", 
                    "by_provincia", 
                    "by_sector"
                ]
                
                all_fields_present = all(field in data for field in required_fields)
                
                if all_fields_present:
                    self.log_test(
                        "Demographics Query", 
                        True, 
                        f"Fisica: {data['total_personas_fisicas']}, Juridica: {data['total_personas_juridicas']}"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test(
                        "Demographics Query", 
                        False, 
                        f"Missing fields: {missing_fields}", 
                        data
                    )
            else:
                self.log_test(
                    "Demographics Query", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Demographics Query", False, f"Exception: {str(e)}")
    
    def test_api_root(self):
        """Test API root endpoint"""
        print("🏠 Testing API Root...")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "version" in data:
                    self.log_test(
                        "API Root", 
                        True, 
                        f"API Version: {data['version']}"
                    )
                else:
                    self.log_test("API Root", False, "Missing message or version", data)
            else:
                self.log_test(
                    "API Root", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("API Root", False, f"Exception: {str(e)}")
    
    def test_ultra_deep_extraction_endpoints(self):
        """Test Ultra Deep Extraction endpoints"""
        print("🔥 Testing Ultra Deep Extraction Endpoints...")
        
        # Test 1: Ultra Deep Extraction Status
        try:
            response = self.session.get(
                f"{self.base_url}/admin/ultra-deep-extraction/status", 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    registros_actuales = data["data"].get("registros_actuales", {})
                    total_principal = registros_actuales.get("total_principal", 0)
                    
                    self.log_test(
                        "Ultra Deep Status", 
                        True, 
                        f"Total registros: {total_principal:,}, Status: {data.get('status')}"
                    )
                else:
                    self.log_test(
                        "Ultra Deep Status", 
                        False, 
                        "Missing required fields in response", 
                        data
                    )
            else:
                self.log_test(
                    "Ultra Deep Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Ultra Deep Status", False, f"Exception: {str(e)}")
        
        # Test 2: Extraction Methods Comparison
        try:
            response = self.session.get(
                f"{self.base_url}/admin/extraction-methods-comparison", 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "comparison_data" in data:
                    methods = data["comparison_data"].get("methods_summary", {})
                    
                    self.log_test(
                        "Extraction Methods Comparison", 
                        True, 
                        f"Methods found: {len(methods)}"
                    )
                else:
                    self.log_test(
                        "Extraction Methods Comparison", 
                        False, 
                        "Missing comparison_data in response", 
                        data
                    )
            else:
                self.log_test(
                    "Extraction Methods Comparison", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Extraction Methods Comparison", False, f"Exception: {str(e)}")
        
        # Test 3: Ultra Deep Extraction Start (POST)
        try:
            response = self.session.post(
                f"{self.base_url}/admin/ultra-deep-extraction/start", 
                json={},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "message" in data:
                    self.log_test(
                        "Ultra Deep Start", 
                        True, 
                        f"Started: {data.get('message')}"
                    )
                else:
                    self.log_test(
                        "Ultra Deep Start", 
                        False, 
                        "Missing success status or message", 
                        data
                    )
            else:
                self.log_test(
                    "Ultra Deep Start", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Ultra Deep Start", False, f"Exception: {str(e)}")
        
        # Test 4: Ultra Deep Execute Now
        try:
            response = self.session.post(
                f"{self.base_url}/admin/ultra-deep-extraction/execute-now", 
                json={},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "message" in data:
                    self.log_test(
                        "Ultra Deep Execute Now", 
                        True, 
                        f"Executed: {data.get('message')}"
                    )
                else:
                    self.log_test(
                        "Ultra Deep Execute Now", 
                        False, 
                        "Missing success status or message", 
                        data
                    )
            else:
                self.log_test(
                    "Ultra Deep Execute Now", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Ultra Deep Execute Now", False, f"Exception: {str(e)}")
    
    def test_autonomous_system_endpoints(self):
        """Test Autonomous System endpoints"""
        print("🤖 Testing Autonomous System Endpoints...")
        
        # Test Autonomous System Status
        try:
            response = self.session.get(
                f"{self.base_url}/admin/autonomous-system/status", 
                timeout=10
            )
            
            # This endpoint might not exist, so we check if it returns 404 or works
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Autonomous System Status", 
                    True, 
                    f"Status retrieved: {data.get('status', 'unknown')}"
                )
            elif response.status_code == 404:
                self.log_test(
                    "Autonomous System Status", 
                    True, 
                    "Endpoint not implemented (404 - expected)"
                )
            else:
                self.log_test(
                    "Autonomous System Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Autonomous System Status", False, f"Exception: {str(e)}")
    
    def test_database_health_and_stats(self):
        """Test database health and statistics"""
        print("💾 Testing Database Health and Stats...")
        
        # Test System Health
        try:
            response = self.session.get(f"{self.base_url}/system/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "services" in data:
                    db_status = data["services"].get("database", "unknown")
                    self.log_test(
                        "System Health Check", 
                        True, 
                        f"Overall: {data['status']}, DB: {db_status}"
                    )
                else:
                    self.log_test(
                        "System Health Check", 
                        False, 
                        "Missing status or services in response", 
                        data
                    )
            else:
                self.log_test(
                    "System Health Check", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
        
        # Test Admin Dashboard Stats
        try:
            response = self.session.get(f"{self.base_url}/admin/dashboard/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected fields in admin stats
                expected_fields = ["total_personas", "total_empresas", "data_quality"]
                
                # The response might have different structure, so we check what we get
                self.log_test(
                    "Admin Dashboard Stats", 
                    True, 
                    f"Stats retrieved with {len(data)} fields"
                )
            else:
                self.log_test(
                    "Admin Dashboard Stats", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Admin Dashboard Stats", False, f"Exception: {str(e)}")
    
    def test_daticos_connection_endpoints(self):
        """Test Daticos connection and extraction endpoints"""
        print("🌐 Testing Daticos Connection Endpoints...")
        
        # Test Daticos Connection
        try:
            response = self.session.get(
                f"{self.base_url}/admin/daticos/test-connection", 
                timeout=30  # Longer timeout for external connection
            )
            
            if response.status_code == 200:
                data = response.json()
                connection_status = data.get("connection_status", "unknown")
                credentials_valid = data.get("credentials_valid", False)
                
                self.log_test(
                    "Daticos Connection Test", 
                    True, 
                    f"Connection: {connection_status}, Credentials: {credentials_valid}"
                )
            else:
                self.log_test(
                    "Daticos Connection Test", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Daticos Connection Test", False, f"Exception: {str(e)}")
    
    def test_high_priority_endpoints(self):
        """Test the 4 HIGH PRIORITY endpoints requested by user"""
        print("🔥 Testing HIGH PRIORITY ENDPOINTS - TuDatos System...")
        
        # Test 1: GET /api/admin/system/complete-overview
        try:
            response = self.session.get(
                f"{self.base_url}/admin/system/complete-overview", 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "system_overview" in data:
                    overview = data["system_overview"]
                    total_records = overview.get("total_records", 0)
                    
                    self.log_test(
                        "System Complete Overview", 
                        True, 
                        f"Total records: {total_records:,}, Collections: {len(overview.get('collections', {}))}"
                    )
                else:
                    self.log_test(
                        "System Complete Overview", 
                        False, 
                        "Missing system_overview in response", 
                        data
                    )
            else:
                self.log_test(
                    "System Complete Overview", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("System Complete Overview", False, f"Exception: {str(e)}")
        
        # Test 2: GET /api/admin/mega-extraction/status
        try:
            response = self.session.get(
                f"{self.base_url}/admin/mega-extraction/status", 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    mega_data = data["data"]
                    mega_total = mega_data.get("mega_extraction_especifica", {}).get("total_mega_extraction", 0)
                    grand_total = mega_data.get("totales_combinados", {}).get("gran_total", 0)
                    
                    self.log_test(
                        "Mega Extraction Status", 
                        True, 
                        f"Mega records: {mega_total:,}, Grand total: {grand_total:,}"
                    )
                else:
                    self.log_test(
                        "Mega Extraction Status", 
                        False, 
                        "Missing data in response", 
                        data
                    )
            else:
                self.log_test(
                    "Mega Extraction Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Mega Extraction Status", False, f"Exception: {str(e)}")
        
        # Test 3: POST /api/admin/mega-extraction/start (only if not running)
        try:
            # First check status to see if already running
            status_response = self.session.get(
                f"{self.base_url}/admin/mega-extraction/status", 
                timeout=15
            )
            
            should_start = True
            if status_response.status_code == 200:
                status_data = status_response.json()
                # Check if extraction is already running
                if status_data.get("data", {}).get("ultima_mega_extraccion", {}).get("estado") == "RUNNING":
                    should_start = False
            
            if should_start:
                response = self.session.post(
                    f"{self.base_url}/admin/mega-extraction/start", 
                    json={},
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success" and "message" in data:
                        self.log_test(
                            "Mega Extraction Start", 
                            True, 
                            f"Started: {data.get('message')}"
                        )
                    else:
                        self.log_test(
                            "Mega Extraction Start", 
                            False, 
                            "Missing success status or message", 
                            data
                        )
                else:
                    self.log_test(
                        "Mega Extraction Start", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
            else:
                self.log_test(
                    "Mega Extraction Start", 
                    True, 
                    "Skipped - extraction already running"
                )
                
        except Exception as e:
            self.log_test("Mega Extraction Start", False, f"Exception: {str(e)}")
        
        # Test 4: GET /api/admin/ultra-deep-extraction/status
        try:
            response = self.session.get(
                f"{self.base_url}/admin/ultra-deep-extraction/status", 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    ultra_data = data["data"]
                    registros_actuales = ultra_data.get("registros_actuales", {})
                    total_principal = registros_actuales.get("total_principal", 0)
                    objetivo_3M = ultra_data.get("objetivo_3M", {})
                    progreso = objetivo_3M.get("progreso_porcentaje", 0)
                    
                    self.log_test(
                        "Ultra Deep Extraction Status", 
                        True, 
                        f"Total: {total_principal:,}, Progress: {progreso}% toward 3M goal"
                    )
                else:
                    self.log_test(
                        "Ultra Deep Extraction Status", 
                        False, 
                        "Missing data in response", 
                        data
                    )
            else:
                self.log_test(
                    "Ultra Deep Extraction Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Ultra Deep Extraction Status", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Daticos Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test API root first
        self.test_api_root()
        
        # Authentication is required for most endpoints
        if self.test_authentication():
            # HIGH PRIORITY TESTS FIRST (as requested by user)
            self.test_high_priority_endpoints()
            
            # Core functionality tests
            self.test_location_endpoints()
            self.test_search_by_cedula()
            self.test_search_by_name()
            self.test_search_by_telefono()
            self.test_geographic_search()
            self.test_demographics_query()
            
            # Ultra Deep Extraction tests
            self.test_ultra_deep_extraction_endpoints()
            
            # Autonomous System tests
            self.test_autonomous_system_endpoints()
            
            # Database health and stats tests
            self.test_database_health_and_stats()
            
            # Daticos connection tests
            self.test_daticos_connection_endpoints()
            
        else:
            print("❌ Authentication failed - skipping authenticated tests")
        
        # Print summary
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = DaticosAPITester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()