from services.ollama_client import ollama_client
from agents.prompt_builder import build_geometry_prompt
from schemas.geometry import GeometryOutput
import json

def run_geometry_agent(constraints: dict) -> GeometryOutput:
    prompt = build_geometry_prompt(constraints)
    raw_response = ollama_client.generate(prompt, format="json")

    try:
        if "```json" in raw_response:
            raw_response = raw_response.split("```json")[1].split("```")[0].strip()
        parsed = json.loads(raw_response)
        return GeometryOutput(**parsed)
    except Exception as e:
        raise ValueError(f"Invalid agent output: {e}")
