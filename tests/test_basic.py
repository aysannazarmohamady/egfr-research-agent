# debug_test.py - Test AI connection
import os
from dotenv import load_dotenv
import requests

def test_gemini_api():
    """Test if Gemini API is working"""
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    print(f" API Key found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print(" No API key - using Simple Mode")
        return False
    
    print(f" API Key: {api_key[:10]}...")
    
    # Test API call
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Extract medical keywords from: renal toxicity of targeted cancer therapy. Return only comma-separated keywords."
                    }
                ]
            }
        ]
    }
    
    try:
        print(" Testing API connection...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result:
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                print(f" AI Response: {ai_response}")
                return True
            else:
                print(f" Unexpected response format: {result}")
                return False
        else:
            print(f" API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f" Connection Error: {e}")
        return False

if __name__ == "__main__":
    print(" Testing EGFR Research Agent - AI Connection")
    print("=" * 50)
    
    is_working = test_gemini_api()
    
    print("=" * 50)
    print(f"🎯 Result: {'AI Mode Ready! 🤖' if is_working else 'Simple Mode Only 📝'}")
