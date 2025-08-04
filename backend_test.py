#!/usr/bin/env python3
"""
CRITICAL SYSTEM RECOVERY TESTING - Post Bug Fix Verification
Testing Costa Rica search system after major lazy loading fix in main.py
Focus: Login systems, search functionality, admin panel, database access, system health
"""

import requests
import json
import sys
from datetime import datetime
import time
import re
import os
from typing import Dict, List, Any

# Configuration - Updated with correct credentials from review request
BACKEND_URL = "https://332af799-0cb6-41e3-b677-b093ae8e52d4.preview.emergentagent.com/api"

# Admin credentials from review request
ADMIN_CREDENTIALS = {
    "login": "master_admin",
    "password": "TuDatos2025!Ultra"
}

# Daticos credentials for testing
DATICOS_CREDENTIALS = [
    {"username": "CABEZAS", "password": "Hola2022"},
    {"username": "Saraya", "password": "12345"}
]

class CriticalSystemTester:
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
    
    def test_health_endpoint(self):
        """Test 1: Health endpoint - Critical after lazy loading fix"""
        print("🏥 Testing Health Endpoint (Critical after fix)...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_test(
                        "Health Endpoint", 
                        True, 
                        f"Health status: {data.get('status')}"
                    )
                else:
                    self.log_test(
                        "Health Endpoint", 
                        False, 
                        "Missing status in health response", 
                        data
                    )
            else:
                self.log_test(
                    "Health Endpoint", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Exception: {str(e)}")
    
    def test_system_health(self):
        """Test 2: System health endpoint - Verify all status endpoints work"""
        print("🔧 Testing System Health Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/system/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "services" in data:
                    db_status = data["services"].get("database", "unknown")
                    overall_status = data.get("status")
                    
                    self.log_test(
                        "System Health Check", 
                        True, 
                        f"Overall: {overall_status}, DB: {db_status}"
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
    
    def test_admin_authentication(self):
        """Test 3: Admin login with new credentials - Critical test"""
        print("🔐 Testing Admin Authentication (master_admin/TuDatos2025!Ultra)...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/admin/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    admin_info = data.get("admin", {})
                    self.log_test(
                        "Admin Authentication", 
                        True, 
                        f"Successfully logged in as {admin_info.get('username', 'admin')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False, 
                        "Missing success or token in response", 
                        data
                    )
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            
        return False
    
    def test_api_root(self):
        """Test 4: API root endpoint - Basic connectivity"""
        print("🏠 Testing API Root Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "version" in data:
                    self.log_test(
                        "API Root", 
                        True, 
                        f"API Version: {data['version']}, Message: {data['message']}"
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
    
    def test_database_access_endpoints(self):
        """Test 5: Database access endpoints - Verify 5000-record database access"""
        print("💾 Testing Database Access Endpoints...")
        
        # Test demographics query to verify database access
        try:
            demo_payload = {}
            
            response = self.session.post(
                f"{self.base_url}/demographics/query",
                json=demo_payload,
                timeout=15
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
                    total_fisica = data['total_personas_fisicas']
                    total_juridica = data['total_personas_juridicas']
                    total_records = total_fisica + total_juridica
                    
                    self.log_test(
                        "Database Access - Demographics", 
                        True, 
                        f"Total records: {total_records:,} (Fisica: {total_fisica:,}, Juridica: {total_juridica:,})"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test(
                        "Database Access - Demographics", 
                        False, 
                        f"Missing fields: {missing_fields}", 
                        data
                    )
            else:
                self.log_test(
                    "Database Access - Demographics", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Database Access - Demographics", False, f"Exception: {str(e)}")
    
    def test_search_functionality(self):
        """Test 6: Search functionality - Verify search endpoints work with lazy loading"""
        print("🔍 Testing Search Functionality...")
        
        # Test search by name
        test_names = ["Maria", "Jose", "Carlos"]
        
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
                        f"Search by Name '{name}'", 
                        True, 
                        f"Found {total} results"
                    )
                else:
                    self.log_test(
                        f"Search by Name '{name}'", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Search by Name '{name}'", False, f"Exception: {str(e)}")
        
        # Test search by cedula
        test_cedulas = ["123456789", "3101234567"]
        
        for cedula in test_cedulas:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/cedula/{cedula}", 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    found = data.get("found", False)
                    
                    self.log_test(
                        f"Search by Cedula {cedula}", 
                        True, 
                        f"Found: {found}"
                    )
                else:
                    self.log_test(
                        f"Search by Cedula {cedula}", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Search by Cedula {cedula}", False, f"Exception: {str(e)}")
    
    def test_admin_panel_functionality(self):
        """Test 7: Admin panel functionality - Test admin dashboard and user creation"""
        print("👨‍💼 Testing Admin Panel Functionality...")
        
        # Test admin dashboard stats
        try:
            response = self.session.get(f"{self.base_url}/admin/dashboard/stats", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
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
        
        # Test admin update stats endpoint
        try:
            response = self.session.get(f"{self.base_url}/admin/update-stats", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Admin Update Stats", 
                    True, 
                    f"Update stats retrieved successfully"
                )
            else:
                self.log_test(
                    "Admin Update Stats", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Admin Update Stats", False, f"Exception: {str(e)}")
    
    def test_daticos_credentials_validation(self):
        """Test 8: Daticos credentials validation - Test CABEZAS/Hola2022 and Saraya/12345"""
        print("🌐 Testing Daticos Credentials Validation...")
        
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
    
    def test_location_hierarchy(self):
        """Test 9: Location hierarchy endpoints - Basic data structure"""
        print("🌍 Testing Location Hierarchy...")
        
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
            self.log_test("Location Hierarchy", False, f"Exception: {str(e)}")
    
    def test_ultra_deep_extraction_status(self):
        """Test 10: Ultra Deep Extraction Status - Verify database statistics access"""
        print("🔥 Testing Ultra Deep Extraction Status...")
        
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
    
    def run_critical_tests(self):
        """Run all critical tests in priority order"""
        print("🚨 CRITICAL SYSTEM RECOVERY TESTING - POST BUG FIX")
        print("=" * 70)
        print("Testing system recovery after major lazy loading fix in main.py")
        print("Focus: Login, Search, Admin Panel, Database Access, System Health")
        print(f"Backend URL: {self.base_url}")
        print("=" * 70)
        
        # Priority 1: Health and basic system endpoints
        self.test_health_endpoint()
        self.test_system_health()
        self.test_api_root()
        
        # Priority 2: Admin login and admin panel functionality
        if self.test_admin_authentication():
            self.test_admin_panel_functionality()
            
            # Priority 3: Database access endpoints
            self.test_database_access_endpoints()
            
            # Priority 4: Search functionality with real database
            self.test_search_functionality()
            
            # Priority 5: All data access endpoints
            self.test_location_hierarchy()
            self.test_ultra_deep_extraction_status()
            self.test_daticos_credentials_validation()
            
        else:
            print("❌ Admin authentication failed - skipping authenticated tests")
        
        # Print summary
        print("=" * 70)
        print("📋 CRITICAL SYSTEM RECOVERY TEST SUMMARY")
        print("=" * 70)
        
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
        
        # Critical system assessment
        print("\n🔍 CRITICAL SYSTEM ASSESSMENT:")
        
        # Check if core systems are working
        health_working = any(r["test"] in ["Health Endpoint", "System Health Check"] and r["success"] for r in self.test_results)
        auth_working = any(r["test"] == "Admin Authentication" and r["success"] for r in self.test_results)
        db_working = any(r["test"] == "Database Access - Demographics" and r["success"] for r in self.test_results)
        search_working = any("Search by" in r["test"] and r["success"] for r in self.test_results)
        
        print(f"🏥 Health Endpoints: {'✅ WORKING' if health_working else '❌ FAILED'}")
        print(f"🔐 Admin Authentication: {'✅ WORKING' if auth_working else '❌ FAILED'}")
        print(f"💾 Database Access: {'✅ WORKING' if db_working else '❌ FAILED'}")
        print(f"🔍 Search Functionality: {'✅ WORKING' if search_working else '❌ FAILED'}")
        
        if health_working and auth_working and db_working and search_working:
            print("\n🎉 CRITICAL SYSTEM RECOVERY: SUCCESS")
            print("✅ All critical systems operational after lazy loading fix")
        else:
            print("\n⚠️ CRITICAL SYSTEM RECOVERY: PARTIAL")
            print("❌ Some critical systems still have issues")
        
        return passed, total

def main():
    """Main test execution"""
    tester = CriticalSystemTester()
    passed, total = tester.run_critical_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All critical tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} critical tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()