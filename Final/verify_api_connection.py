import requests
import sys

try:
    print("Testing http://127.0.0.1:5000/api/health...")
    r = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
    print(f"127.0.0.1 Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"127.0.0.1 Failed: {e}")

try:
    print("\nTesting http://localhost:5000/api/health...")
    r = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"localhost Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"localhost Failed: {e}")
