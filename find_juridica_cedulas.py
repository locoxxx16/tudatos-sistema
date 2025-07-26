#!/usr/bin/env python3
"""
Find Juridica Cedulas Script
"""

import requests
import json

# Configuration
BACKEND_URL = "https://815deec3-a5c7-4c40-b840-156d8abd979e.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "login": "admin",
    "password": "admin123"
}

def authenticate():
    """Authenticate with the API"""
    session = requests.Session()
    try:
        response = session.post(
            f"{BACKEND_URL}/auth/login",
            json=TEST_CREDENTIALS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                auth_token = data["access_token"]
                session.headers.update({
                    "Authorization": f"Bearer {auth_token}"
                })
                print("✅ Authentication successful")
                return session
        
        print(f"❌ Authentication failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def find_juridica_cedulas(session):
    """Find juridica cedulas by searching for business terms"""
    print("\n🏢 Finding juridica cedulas...")
    
    # Search for business-related terms
    business_terms = ["Empresa", "Sociedad", "S.A.", "Ltda", "Corp", "Company", "Comercial"]
    found_cedulas = []
    
    for term in business_terms:
        try:
            response = session.get(
                f"{BACKEND_URL}/search/name/{term}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                print(f"📝 Found {len(results)} results for term '{term}'")
                
                for result in results[:3]:  # Take first 3 results
                    person_type = result.get("type")
                    person_data = result.get("data", {})
                    
                    if person_type == "juridica":
                        cedula = person_data.get("cedula_juridica")
                        if cedula and cedula not in found_cedulas:
                            found_cedulas.append(cedula)
                            print(f"   🏢 Juridica cedula: {cedula} ({person_data.get('nombre_comercial', 'N/A')})")
            
        except Exception as e:
            print(f"❌ Error searching for term '{term}': {str(e)}")
    
    return found_cedulas

def test_juridica_cedulas(session, cedulas):
    """Test juridica cedulas"""
    print("\n🧪 Testing juridica cedulas...")
    
    for cedula in cedulas[:5]:  # Test first 5
        try:
            response = session.get(
                f"{BACKEND_URL}/search/cedula/{cedula}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("found"):
                    person_data = data.get("data", {})
                    print(f"✅ Cedula {cedula} found!")
                    print(f"   Commercial Name: {person_data.get('nombre_comercial', 'N/A')}")
                    print(f"   Legal Name: {person_data.get('razon_social', 'N/A')}")
                    print(f"   Sector: {person_data.get('sector_negocio', 'N/A')}")
                    print(f"   Phone: {person_data.get('telefono', 'N/A')}")
                    print(f"   Location: {person_data.get('provincia_nombre', 'N/A')}")
                    print()
                else:
                    print(f"❌ Cedula {cedula} not found")
            else:
                print(f"❌ Error searching cedula {cedula}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception searching cedula {cedula}: {str(e)}")

def main():
    session = authenticate()
    if not session:
        return
    
    juridica_cedulas = find_juridica_cedulas(session)
    
    if juridica_cedulas:
        print(f"\n🎯 Found {len(juridica_cedulas)} juridica cedulas:")
        for cedula in juridica_cedulas:
            print(f"   - {cedula}")
        
        test_juridica_cedulas(session, juridica_cedulas)
    else:
        print("❌ No juridica cedulas found")

if __name__ == "__main__":
    main()