#!/usr/bin/env python3
"""
Comprehensive Cedula Search Endpoint Test
Specifically tests /api/search/cedula/{cedula} endpoint as requested
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fa24ba8a-848e-48cd-bba5-592950660fa8.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "login": "admin",
    "password": "admin123"
}

# Working cedulas found in the database
WORKING_FISICA_CEDULAS = [
    "692785539",  # Marianela Chacón
    "410197954",  # Marianela Pagès Lucas
    "903153808",  # Mariana Valera
    "945985846",  # Jose Manuel Montenegro Cabezas
    "255043829"   # Jose Miguel Busquets
]

WORKING_JURIDICA_CEDULAS = [
    "3-101-629135",  # Banca Privada LX S.Com.
    "3-101-587436",  # Uría y Marquez S.C.P
    "3-101-371162",  # Desarrollo Mur S.L.
    "3-101-296456",  # Finanzas Castellana S.L.N.E
    "3-101-188515"   # Inversiones Ibérica S.Coop.
]

class CedulaEndpointTester:
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
    
    def authenticate(self):
        """Authenticate with the API"""
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
            
            print(f"❌ Authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def verify_database_content(self):
        """Verify database has content"""
        print("📊 Verifying database content...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/demographics/query",
                json={},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                fisica_count = data.get("total_personas_fisicas", 0)
                juridica_count = data.get("total_personas_juridicas", 0)
                
                self.log_test(
                    "Database Content Verification",
                    True,
                    f"Física: {fisica_count}, Jurídica: {juridica_count}, Total: {fisica_count + juridica_count}"
                )
                
                return fisica_count > 0 or juridica_count > 0
            else:
                self.log_test(
                    "Database Content Verification",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Database Content Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_cedula_search_fisica(self):
        """Test cedula search for personas fisicas"""
        print("👤 Testing Cedula Search - Personas Físicas...")
        
        for cedula in WORKING_FISICA_CEDULAS:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/cedula/{cedula}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("found") and data.get("type") == "fisica":
                        person_data = data.get("data", {})
                        
                        # Verify required fields are present
                        required_fields = ["cedula", "nombre", "primer_apellido"]
                        missing_fields = [field for field in required_fields if not person_data.get(field)]
                        
                        if not missing_fields:
                            name = f"{person_data.get('nombre')} {person_data.get('primer_apellido')} {person_data.get('segundo_apellido', '')}"
                            location = f"{person_data.get('provincia_nombre', 'N/A')}, {person_data.get('canton_nombre', 'N/A')}, {person_data.get('distrito_nombre', 'N/A')}"
                            
                            self.log_test(
                                f"Cedula Search Física {cedula}",
                                True,
                                f"Found: {name.strip()}, Location: {location}, Phone: {person_data.get('telefono', 'N/A')}"
                            )
                        else:
                            self.log_test(
                                f"Cedula Search Física {cedula}",
                                False,
                                f"Missing required fields: {missing_fields}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Cedula Search Física {cedula}",
                            False,
                            f"Not found or wrong type. Found: {data.get('found')}, Type: {data.get('type')}",
                            data
                        )
                else:
                    self.log_test(
                        f"Cedula Search Física {cedula}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Cedula Search Física {cedula}", False, f"Exception: {str(e)}")
    
    def test_cedula_search_juridica(self):
        """Test cedula search for personas juridicas"""
        print("🏢 Testing Cedula Search - Personas Jurídicas...")
        
        for cedula in WORKING_JURIDICA_CEDULAS:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/cedula/{cedula}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("found") and data.get("type") == "juridica":
                        person_data = data.get("data", {})
                        
                        # Verify required fields are present
                        required_fields = ["cedula_juridica", "nombre_comercial", "razon_social"]
                        missing_fields = [field for field in required_fields if not person_data.get(field)]
                        
                        if not missing_fields:
                            commercial_name = person_data.get('nombre_comercial', 'N/A')
                            sector = person_data.get('sector_negocio', 'N/A')
                            location = f"{person_data.get('provincia_nombre', 'N/A')}, {person_data.get('canton_nombre', 'N/A')}, {person_data.get('distrito_nombre', 'N/A')}"
                            
                            self.log_test(
                                f"Cedula Search Jurídica {cedula}",
                                True,
                                f"Found: {commercial_name}, Sector: {sector}, Location: {location}, Phone: {person_data.get('telefono', 'N/A')}"
                            )
                        else:
                            self.log_test(
                                f"Cedula Search Jurídica {cedula}",
                                False,
                                f"Missing required fields: {missing_fields}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Cedula Search Jurídica {cedula}",
                            False,
                            f"Not found or wrong type. Found: {data.get('found')}, Type: {data.get('type')}",
                            data
                        )
                else:
                    self.log_test(
                        f"Cedula Search Jurídica {cedula}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Cedula Search Jurídica {cedula}", False, f"Exception: {str(e)}")
    
    def test_cedula_not_found(self):
        """Test cedula search for non-existent cedulas"""
        print("❌ Testing Cedula Search - Non-existent Cedulas...")
        
        non_existent_cedulas = [
            "000000000",
            "999999999", 
            "3-101-000000",
            "invalid-cedula"
        ]
        
        for cedula in non_existent_cedulas:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/cedula/{cedula}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if not data.get("found"):
                        self.log_test(
                            f"Cedula Not Found {cedula}",
                            True,
                            f"Correctly returned not found: {data.get('message', 'No message')}"
                        )
                    else:
                        self.log_test(
                            f"Cedula Not Found {cedula}",
                            False,
                            f"Unexpectedly found data for non-existent cedula",
                            data
                        )
                else:
                    self.log_test(
                        f"Cedula Not Found {cedula}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Cedula Not Found {cedula}", False, f"Exception: {str(e)}")
    
    def test_response_format(self):
        """Test response format consistency"""
        print("📋 Testing Response Format...")
        
        # Test with a known working cedula
        test_cedula = WORKING_FISICA_CEDULAS[0]
        
        try:
            response = self.session.get(
                f"{self.base_url}/search/cedula/{test_cedula}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response structure
                required_keys = ["found", "type", "data"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    # Check data structure for fisica
                    person_data = data.get("data", {})
                    expected_data_keys = ["id", "cedula", "nombre", "primer_apellido", "provincia_nombre", "canton_nombre", "distrito_nombre"]
                    missing_data_keys = [key for key in expected_data_keys if key not in person_data]
                    
                    if not missing_data_keys:
                        self.log_test(
                            "Response Format Validation",
                            True,
                            "All required fields present in response"
                        )
                    else:
                        self.log_test(
                            "Response Format Validation",
                            False,
                            f"Missing data fields: {missing_data_keys}",
                            data
                        )
                else:
                    self.log_test(
                        "Response Format Validation",
                        False,
                        f"Missing response keys: {missing_keys}",
                        data
                    )
            else:
                self.log_test(
                    "Response Format Validation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Response Format Validation", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive cedula endpoint test"""
        print("🔍 Starting Comprehensive Cedula Search Endpoint Test")
        print(f"Backend URL: {self.base_url}")
        print("=" * 70)
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Verify database content
        if not self.verify_database_content():
            return False
        
        # Run all tests
        self.test_response_format()
        self.test_cedula_search_fisica()
        self.test_cedula_search_juridica()
        self.test_cedula_not_found()
        
        # Print summary
        print("=" * 70)
        print("📋 CEDULA ENDPOINT TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show working cedulas for user reference
        print("\n🎯 WORKING CEDULAS FOR TESTING:")
        print("=" * 40)
        print("📋 Personas Físicas:")
        for cedula in WORKING_FISICA_CEDULAS:
            print(f"   - {cedula}")
        
        print("\n🏢 Personas Jurídicas:")
        for cedula in WORKING_JURIDICA_CEDULAS:
            print(f"   - {cedula}")
        
        print("\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return passed == total

def main():
    """Main test execution"""
    tester = CedulaEndpointTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All cedula endpoint tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()