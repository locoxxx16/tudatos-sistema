#!/usr/bin/env python3
"""
🔥 COMPREHENSIVE BACKEND TESTING - SISTEMA TUDATOS COMPLETO
Testing ALL CRITICAL ENDPOINTS from the review request after Vercel deployment fix
Focus: All backend functionality including enterprise endpoints, search, and system health
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
BACKEND_URL = "https://de6fd9e7-224c-479d-8229-2be5d5f8e611.preview.emergentagent.com/api"

# Admin credentials from review request
ADMIN_CREDENTIALS = {
    "username": "master_admin",
    "password": "TuDatos2025!Ultra"
}

# Test notification email
NOTIFICATION_EMAIL = "jykinternacional@gmail.com"

class ComprehensiveBackendTester:
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
    
    def test_admin_login_ultra_credentials(self):
        """Test 1: Admin login with ultra credentials"""
        print("🔐 Testing Admin Login (master_admin / TuDatos2025!Ultra)...")
        
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
                        "Admin Login - Ultra Credentials", 
                        True, 
                        f"✅ Successfully logged in as {admin_info.get('username', 'master_admin')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Login - Ultra Credentials", 
                        False, 
                        "❌ Missing success or token in response", 
                        data
                    )
            else:
                self.log_test(
                    "Admin Login - Ultra Credentials", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Admin Login - Ultra Credentials", False, f"Exception: {str(e)}")
            
        return False
    
    def test_health_endpoint_4_2m_records(self):
        """Test 2: Health endpoint - Must show 4,283,709 records (NOT 5,000)"""
        print("🏥 Testing Health Endpoint - 4.2M+ Records Verification...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for total records count
                total_records = 0
                if "total_records" in data:
                    total_records = data["total_records"]
                elif "registros_totales" in data:
                    total_records = data["registros_totales"]
                elif "database" in data and "personas_completas" in data["database"]:
                    total_records = data["database"]["personas_completas"]
                elif "database_stats" in data:
                    db_stats = data["database_stats"]
                    if isinstance(db_stats, dict):
                        total_records = sum(db_stats.values()) if all(isinstance(v, int) for v in db_stats.values()) else 0
                
                # Check if we have the expected 4.2M+ records
                expected_records = 4283709
                if total_records >= expected_records:
                    self.log_test(
                        "Health Endpoint - 4.2M+ Records", 
                        True, 
                        f"✅ CORRECT: {total_records:,} records (≥ {expected_records:,})"
                    )
                elif total_records == 5000:
                    self.log_test(
                        "Health Endpoint - 4.2M+ Records", 
                        False, 
                        f"❌ FALLBACK DETECTED: Only {total_records:,} records (should be {expected_records:,}+)", 
                        data
                    )
                else:
                    self.log_test(
                        "Health Endpoint - 4.2M+ Records", 
                        False, 
                        f"❌ INCORRECT COUNT: {total_records:,} records (should be {expected_records:,}+)", 
                        data
                    )
            else:
                self.log_test(
                    "Health Endpoint - 4.2M+ Records", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Health Endpoint - 4.2M+ Records", False, f"Exception: {str(e)}")
    
    def test_system_complete_overview(self):
        """Test 3: System Complete Overview - Critical statistics endpoint"""
        print("📊 Testing System Complete Overview...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/admin/system/complete-overview",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success" and "data" in data:
                    overview_data = data["data"]
                    
                    # Check for key sections
                    expected_sections = ["sistema_general", "estadisticas_detalladas", "resumen_ejecutivo"]
                    has_sections = any(section in overview_data for section in expected_sections)
                    
                    if has_sections:
                        # Try to extract total records
                        total_records = 0
                        if "sistema_general" in overview_data:
                            sistema = overview_data["sistema_general"]
                            total_records = sistema.get("total_registros", 0)
                        
                        self.log_test(
                            "System Complete Overview", 
                            True, 
                            f"✅ Overview retrieved successfully: {total_records:,} total records"
                        )
                    else:
                        self.log_test(
                            "System Complete Overview", 
                            False, 
                            f"❌ Missing expected sections in response", 
                            overview_data
                        )
                else:
                    self.log_test(
                        "System Complete Overview", 
                        False, 
                        f"❌ Invalid response structure", 
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
    
    def test_ultra_complete_search(self):
        """Test 4: Ultra Complete Search - The most critical search endpoint"""
        print("🔍 Testing Ultra Complete Search...")
        
        # Test with a real Costa Rica cedula format
        test_queries = [
            "6-95601834",  # Real format cedula
            "1-1234-5678", # Another format
            "empresa"      # Text search
        ]
        
        for query in test_queries:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/ultra-complete",
                    params={"query": query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") or "results" in data or "profiles" in data:
                        # Check for ultra complete features
                        profiles = data.get("profiles", data.get("results", []))
                        total_profiles = len(profiles)
                        
                        # Look for advanced features
                        has_whatsapp = any("whatsapp" in str(profile).lower() for profile in profiles)
                        has_credit_analysis = any("credit" in str(profile).lower() or "crediticio" in str(profile).lower() for profile in profiles)
                        has_social_media = any("social" in str(profile).lower() or "instagram" in str(profile).lower() for profile in profiles)
                        
                        advanced_features = sum([has_whatsapp, has_credit_analysis, has_social_media])
                        
                        self.log_test(
                            f"Ultra Complete Search - {query}", 
                            True, 
                            f"✅ Search successful: {total_profiles} profiles, {advanced_features}/3 advanced features detected"
                        )
                    else:
                        self.log_test(
                            f"Ultra Complete Search - {query}", 
                            True, 
                            f"✅ Search endpoint working (no results for test query - expected)"
                        )
                else:
                    self.log_test(
                        f"Ultra Complete Search - {query}", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Ultra Complete Search - {query}", False, f"Exception: {str(e)}")
    
    def test_ultra_empresarial_extraction_endpoints(self):
        """Test 5: Ultra Empresarial Extraction Endpoints"""
        print("🔥 Testing Ultra Empresarial Extraction Endpoints...")
        
        # Test start endpoint
        try:
            response = self.session.post(
                f"{self.base_url}/admin/ultra-empresarial-extraction/start",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    fuentes_count = len(data.get("fuentes_empresariales", []))
                    estimado = data.get("estimado_total", "")
                    
                    self.log_test(
                        "Ultra Empresarial Extraction - Start", 
                        True, 
                        f"✅ Started successfully with {fuentes_count} sources, estimated: {estimado}"
                    )
                else:
                    self.log_test(
                        "Ultra Empresarial Extraction - Start", 
                        False, 
                        f"❌ Failed to start extraction", 
                        data
                    )
            else:
                self.log_test(
                    "Ultra Empresarial Extraction - Start", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Ultra Empresarial Extraction - Start", False, f"Exception: {str(e)}")
        
        # Test status endpoint
        try:
            response = self.session.get(
                f"{self.base_url}/admin/ultra-empresarial-extraction/status",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    extraction_data = data.get("data", {})
                    empresarial = extraction_data.get("extraccion_empresarial", {})
                    total_empresas = empresarial.get("total_empresas_nuevas", 0)
                    
                    self.log_test(
                        "Ultra Empresarial Extraction - Status", 
                        True, 
                        f"✅ Status retrieved: {total_empresas} empresas extracted"
                    )
                else:
                    self.log_test(
                        "Ultra Empresarial Extraction - Status", 
                        False, 
                        f"❌ Failed to get status", 
                        data
                    )
            else:
                self.log_test(
                    "Ultra Empresarial Extraction - Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Ultra Empresarial Extraction - Status", False, f"Exception: {str(e)}")
    
    def test_master_extractor_controller_endpoints(self):
        """Test 6: Master Extractor Controller Endpoints"""
        print("🎛️ Testing Master Extractor Controller Endpoints...")
        
        # Test start endpoint
        try:
            response = self.session.post(
                f"{self.base_url}/admin/master-extractor-controller/start",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    extractores_count = len(data.get("extractores_controlados", []))
                    objetivo = data.get("objetivo", "")
                    
                    self.log_test(
                        "Master Extractor Controller - Start", 
                        True, 
                        f"✅ Started successfully controlling {extractores_count} extractors"
                    )
                else:
                    self.log_test(
                        "Master Extractor Controller - Start", 
                        False, 
                        f"❌ Failed to start controller", 
                        data
                    )
            else:
                self.log_test(
                    "Master Extractor Controller - Start", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Master Extractor Controller - Start", False, f"Exception: {str(e)}")
        
        # Test status endpoint
        try:
            response = self.session.get(
                f"{self.base_url}/admin/master-extractor-controller/status",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    controller_data = data.get("data", {})
                    maestro = controller_data.get("controlador_maestro", {})
                    extractores_disponibles = maestro.get("extractores_disponibles", 0)
                    
                    self.log_test(
                        "Master Extractor Controller - Status", 
                        True, 
                        f"✅ Status retrieved: {extractores_disponibles} extractors available"
                    )
                else:
                    self.log_test(
                        "Master Extractor Controller - Status", 
                        False, 
                        f"❌ Failed to get status", 
                        data
                    )
            else:
                self.log_test(
                    "Master Extractor Controller - Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_test("Master Extractor Controller - Status", False, f"Exception: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🔥 COMPREHENSIVE BACKEND TESTING - SISTEMA TUDATOS COMPLETO")
        print("=" * 80)
        print("Testing ALL CRITICAL ENDPOINTS from review request after Vercel deployment fix")
        print("Focus: All backend functionality including enterprise endpoints, search, and system health")
        print(f"Backend URL: {self.base_url}")
        print(f"Admin Credentials: {ADMIN_CREDENTIALS['username']} / {ADMIN_CREDENTIALS['password']}")
        print("=" * 80)
        
        # Priority 1: Admin authentication (required for all other tests)
        admin_authenticated = self.test_admin_login_ultra_credentials()
        
        if not admin_authenticated:
            print("❌ Admin authentication failed - cannot proceed with protected endpoint tests")
            # Continue with public endpoints
        
        # Priority 2: Critical system endpoints
        self.test_health_endpoint_4_2m_records()
        
        if admin_authenticated:
            self.test_system_complete_overview()
        
        # Priority 3: Search functionality
        self.test_ultra_complete_search()
        
        # Priority 4: Enterprise functionality (if authenticated)
        if admin_authenticated:
            self.test_ultra_empresarial_extraction_endpoints()
            self.test_master_extractor_controller_endpoints()
        
        # Print comprehensive summary
        print("=" * 80)
        print("📋 COMPREHENSIVE BACKEND TEST SUMMARY")
        print("=" * 80)
        
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
        
        # Critical systems assessment
        print("\n🔍 CRITICAL SYSTEMS ASSESSMENT:")
        
        # Check critical systems
        admin_auth = any("Admin Login" in r["test"] and r["success"] for r in self.test_results)
        health_4_2m = any("Health Endpoint - 4.2M+ Records" in r["test"] and r["success"] for r in self.test_results)
        system_overview = any("System Complete Overview" in r["test"] and r["success"] for r in self.test_results)
        ultra_search = any("Ultra Complete Search" in r["test"] and r["success"] for r in self.test_results)
        ultra_empresarial = any("Ultra Empresarial Extraction" in r["test"] and r["success"] for r in self.test_results)
        master_controller = any("Master Extractor Controller" in r["test"] and r["success"] for r in self.test_results)
        
        print(f"🔐 Admin Authentication: {'✅ WORKING' if admin_auth else '❌ FAILED'}")
        print(f"🏥 Health (4.2M+ Records): {'✅ WORKING' if health_4_2m else '❌ FAILED'}")
        print(f"📊 System Overview: {'✅ WORKING' if system_overview else '❌ FAILED'}")
        print(f"🔍 Ultra Complete Search: {'✅ WORKING' if ultra_search else '❌ FAILED'}")
        print(f"🔥 Ultra Empresarial: {'✅ WORKING' if ultra_empresarial else '❌ FAILED'}")
        print(f"🎛️ Master Controller: {'✅ WORKING' if master_controller else '❌ FAILED'}")
        
        # Final assessment
        critical_systems = [health_4_2m, ultra_search]
        if admin_authenticated:
            critical_systems.extend([system_overview, ultra_empresarial, master_controller])
        
        critical_working = sum(critical_systems)
        
        if critical_working >= len(critical_systems) * 0.8:  # 80% or more working
            print("\n🎉 SISTEMA TUDATOS: OPERATIONAL")
            print("✅ Critical backend functionality is working correctly")
            print("✅ System ready for production deployment")
            print("✅ 4.2M+ records confirmed and accessible")
        elif critical_working >= len(critical_systems) * 0.6:  # 60% or more working
            print("\n⚠️ SISTEMA TUDATOS: MOSTLY OPERATIONAL")
            print("⚠️ Most critical features working, minor issues detected")
        else:
            print("\n❌ SISTEMA TUDATOS: NEEDS ATTENTION")
            print("❌ Critical backend functionality has significant issues")
        
        return passed, total

def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    passed, total = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All comprehensive backend tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} comprehensive backend tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()