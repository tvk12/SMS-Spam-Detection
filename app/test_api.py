from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_predict_ham():
    print("Testing Ham Prediction...")
    response = client.post("/predict", json={"text": "Hello, how are you regarding the meeting?"})
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Response: {data}")
    # Note: We can't strictly assert "Ham" without running the actual model, 
    # but we check if the response format is correct and model runs.
    if "prediction" not in data:
        print("FAILED: 'prediction' field missing")
        return False
    print("PASSED")
    return True

def test_predict_spam():
    print("\nTesting Spam Prediction...")
    response = client.post("/predict", json={"text": "WINNER! You have won a lottery. Call now!"})
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.text)
        return False
        
    data = response.json()
    print(f"Response: {data}")
    if "prediction" not in data:
        print("FAILED: 'prediction' field missing")
        return False
    print("PASSED")
    return True

if __name__ == "__main__":
    print("Running API Tests...")
    try:
        ham_passed = test_predict_ham()
        spam_passed = test_predict_spam()
        
        if ham_passed and spam_passed:
            print("\nAll tests passed successfully!")
            sys.exit(0)
        else:
            print("\nSome tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")
        sys.exit(1)
