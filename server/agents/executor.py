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

def run_lsp_agent(plan: dict, geometry: GeometryOutput) -> str:
    from agents.prompt_builder import build_lsp_prompt
    
    # Convert Pydantic to dict
    geometry_dict = geometry.dict() if hasattr(geometry, 'dict') else geometry
    
    prompt = build_lsp_prompt(plan, geometry_dict)
    raw_response = ollama_client.generate(prompt) # Text output, not JSON format enforced
    
    # Strip markdown code blocks if present
    if "```lisp" in raw_response:
        raw_response = raw_response.split("```lisp")[1].split("```")[0].strip()
    elif "```" in raw_response:
        raw_response = raw_response.split("```")[1].split("```")[0].strip()
        
    return raw_response


def run_lsp_to_svg_agent(lsp_code: str) -> str:
    from agents.prompt_builder import build_lsp_to_svg_prompt
    
    prompt = build_lsp_to_svg_prompt(lsp_code)
    raw_response = ollama_client.generate(prompt)
    
    # Strip markdown code blocks if present
    if "```svg" in raw_response:
        raw_response = raw_response.split("```svg")[1].split("```")[0].strip()
    elif "```xml" in raw_response:
        raw_response = raw_response.split("```xml")[1].split("```")[0].strip()
    elif "```" in raw_response:
        raw_response = raw_response.split("```")[1].split("```")[0].strip()
        
    return raw_response

