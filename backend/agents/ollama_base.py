"""
Ollama Agent Base Class - FREE Local AI
Works with Docker or native Ollama installation
"""

import json
import re
import requests
from typing import Dict, Any


class OllamaBaseAgent:
    """
    Base class for Ollama agents - 100% free local AI
    """
    
    def __init__(self, 
                 model_name: str = "llama3.2",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 60):
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = timeout
        
    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            
        Returns:
            Generated text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 1000
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result['response']
            
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Is Docker running? Run: docker start ollama")
        except requests.exceptions.Timeout:
            raise Exception("Ollama timeout. Try a smaller model or increase timeout.")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def extract_json(self, text: str) -> Dict[Any, Any]:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Could not extract valid JSON from response")
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


def check_ollama_setup():
    """
    Check if Ollama is properly set up
    """
    print("Checking Ollama setup...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running!")
            print(f"✓ Available models: {[m['name'] for m in models]}")
            
            if not models:
                print("⚠️ No models downloaded yet!")
                print("Run: docker exec -it ollama ollama pull llama3.2")
            
            return True
        else:
            print("✗ Ollama returned error")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama")
        print("\nSetup instructions:")
        print("1. Install Docker Desktop")
        print("2. Run: docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama")
        print("3. Run: docker exec -it ollama ollama pull llama3.2")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    check_ollama_setup()
