import json
from agents.prompts import GEOMETRY_SYSTEM_PROMPT as SYSTEM_PROMPT

def build_geometry_prompt(constraints: dict) -> str:
    return f"""
{SYSTEM_PROMPT}

Input constraints (JSON):
{json.dumps(constraints, indent=2)}

Output JSON only:
"""
