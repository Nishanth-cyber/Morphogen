"""
Agent 3: Engineering Rules Agent
Validates and adjusts dimensions according to building codes
"""

import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from templates.prompts import RULES_AGENT_PROMPT


class RulesAgent:
    """
    Applies architectural and engineering rules to room dimensions
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )
        self.prompt_template = PromptTemplate(
            input_variables=["requirements"],
            template=RULES_AGENT_PROMPT
        )
    
    def validate(self, requirements: dict) -> dict:
        """
        Validate and adjust room dimensions
        
        Args:
            requirements: Output from RequirementAgent
            
        Returns:
            Dictionary with validated dimensions in millimeters
        """
        try:
            # Format prompt with requirements
            prompt = self.prompt_template.format(
                requirements=json.dumps(requirements, indent=2)
            )
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response
            dimensions = self._extract_json(response.content)
            
            # Validate structure
            self._validate_dimensions(dimensions)
            
            return dimensions
            
        except Exception as e:
            print(f"Error in RulesAgent: {e}")
            # Return default dimensions on error
            return self._get_default_dimensions()
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks if present
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
    
    def _validate_dimensions(self, dimensions: dict):
        """Validate dimensions structure"""
        required_keys = ["rooms", "wall_thickness_mm", "door_width_mm"]
        
        for key in required_keys:
            if key not in dimensions:
                raise ValueError(f"Missing required key: {key}")
        
        if not isinstance(dimensions["rooms"], list):
            raise ValueError("rooms must be a list")
        
        for room in dimensions["rooms"]:
            required_room_keys = ["name", "width_mm", "length_mm", "area_sqft"]
            for key in required_room_keys:
                if key not in room:
                    raise ValueError(f"Each room must have '{key}'")
    
    def _get_default_dimensions(self) -> dict:
        """Return default dimensions for error cases"""
        return {
            "rooms": [
                {
                    "name": "Living Room",
                    "width_mm": 4000,
                    "length_mm": 5000,
                    "area_sqft": 215
                },
                {
                    "name": "Bedroom 1",
                    "width_mm": 3500,
                    "length_mm": 3500,
                    "area_sqft": 132
                },
                {
                    "name": "Bedroom 2",
                    "width_mm": 3000,
                    "length_mm": 3500,
                    "area_sqft": 113
                },
                {
                    "name": "Kitchen",
                    "width_mm": 4000,
                    "length_mm": 2500,
                    "area_sqft": 108
                },
                {
                    "name": "Bathroom 1",
                    "width_mm": 2000,
                    "length_mm": 2000,
                    "area_sqft": 43
                },
                {
                    "name": "Bathroom 2",
                    "width_mm": 1800,
                    "length_mm": 2000,
                    "area_sqft": 39
                }
            ],
            "wall_thickness_mm": 230,
            "door_width_mm": 900
        }
