from services.ollama_client import ollama_client
import json
from agents.prompts import INTENT_SYSTEM_PROMPT as SYSTEM_PROMPT

def get_intent(user_prompt: str) -> dict:
    prompt = f"""
{SYSTEM_PROMPT}

Input:
{user_prompt}
"""
    response = ollama_client.generate(prompt, format="json")
    print(f"DEBUG: Intent Agent Raw Response:\n{response}\n")
    
    # Clean markdown code blocks if present
    cleaned_response = response.strip()
    if "```json" in cleaned_response:
        cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned_response:
        cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        # Fallback or error handling
        return {"domain": "unknown", "subdomain": "unknown", "intent": "unknown", "error": "Failed to parse JSON"}
