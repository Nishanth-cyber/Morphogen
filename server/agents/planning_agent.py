from services.ollama_client import ollama_client
import json
from agents.prompts import PLANNING_SYSTEM_PROMPT as SYSTEM_PROMPT

def create_plan(merged_requirements: dict) -> dict:
    prompt = f"""
{SYSTEM_PROMPT}

Input Requirements:
{json.dumps(merged_requirements, indent=2)}
"""
    response = ollama_client.generate(prompt, format="json")
    print(f"DEBUG: Planning Agent Raw Response:\n{response}\n")

    # Clean markdown code blocks if present
    cleaned_response = response.strip()
    if "```json" in cleaned_response:
        cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned_response:
        cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return {"error": "Failed to generate plan"}
