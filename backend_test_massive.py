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
BACKEND_URL = "https://37735176-6152-46aa-8c58-184988c5ed57.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "login": "admin",
    "password": "admin123"
}

# MongoDB connection for direct database testing
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class MassiveDataExtractionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
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
    
    def connect_mongodb(self):
        """Connect to MongoDB for direct database testing"""
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            # Test connection
            self.db.admin.command('ping')
            self.log_test("MongoDB Connection", True, f"Connected to {DB_NAME}")
            return True
        except Exception as e:
            self.log_test("MongoDB Connection", False, f"Failed to connect: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with admin credentials"""
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
    
    def test_mongodb_collections_verification(self):
        """Test 1: Verify MongoDB collections are populated correctly"""
        print("🗄️ Testing MongoDB Collections Verification...")
        
        if not self.mongo_client:
            self.log_test("MongoDB Collections", False, "MongoDB not connected")
            return
        
        # Test required collections
        required_collections = [
            'tse_datos_hibridos',
            'daticos_datos_masivos', 
            'datos_mercantiles_enhanced',
            'extraction_final_statistics'
        ]
        
        for collection_name in required_collections:
            try:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                
                if collection_name == 'tse_datos_hibridos':
                    # Should have 100K+ records
                    if count >= 100000:
                        self.log_test(
                            f"Collection {collection_name}", 
                            True, 
                            f"Has {count:,} records (target: 100K+)"
                        )
                    else:
                        self.log_test(
                            f"Collection {collection_name}", 
                            False, 
                            f"Only {count:,} records, expected 100K+"
                        )
                elif collection_name == 'daticos_datos_masivos':
                    # Should contain Daticos data with Saraya/12345
                    sample_doc = collection.find_one({"credencial_usada": "Saraya/12345"})
                    if sample_doc:
                        self.log_test(
                            f"Collection {collection_name}", 
                            True, 
                            f"Has {count:,} records with Saraya/12345 credentials"
                        )
                    else:
                        self.log_test(
                            f"Collection {collection_name}", 
                            False, 
                            f"No records found with Saraya/12345 credentials"
                        )
                elif collection_name == 'datos_mercantiles_enhanced':
                    # Should contain enhanced mercantile data
                    if count > 0:
                        self.log_test(
                            f"Collection {collection_name}", 
                            True, 
                            f"Has {count:,} enhanced mercantile records"
                        )
                    else:
                        self.log_test(
                            f"Collection {collection_name}", 
                            False, 
                            "No enhanced mercantile records found"
                        )
                elif collection_name == 'extraction_final_statistics':
                    # Should contain extraction statistics
                    if count > 0:
                        latest_stats = collection.find().sort("extraction_date", -1).limit(1)
                        stats_doc = list(latest_stats)[0] if latest_stats else None
                        if stats_doc:
                            total_records = stats_doc.get('total_unique_records', 0)
                            self.log_test(
                                f"Collection {collection_name}", 
                                True, 
                                f"Latest extraction: {total_records:,} unique records"
                            )
                        else:
                            self.log_test(
                                f"Collection {collection_name}", 
                                True, 
                                f"Has {count} statistics records"
                            )
                    else:
                        self.log_test(
                            f"Collection {collection_name}", 
                            False, 
                            "No extraction statistics found"
                        )
                        
            except Exception as e:
                self.log_test(f"Collection {collection_name}", False, f"Error: {str(e)}")
    
    def test_data_quality_verification(self):
        """Test 2: Verify data quality - Costa Rican phone numbers, cedulas, names"""
        print("🔍 Testing Data Quality Verification...")
        
        if not self.mongo_client:
            self.log_test("Data Quality", False, "MongoDB not connected")
            return
        
        # Test Costa Rican phone number formats
        try:
            # Sample from TSE data
            tse_sample = list(self.db.tse_datos_hibridos.find().limit(100))
            valid_phones = 0
            total_phones = 0
            
            cr_phone_pattern = re.compile(r'\+506[\s-]?([678]\d{7}|2\d{3}[\s-]?\d{4})')
            
            for record in tse_sample:
                phones = record.get('telefonos_encontrados', [])
                if isinstance(phones, list):
                    for phone in phones:
                        total_phones += 1
                        if cr_phone_pattern.match(str(phone)):
                            valid_phones += 1
                elif record.get('telefono_principal'):
                    total_phones += 1
                    if cr_phone_pattern.match(str(record['telefono_principal'])):
                        valid_phones += 1
            
            if total_phones > 0:
                phone_quality = (valid_phones / total_phones) * 100
                self.log_test(
                    "Costa Rican Phone Format Quality", 
                    phone_quality >= 80, 
                    f"{phone_quality:.1f}% valid CR phone formats ({valid_phones}/{total_phones})"
                )
            else:
                self.log_test("Costa Rican Phone Format Quality", False, "No phone numbers found in sample")
                
        except Exception as e:
            self.log_test("Phone Format Quality", False, f"Error: {str(e)}")
        
        # Test cedula formats (X-XXXX-XXXX)
        try:
            cedula_sample = list(self.db.tse_datos_hibridos.find().limit(100))
            valid_cedulas = 0
            total_cedulas = 0
            
            cedula_pattern = re.compile(r'^[1-9]-?\d{4}-?\d{4}$')
            
            for record in cedula_sample:
                cedula = record.get('cedula')
                if cedula:
                    total_cedulas += 1
                    if cedula_pattern.match(str(cedula)):
                        valid_cedulas += 1
            
            if total_cedulas > 0:
                cedula_quality = (valid_cedulas / total_cedulas) * 100
                self.log_test(
                    "Costa Rican Cedula Format Quality", 
                    cedula_quality >= 90, 
                    f"{cedula_quality:.1f}% valid cedula formats ({valid_cedulas}/{total_cedulas})"
                )
            else:
                self.log_test("Cedula Format Quality", False, "No cedulas found in sample")
                
        except Exception as e:
            self.log_test("Cedula Format Quality", False, f"Error: {str(e)}")
        
        # Test Costa Rican provinces
        try:
            province_sample = list(self.db.tse_datos_hibridos.find().limit(100))
            cr_provinces = {
                "San José", "Alajuela", "Cartago", "Heredia", 
                "Guanacaste", "Puntarenas", "Limón"
            }
            valid_provinces = 0
            total_provinces = 0
            
            for record in province_sample:
                provincia = record.get('provincia')
                if provincia:
                    total_provinces += 1
                    if provincia in cr_provinces:
                        valid_provinces += 1
            
            if total_provinces > 0:
                province_quality = (valid_provinces / total_provinces) * 100
                self.log_test(
                    "Costa Rican Province Quality", 
                    province_quality >= 80, 
                    f"{province_quality:.1f}% valid CR provinces ({valid_provinces}/{total_provinces})"
                )
            else:
                self.log_test("Province Quality", False, "No provinces found in sample")
                
        except Exception as e:
            self.log_test("Province Quality", False, f"Error: {str(e)}")
    
    def test_backend_api_massive_data(self):
        """Test 3: Backend API endpoints can handle massive data"""
        print("🌐 Testing Backend API with Massive Data...")
        
        # Test system health
        try:
            response = self.session.get(f"{self.base_url}/system/health", timeout=15)
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get('services', {}).get('database', 'unknown')
                self.log_test(
                    "System Health Check", 
                    db_status == 'healthy', 
                    f"Database status: {db_status}"
                )
            else:
                self.log_test("System Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
        
        # Test admin statistics endpoint
        try:
            response = self.session.get(f"{self.base_url}/admin/update-stats", timeout=15)
            if response.status_code == 200:
                stats_data = response.json()
                system_stats = stats_data.get('system_stats', {})
                total_fisica = system_stats.get('total_personas_fisicas', 0)
                total_juridica = system_stats.get('total_personas_juridicas', 0)
                
                self.log_test(
                    "Admin Statistics Endpoint", 
                    True, 
                    f"Fisica: {total_fisica:,}, Juridica: {total_juridica:,}"
                )
            else:
                self.log_test("Admin Statistics Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Admin Statistics Endpoint", False, f"Exception: {str(e)}")
        
        # Test search functionality with large dataset
        try:
            # Test name search that should return many results
            response = self.session.get(f"{self.base_url}/search/name/Maria", timeout=15)
            if response.status_code == 200:
                search_data = response.json()
                results = search_data.get('results', [])
                total = search_data.get('total', 0)
                
                self.log_test(
                    "Large Dataset Search", 
                    total > 0, 
                    f"Found {total} results for 'Maria' search"
                )
            else:
                self.log_test("Large Dataset Search", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Large Dataset Search", False, f"Exception: {str(e)}")
    
    def test_daticos_integration(self):
        """Test 4: Daticos integration with Saraya/12345 credentials"""
        print("🏛️ Testing Daticos Integration...")
        
        # Test Daticos connection
        try:
            response = self.session.get(f"{self.base_url}/admin/daticos/test-connection", timeout=20)
            if response.status_code == 200:
                connection_data = response.json()
                connection_status = connection_data.get('connection_status')
                credentials_valid = connection_data.get('credentials_valid', False)
                
                self.log_test(
                    "Daticos Connection Test", 
                    connection_status == 'success' and credentials_valid, 
                    f"Status: {connection_status}, Credentials: {'Valid' if credentials_valid else 'Invalid'}"
                )
            else:
                self.log_test("Daticos Connection Test", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Daticos Connection Test", False, f"Exception: {str(e)}")
        
        # Test data integration summary
        try:
            response = self.session.get(f"{self.base_url}/admin/data-integration/summary", timeout=15)
            if response.status_code == 200:
                integration_data = response.json()
                summary = integration_data.get('integration_summary', {})
                total_personas = summary.get('total_personas', 0)
                total_empresas = summary.get('total_empresas', 0)
                
                self.log_test(
                    "Daticos Integration Summary", 
                    total_personas > 0 or total_empresas > 0, 
                    f"Personas: {total_personas:,}, Empresas: {total_empresas:,}"
                )
            else:
                self.log_test("Daticos Integration Summary", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Daticos Integration Summary", False, f"Exception: {str(e)}")
    
    def test_extraction_statistics(self):
        """Test 5: Extraction statistics are being saved properly"""
        print("📊 Testing Extraction Statistics...")
        
        if not self.mongo_client:
            self.log_test("Extraction Statistics", False, "MongoDB not connected")
            return
        
        try:
            # Check extraction_final_statistics collection
            stats_collection = self.db.extraction_final_statistics
            latest_stats = list(stats_collection.find().sort("extraction_date", -1).limit(1))
            
            if latest_stats:
                stats_doc = latest_stats[0]
                total_records = stats_doc.get('total_unique_records', 0)
                target_achieved = stats_doc.get('target_achieved', False)
                sources = stats_doc.get('sources', {})
                
                tse_records = sources.get('tse_reales', 0)
                daticos_records = sources.get('daticos_saraya', 0)
                mercantile_records = sources.get('mercantiles_enhanced', 0)
                
                self.log_test(
                    "Extraction Statistics Saved", 
                    True, 
                    f"Total: {total_records:,}, Target achieved: {target_achieved}"
                )
                
                self.log_test(
                    "Source Breakdown", 
                    True, 
                    f"TSE: {tse_records:,}, Daticos: {daticos_records:,}, Mercantile: {mercantile_records:,}"
                )
                
                # Check phone statistics
                phone_stats = stats_doc.get('phone_stats', {})
                total_phones = phone_stats.get('total_phones_found', 0)
                mobile_phones = phone_stats.get('mobile_phones', 0)
                
                self.log_test(
                    "Phone Number Statistics", 
                    total_phones > 0, 
                    f"Total phones: {total_phones:,}, Mobile: {mobile_phones:,}"
                )
                
            else:
                self.log_test("Extraction Statistics Saved", False, "No extraction statistics found")
                
        except Exception as e:
            self.log_test("Extraction Statistics", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all massive data extraction tests"""
        print("🚀 Starting Massive Costa Rican Data Extraction Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"MongoDB URL: {MONGO_URL}")
        print("=" * 80)
        
        # Connect to MongoDB first
        mongo_connected = self.connect_mongodb()
        
        # Test authentication
        auth_success = self.test_authentication()
        
        if auth_success:
            # Run all tests
            self.test_mongodb_collections_verification()
            self.test_data_quality_verification()
            self.test_backend_api_massive_data()
            self.test_daticos_integration()
            self.test_extraction_statistics()
        else:
            print("❌ Authentication failed - skipping authenticated tests")
        
        # Print summary
        print("=" * 80)
        print("📋 MASSIVE DATA EXTRACTION TEST SUMMARY")
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
        
        # Close MongoDB connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return passed, total

def main():
    """Main test execution"""
    tester = MassiveDataExtractionTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All massive data extraction tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()