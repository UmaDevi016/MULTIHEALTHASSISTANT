
import sys
import os
from fastapi.testclient import TestClient

# Add current directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("Successfully imported app")
except ImportError as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

client = TestClient(app)

def test_health():
    response = client.get("/health")
    if response.status_code == 200:
        print("Health check passed")
        print(response.json())
    else:
        print(f"Health check failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

if __name__ == "__main__":
    test_health()
