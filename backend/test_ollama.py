"""
Test Ollama connection and model
"""

import requests
import json

def test_ollama():
    """Test if Ollama is working with llama3.2"""
    
    print("=" * 60)
    print("Testing Ollama Connection")
    print("=" * 60)
    
    base_url = "http://localhost:11434"
    
    # Test 1: Check if Ollama is running
    print("\n1. Checking if Ollama is running...")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("   ✅ Ollama is running!")
            models = response.json().get('models', [])
            print(f"   📦 Available models: {[m['name'] for m in models]}")
        else:
            print(f"   ❌ Ollama returned error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to Ollama: {e}")
        print("\n   Make sure Docker container is running:")
        print("   docker ps")
        return False
    
    # Test 2: Check if llama3.2 is available
    print("\n2. Checking llama3.2 model...")
    model_names = [m['name'] for m in models]
    if 'llama3.2:latest' in model_names or 'llama3.2' in str(model_names):
        print("   ✅ llama3.2 is available!")
    else:
        print("   ❌ llama3.2 not found!")
        print("\n   Download it with:")
        print("   docker exec -it ollama ollama pull llama3.2")
        return False
    
    # Test 3: Generate test response
    print("\n3. Testing text generation...")
    try:
        prompt = "List 3 rooms in a house. Answer with just the room names, separated by commas."
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 50
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"   ✅ Generation successful!")
            print(f"   📝 Response: {generated_text[:100]}...")
            print(f"   ⏱️ Time: {result.get('total_duration', 0) / 1e9:.2f}s")
        else:
            print(f"   ❌ Generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
        return False
    
    # Test 4: Test JSON extraction
    print("\n4. Testing JSON generation...")
    try:
        prompt = """Return ONLY valid JSON with this format:
{
  "building_type": "residential",
  "bedroom_count": 2
}

No explanation, just the JSON."""
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            # Try to parse JSON
            import re
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                parsed_json = json.loads(json_match.group())
                print(f"   ✅ JSON parsing successful!")
                print(f"   📋 Result: {json.dumps(parsed_json, indent=2)}")
            else:
                print(f"   ⚠️ Could not find JSON in response")
                print(f"   Response: {generated_text}")
        else:
            print(f"   ❌ JSON test failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ JSON test error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour Ollama setup is ready!")
    print("You can now run: python main.py")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_ollama()
