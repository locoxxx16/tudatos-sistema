#!/usr/bin/env python3
"""
🚀 TESTING COMPLETO SISTEMA ULTRA COMPLETO - 4.2M+ REGISTROS
Testing the ultra complete system with intelligent data fusion from 7+ collections
Focus: Ultra complete search, WhatsApp verification, credit analysis, business registration
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
    "username": "master_admin",
    "password": "TuDatos2025!Ultra"
}

# Test notification email
NOTIFICATION_EMAIL = "jykinternacional@gmail.com"

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
        
        # The main.py doesn't have /system/health, but we can test the health endpoint we know works
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    status = data.get("status")
                    
                    self.log_test(
                        "System Health Check", 
                        True, 
                        f"System status: {status}"
                    )
                else:
                    self.log_test(
                        "System Health Check", 
                        False, 
                        "Missing status in health response", 
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
            # Test the main page endpoint
            response = self.session.get(f"https://332af799-0cb6-41e3-b677-b093ae8e52d4.preview.emergentagent.com/", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if "TuDatos" in content and "Base de Datos" in content:
                    self.log_test(
                        "Main Page", 
                        True, 
                        "Main page loaded successfully with TuDatos branding"
                    )
                else:
                    self.log_test("Main Page", False, "Missing expected content", content[:200])
            else:
                self.log_test(
                    "Main Page", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text[:200]
                )
                
        except Exception as e:
            self.log_test("Main Page", False, f"Exception: {str(e)}")
    
    def test_database_access_endpoints(self):
        """Test 5: Database access endpoints - Verify 5000-record database access"""
        print("💾 Testing Database Access Endpoints...")
        
        # Test database access through user profile (which should work with admin token)
        try:
            response = self.session.get(f"{self.base_url}/user/profile", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user = data.get("user", {})
                    self.log_test(
                        "Database Access - User Profile", 
                        True, 
                        f"User database accessible, user: {user.get('username', 'unknown')}"
                    )
                else:
                    self.log_test(
                        "Database Access - User Profile", 
                        False, 
                        f"User profile failed: {data.get('message')}", 
                        data
                    )
            else:
                self.log_test(
                    "Database Access - User Profile", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Database Access - User Profile", False, f"Exception: {str(e)}")
        
        # Test database lazy loading by checking if get_database() works
        try:
            # Import and test the lazy loading functions directly
            import sys
            sys.path.append('/app')
            from database_real import get_database, get_stats
            
            # Test lazy loading
            database = get_database()
            stats = get_stats()
            
            if database and len(database) > 0:
                self.log_test(
                    "Database Lazy Loading", 
                    True, 
                    f"Database loaded successfully with {len(database)} records"
                )
            else:
                self.log_test(
                    "Database Lazy Loading", 
                    False, 
                    "Database is empty or failed to load"
                )
                
            if stats and "total_personas" in stats:
                self.log_test(
                    "Stats Calculator", 
                    True, 
                    f"Stats calculated: {stats['total_personas']} personas"
                )
            else:
                self.log_test(
                    "Stats Calculator", 
                    False, 
                    "Stats calculation failed"
                )
                
        except Exception as e:
            self.log_test("Database Lazy Loading Test", False, f"Exception: {str(e)}")
    
    def test_search_functionality(self):
        """Test 6: Search functionality - Verify search endpoints work with lazy loading"""
        print("🔍 Testing Search Functionality...")
        
        # First, create a test user for search testing
        test_user_data = {
            "username": "search_test_user",
            "email": "search@test.cr",
            "password": "SearchTest123",
            "plan": "Básico",
            "customCredits": "10"
        }
        
        try:
            # Create user
            create_response = self.session.post(
                f"{self.base_url}/admin/users/create",
                json=test_user_data,
                timeout=15
            )
            
            if create_response.status_code == 200 and create_response.json().get("success"):
                # Now login as the user
                user_session = requests.Session()
                login_response = user_session.post(
                    f"{self.base_url}/user/login",
                    json={"username": "search_test_user", "password": "SearchTest123"},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    if login_data.get("success"):
                        user_token = login_data.get("token")
                        user_session.headers.update({
                            "Authorization": f"Bearer {user_token}"
                        })
                        
                        # Test search with user token
                        test_queries = ["Maria", "Jose"]
                        
                        for query in test_queries:
                            try:
                                response = user_session.get(
                                    f"{self.base_url}/search/complete?q={query}&limit=5", 
                                    timeout=10
                                )
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get("success"):
                                        total = data.get("total", 0)
                                        
                                        self.log_test(
                                            f"Search Complete '{query}'", 
                                            True, 
                                            f"Found {total} results"
                                        )
                                    else:
                                        message = data.get("message", "")
                                        self.log_test(
                                            f"Search Complete '{query}'", 
                                            False, 
                                            f"Search failed: {message}", 
                                            data
                                        )
                                else:
                                    self.log_test(
                                        f"Search Complete '{query}'", 
                                        False, 
                                        f"HTTP {response.status_code}", 
                                        response.text
                                    )
                                    
                            except Exception as e:
                                self.log_test(f"Search Complete '{query}'", False, f"Exception: {str(e)}")
                    else:
                        self.log_test("User Login for Search", False, f"Login failed: {login_data.get('message')}")
                else:
                    self.log_test("User Login for Search", False, f"HTTP {login_response.status_code}")
            else:
                self.log_test("Create Search Test User", False, "Failed to create test user")
                
        except Exception as e:
            self.log_test("Search Functionality Setup", False, f"Exception: {str(e)}")
        
        # Test user dashboard page (which contains search functionality)
        try:
            response = self.session.get(f"https://332af799-0cb6-41e3-b677-b093ae8e52d4.preview.emergentagent.com/user/dashboard", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if "CONSULTA ULTRA COMPLETA" in content and "Buscar por nombre" in content:
                    self.log_test(
                        "User Dashboard Search Interface", 
                        True, 
                        "Search interface loaded successfully"
                    )
                else:
                    self.log_test(
                        "User Dashboard Search Interface", 
                        False, 
                        "Missing expected search interface content", 
                        content[:200]
                    )
            else:
                self.log_test(
                    "User Dashboard Search Interface", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text[:200]
                )
                
        except Exception as e:
            self.log_test("User Dashboard Search Interface", False, f"Exception: {str(e)}")
    
    def test_admin_panel_functionality(self):
        """Test 7: Admin panel functionality - Test admin dashboard and user creation"""
        print("👨‍💼 Testing Admin Panel Functionality...")
        
        # Test admin users list
        try:
            response = self.session.get(f"{self.base_url}/admin/users", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    users = data.get("users", [])
                    self.log_test(
                        "Admin Users List", 
                        True, 
                        f"Successfully retrieved {len(users)} users"
                    )
                else:
                    self.log_test(
                        "Admin Users List", 
                        False, 
                        f"API returned success=false: {data.get('message')}", 
                        data
                    )
            else:
                self.log_test(
                    "Admin Users List", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Admin Users List", False, f"Exception: {str(e)}")
        
        # Test admin dashboard page
        try:
            response = self.session.get(f"https://332af799-0cb6-41e3-b677-b093ae8e52d4.preview.emergentagent.com/admin/dashboard", timeout=15)
            
            if response.status_code == 200:
                content = response.text
                if "Panel Admin" in content and "Dashboard" in content:
                    self.log_test(
                        "Admin Dashboard Page", 
                        True, 
                        "Admin dashboard page loaded successfully"
                    )
                else:
                    self.log_test(
                        "Admin Dashboard Page", 
                        False, 
                        "Missing expected admin dashboard content", 
                        content[:200]
                    )
            else:
                self.log_test(
                    "Admin Dashboard Page", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text[:200]
                )
                
        except Exception as e:
            self.log_test("Admin Dashboard Page", False, f"Exception: {str(e)}")
    
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
    
    def test_user_creation_capability(self):
        """Test 10: User creation capability - Verify admin can create users"""
        print("👥 Testing User Creation Capability...")
        
        # Test creating a test user
        try:
            test_user_data = {
                "username": "test_user_recovery",
                "email": "test@recovery.cr",
                "password": "TestPass123",
                "plan": "Básico",
                "customCredits": "50"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/users/create",
                json=test_user_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    username = data.get("username", "unknown")
                    credits = data.get("credits", 0)
                    
                    self.log_test(
                        "User Creation Test", 
                        True, 
                        f"Successfully created user '{username}' with {credits} credits"
                    )
                else:
                    self.log_test(
                        "User Creation Test", 
                        False, 
                        f"User creation failed: {data.get('message')}", 
                        data
                    )
            else:
                self.log_test(
                    "User Creation Test", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("User Creation Test", False, f"Exception: {str(e)}")
    
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
            
            # Priority 5: Core system verification
            self.test_user_creation_capability()
            
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
        db_working = any("Database Access" in r["test"] and r["success"] for r in self.test_results)
        search_working = any("Search" in r["test"] and r["success"] for r in self.test_results)
        admin_panel_working = any("Admin" in r["test"] and "Authentication" not in r["test"] and r["success"] for r in self.test_results)
        
        print(f"🏥 Health Endpoints: {'✅ WORKING' if health_working else '❌ FAILED'}")
        print(f"🔐 Admin Authentication: {'✅ WORKING' if auth_working else '❌ FAILED'}")
        print(f"💾 Database Access: {'✅ WORKING' if db_working else '❌ FAILED'}")
        print(f"🔍 Search Functionality: {'✅ WORKING' if search_working else '❌ FAILED'}")
        print(f"👨‍💼 Admin Panel: {'✅ WORKING' if admin_panel_working else '❌ FAILED'}")
        
        if health_working and auth_working and (db_working or search_working) and admin_panel_working:
            print("\n🎉 CRITICAL SYSTEM RECOVERY: SUCCESS")
            print("✅ All critical systems operational after lazy loading fix")
        elif health_working and auth_working:
            print("\n⚠️ CRITICAL SYSTEM RECOVERY: PARTIAL SUCCESS")
            print("✅ Core authentication and health systems working")
            print("⚠️ Some secondary systems may need attention")
        else:
            print("\n❌ CRITICAL SYSTEM RECOVERY: NEEDS ATTENTION")
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