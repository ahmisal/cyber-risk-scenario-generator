
import requests
import os
import sys

# Backend URL
API_URL = "http://localhost:8000/api/v1/analyze"
TEST_FILE = "tests/sample_context.txt"

def test_backend():
    print("Testing Backend API directly (Bypassing Gradio)...")
    
    if not os.path.exists(TEST_FILE):
        print(f"Error: Test file {TEST_FILE} not found.")
        return

    print(f"Uploading {TEST_FILE} to {API_URL}...")
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (os.path.basename(TEST_FILE), f, 'text/plain')}
            data = {'asset_name': 'Acme Production Endpoint'}
            
            # Send request
            response = requests.post(API_URL, files=files, data=data, timeout=600)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("\n✅ SUCCESS! Report Generated:\n")
                print("="*60)
                # Handle both 'report' (new) and 'analysis' (old) keys just in case
                report = result.get("report") or result.get("analysis")
                print(report)
                print("="*60)
            else:
                print(f"❌ Failed: {result.get('error')}")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Ensure the backend server is running: .\\venv-backend\\Scripts\\uvicorn.exe app.main:app --port 8000")

if __name__ == "__main__":
    test_backend()
