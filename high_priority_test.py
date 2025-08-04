#!/usr/bin/env python3
"""
HIGH PRIORITY ENDPOINT TESTING - TuDatos System
Tests the 4 specific endpoints requested by user
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://89e24cda-edb1-49a8-aa6d-fa1a1226147e.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "login": "admin",
    "password": "admin123"
}

class HighPriorityTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.results = []
        
    def log_result(self, test_name, success, details="", data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    print("✅ Authentication successful")
                    return True
                    
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            
        return False
    
    def test_high_priority_endpoints(self):
        """Test the 4 HIGH PRIORITY endpoints"""
        print("🔥 TESTING HIGH PRIORITY ENDPOINTS - TuDatos System")
        print("=" * 60)
        
        # Test 1: GET /api/admin/system/complete-overview
        print("1️⃣ Testing System Complete Overview...")
        try:
            response = self.session.get(
                f"{self.base_url}/admin/system/complete-overview", 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "overview" in data:
                    overview = data["overview"]
                    resumen = overview.get("resumen", {})
                    total_records = resumen.get("gran_total", 0)
                    progreso_3M = resumen.get("progreso_3M", "0%")
                    objetivo_alcanzado = resumen.get("objetivo_3M_alcanzado", False)
                    
                    # Check for new collections
                    mega_extraction = overview.get("mega_extraction", {})
                    personas_fisicas_mega = mega_extraction.get("personas_fisicas_mega", 0)
                    profesionales_cr = mega_extraction.get("profesionales_cr", 0)
                    
                    self.log_result(
                        "System Complete Overview", 
                        True, 
                        f"Total: {total_records:,} records, Progress: {progreso_3M}, 3M Goal: {objetivo_alcanzado}, Mega Fisicas: {personas_fisicas_mega}, Profesionales: {profesionales_cr}",
                        overview
                    )
                else:
                    self.log_result(
                        "System Complete Overview", 
                        False, 
                        "Missing overview in response", 
                        data
                    )
            else:
                self.log_result(
                    "System Complete Overview", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_result("System Complete Overview", False, f"Exception: {str(e)}")
        
        # Test 2: GET /api/admin/mega-extraction/status
        print("2️⃣ Testing Mega Extraction Status...")
        try:
            response = self.session.get(
                f"{self.base_url}/admin/mega-extraction/status", 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    mega_data = data["data"]
                    mega_especifica = mega_data.get("mega_extraction_especifica", {})
                    personas_fisicas_mega = mega_especifica.get("personas_fisicas_mega", 0)
                    personas_juridicas_mega = mega_especifica.get("personas_juridicas_mega", 0)
                    profesionales_cr = mega_especifica.get("profesionales_cr", 0)
                    total_mega = mega_especifica.get("total_mega_extraction", 0)
                    
                    totales = mega_data.get("totales_combinados", {})
                    grand_total = totales.get("gran_total", 0)
                    progreso_3M = totales.get("progreso_hacia_3M", "0%")
                    objetivo_alcanzado = totales.get("objetivo_3M_alcanzado", False)
                    
                    self.log_result(
                        "Mega Extraction Status", 
                        True, 
                        f"Mega Total: {total_mega:,}, Grand Total: {grand_total:,}, Progress: {progreso_3M}, Goal: {objetivo_alcanzado}",
                        mega_data
                    )
                else:
                    self.log_result(
                        "Mega Extraction Status", 
                        False, 
                        "Missing data in response", 
                        data
                    )
            else:
                self.log_result(
                    "Mega Extraction Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_result("Mega Extraction Status", False, f"Exception: {str(e)}")
        
        # Test 3: POST /api/admin/mega-extraction/start (only if not running)
        print("3️⃣ Testing Mega Extraction Start...")
        try:
            response = self.session.post(
                f"{self.base_url}/admin/mega-extraction/start", 
                json={},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "message" in data:
                    details_info = data.get("details", {})
                    fuentes = details_info.get("fuentes", [])
                    estimado = details_info.get("estimado_registros", "Unknown")
                    
                    self.log_result(
                        "Mega Extraction Start", 
                        True, 
                        f"Started successfully. Sources: {len(fuentes)}, Estimated: {estimado}",
                        data
                    )
                else:
                    self.log_result(
                        "Mega Extraction Start", 
                        False, 
                        "Missing success status or message", 
                        data
                    )
            else:
                self.log_result(
                    "Mega Extraction Start", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_result("Mega Extraction Start", False, f"Exception: {str(e)}")
        
        # Test 4: GET /api/admin/ultra-deep-extraction/status
        print("4️⃣ Testing Ultra Deep Extraction Status...")
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
                    personas_fisicas = registros_actuales.get("personas_fisicas", 0)
                    personas_juridicas = registros_actuales.get("personas_juridicas", 0)
                    
                    objetivo_3M = ultra_data.get("objetivo_3M", {})
                    progreso = objetivo_3M.get("progreso_porcentaje", 0)
                    alcanzado = objetivo_3M.get("alcanzado", False)
                    faltantes = objetivo_3M.get("registros_faltantes", 0)
                    
                    self.log_result(
                        "Ultra Deep Extraction Status", 
                        True, 
                        f"Total: {total_principal:,} (Físicas: {personas_fisicas:,}, Jurídicas: {personas_juridicas:,}), Progress: {progreso:.2f}%, Goal: {alcanzado}, Missing: {faltantes:,}",
                        ultra_data
                    )
                else:
                    self.log_result(
                        "Ultra Deep Extraction Status", 
                        False, 
                        "Missing data in response", 
                        data
                    )
            else:
                self.log_result(
                    "Ultra Deep Extraction Status", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                
        except Exception as e:
            self.log_result("Ultra Deep Extraction Status", False, f"Exception: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📋 HIGH PRIORITY ENDPOINTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results if result["success"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📝 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = HighPriorityTester()
    
    if tester.authenticate():
        tester.test_high_priority_endpoints()
        passed, total = tester.print_summary()
        
        if passed == total:
            print("\n🎉 All high priority endpoints working!")
        else:
            print(f"\n⚠️  {total - passed} endpoints have issues")
    else:
        print("❌ Authentication failed - cannot test endpoints")

if __name__ == "__main__":
    main()