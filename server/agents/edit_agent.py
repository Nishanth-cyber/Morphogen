from services.ollama_client import ollama_client
import json
from agents.prompts import EDIT_SYSTEM_PROMPT as SYSTEM_PROMPT

def edit_geometry(current_geometry: dict, instruction: str) -> dict:
    prompt = f"""
{SYSTEM_PROMPT}

Existing Geometry:
{json.dumps(current_geometry, indent=2)}

Edit Instruction:
{instruction}
"""
    response = ollama_client.generate(prompt, format="json")
    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Failed to edit geometry", "original": current_geometry}
