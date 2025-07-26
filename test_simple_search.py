#!/usr/bin/env python3
"""
Simple test to verify search endpoints work with actual data
"""

import requests
import json

BACKEND_URL = "https://1aac54d4-eee0-4add-99c9-f5d440a69076.preview.emergentagent.com/api"

# Login first
login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
    "login": "admin",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test search by name with actual name from database
    print("Testing search by name 'Jacinto'...")
    response = requests.get(f"{BACKEND_URL}/search/name/Jacinto", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"Results: {data.get('total', 0)}")
        
    # Test search by cedula with actual cedula
    print("\nTesting search by cedula '588344543'...")
    response = requests.get(f"{BACKEND_URL}/search/cedula/588344543", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"Found: {data.get('found', False)}")
        
else:
    print("Login failed")