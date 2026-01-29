from services.ollama_client import ollama_client
import json
from agents.prompts import COMPLETENESS_SYSTEM_PROMPT as SYSTEM_PROMPT

def check_completeness(domain: str, current_data: dict) -> dict:
    prompt = f"""
{SYSTEM_PROMPT}

Domain: {domain}
Current Data:
{json.dumps(current_data, indent=2)}
"""
    response = ollama_client.generate(prompt, format="json")
    print(f"DEBUG: Completeness Agent Raw Response:\n{response}\n")

    # Clean markdown code blocks if present
    cleaned_response = response.strip()
    if "```json" in cleaned_response:
        cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned_response:
        cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to parse info"}
