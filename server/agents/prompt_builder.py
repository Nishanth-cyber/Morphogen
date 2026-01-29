import json
from agents.prompts import GEOMETRY_SYSTEM_PROMPT as SYSTEM_PROMPT

def build_geometry_prompt(constraints: dict) -> str:
    return f"""
{SYSTEM_PROMPT}

Input constraints (JSON):
{json.dumps(constraints, indent=2)}

Output JSON only:
"""

def build_lsp_prompt(plan: dict, geometry: dict) -> str:
    from agents.prompts import LSP_SYSTEM_PROMPT_V2 as LSP_SYSTEM_PROMPT
    return f"""
{LSP_SYSTEM_PROMPT}

DESIGN DATA (JSON):
{json.dumps({'plan': plan, 'geometry': geometry}, indent=2)}

GENERATE AUTOLISP SCRIPT:
"""


def build_lsp_to_svg_prompt(lsp_code: str) -> str:
    from agents.prompts import LSP_TO_SVG_SYSTEM_PROMPT
    return f"""
{LSP_TO_SVG_SYSTEM_PROMPT}

AUTOLISP CODE:
{lsp_code}

GENERATE SVG XML:
"""

