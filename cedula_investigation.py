#!/usr/bin/env python3
"""
Cedula Investigation Script for Daticos System
This script will help find actual cedulas in the database for testing
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://6916a4c6-b8c5-4b4d-89fd-1f4552be8c9e.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "login": "admin",
    "password": "admin123"
}

class CedulaInvestigator:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self):
        """Authenticate with the API"""
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
    
    def find_cedulas_from_name_search(self):
        """Find actual cedulas by searching for common names"""
        print("\n🔍 Finding actual cedulas from name searches...")
        
        # Search for common names to get actual data
        common_names = ["Maria", "Jose", "Ana", "Carlos"]
        found_cedulas = {"fisica": [], "juridica": []}
        
        for name in common_names:
            try:
                response = self.session.get(
                    f"{self.base_url}/search/name/{name}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    print(f"📝 Found {len(results)} results for name '{name}'")
                    
                    for result in results[:3]:  # Take first 3 results
                        person_type = result.get("type")
                        person_data = result.get("data", {})
                        
                        if person_type == "fisica":
                            cedula = person_data.get("cedula")
                            if cedula and cedula not in found_cedulas["fisica"]:
                                found_cedulas["fisica"].append(cedula)
                                print(f"   📋 Fisica cedula: {cedula} ({person_data.get('nombre', 'N/A')} {person_data.get('primer_apellido', '')})")
                        
                        elif person_type == "juridica":
                            cedula = person_data.get("cedula_juridica")
                            if cedula and cedula not in found_cedulas["juridica"]:
                                found_cedulas["juridica"].append(cedula)
                                print(f"   🏢 Juridica cedula: {cedula} ({person_data.get('nombre_comercial', 'N/A')})")
                
            except Exception as e:
                print(f"❌ Error searching for name '{name}': {str(e)}")
        
        return found_cedulas
    
    def test_cedula_search(self, cedula, expected_type):
        """Test a specific cedula search"""
        try:
            response = self.session.get(
                f"{self.base_url}/search/cedula/{cedula}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("found"):
                    person_type = data.get("type")
                    person_data = data.get("data", {})
                    
                    print(f"✅ Cedula {cedula} found!")
                    print(f"   Type: {person_type}")
                    
                    if person_type == "fisica":
                        print(f"   Name: {person_data.get('nombre', 'N/A')} {person_data.get('primer_apellido', '')} {person_data.get('segundo_apellido', '')}")
                        print(f"   Phone: {person_data.get('telefono', 'N/A')}")
                        print(f"   Email: {person_data.get('email', 'N/A')}")
                    elif person_type == "juridica":
                        print(f"   Commercial Name: {person_data.get('nombre_comercial', 'N/A')}")
                        print(f"   Legal Name: {person_data.get('razon_social', 'N/A')}")
                        print(f"   Sector: {person_data.get('sector_negocio', 'N/A')}")
                        print(f"   Phone: {person_data.get('telefono', 'N/A')}")
                    
                    print(f"   Location: {person_data.get('provincia_nombre', 'N/A')}, {person_data.get('canton_nombre', 'N/A')}, {person_data.get('distrito_nombre', 'N/A')}")
                    
                    return True
                else:
                    print(f"❌ Cedula {cedula} not found: {data.get('message', 'No message')}")
                    return False
            else:
                print(f"❌ Error searching cedula {cedula}: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception searching cedula {cedula}: {str(e)}")
            return False
    
    def verify_database_content(self):
        """Verify database has content"""
        print("\n📊 Verifying database content...")
        
        try:
            # Check demographics
            response = self.session.post(
                f"{self.base_url}/demographics/query",
                json={},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                fisica_count = data.get("total_personas_fisicas", 0)
                juridica_count = data.get("total_personas_juridicas", 0)
                
                print(f"✅ Database contains:")
                print(f"   📋 Personas Físicas: {fisica_count}")
                print(f"   🏢 Personas Jurídicas: {juridica_count}")
                print(f"   📍 Total: {fisica_count + juridica_count}")
                
                return fisica_count > 0 or juridica_count > 0
            else:
                print(f"❌ Error checking demographics: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying database: {str(e)}")
            return False
    
    def run_investigation(self):
        """Run the full investigation"""
        print("🕵️ Starting Cedula Investigation for Daticos System")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Verify database has content
        if not self.verify_database_content():
            print("❌ Database appears to be empty")
            return False
        
        # Find actual cedulas
        found_cedulas = self.find_cedulas_from_name_search()
        
        print("\n🧪 Testing found cedulas...")
        print("=" * 40)
        
        success_count = 0
        total_tests = 0
        
        # Test fisica cedulas
        for cedula in found_cedulas["fisica"][:5]:  # Test first 5
            total_tests += 1
            if self.test_cedula_search(cedula, "fisica"):
                success_count += 1
            print()
        
        # Test juridica cedulas
        for cedula in found_cedulas["juridica"][:5]:  # Test first 5
            total_tests += 1
            if self.test_cedula_search(cedula, "juridica"):
                success_count += 1
            print()
        
        print("=" * 60)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 60)
        print(f"✅ Working cedulas found: {success_count}/{total_tests}")
        
        if success_count > 0:
            print("\n🎯 WORKING CEDULAS FOR TESTING:")
            print("Física cedulas:")
            for cedula in found_cedulas["fisica"][:3]:
                print(f"   - {cedula}")
            
            print("Jurídica cedulas:")
            for cedula in found_cedulas["juridica"][:3]:
                print(f"   - {cedula}")
        
        return success_count > 0

def main():
    """Main execution"""
    investigator = CedulaInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("\n🎉 Investigation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Investigation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()