"""
Hugging Face Inference API - 100% FREE
No installation, no system requirements, just API calls!
"""

import os
import requests
from typing import Dict, Any


class HuggingFaceAgent:
    """
    Use Hugging Face Inference API (FREE)
    No installation needed!
    """
    
    def __init__(self, hf_token: str = None, model: str = "meta-llama/Llama-3.2-3B-Instruct"):
        """
        Initialize Hugging Face agent
        
        Args:
            hf_token: Hugging Face API token (get free from hf.co/settings/tokens)
            model: Model to use (default: Llama 3.2 3B)
        """
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        if not self.hf_token:
            raise ValueError("HF_TOKEN required. Get free token from: https://huggingface.co/settings/tokens")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """
        Generate text using Hugging Face API
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 503:
                # Model is loading, wait and retry
                print("  Model loading, retrying in 20 seconds...")
                import time
                time.sleep(20)
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"HF API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            elif isinstance(result, dict):
                return result.get('generated_text', '')
            else:
                raise Exception(f"Unexpected response format: {result}")
                
        except Exception as e:
            raise Exception(f"Hugging Face API failed: {str(e)}")


# Available FREE models on Hugging Face
FREE_MODELS = {
    "llama-3.2-3b": "meta-llama/Llama-3.2-3B-Instruct",  # RECOMMENDED
    "llama-3.2-1b": "meta-llama/Llama-3.2-1B-Instruct",  # Faster
    "phi-3": "microsoft/Phi-3-mini-4k-instruct",         # Good quality
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",    # High quality
    "gemma-2b": "google/gemma-2b-it",                    # Fast
}


def check_hf_setup():
    """Check if Hugging Face is set up correctly"""
    
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_token:
        print("❌ HF_TOKEN not found")
        print("\nSetup steps:")
        print("1. Go to: https://huggingface.co/settings/tokens")
        print("2. Create a new token (Free)")
        print("3. Add to backend/.env:")
        print("   HF_TOKEN=your_token_here")
        return False
    
    try:
        agent = HuggingFaceAgent(hf_token)
        response = agent.generate("Hello", max_tokens=10)
        print(f"✅ Hugging Face API working!")
        print(f"   Model: {agent.model}")
        print(f"   Response: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ HF API error: {e}")
        return False


if __name__ == "__main__":
    check_hf_setup()
