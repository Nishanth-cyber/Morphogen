"""
Agent 2: Requirement Expansion Agent
Fills in missing details with engineering defaults
"""

import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from templates.prompts import REQUIREMENT_AGENT_PROMPT


class RequirementAgent:
    """
    Expands incomplete requirements using architectural defaults
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )
        self.prompt_template = PromptTemplate(
            input_variables=["intent_data"],
            template=REQUIREMENT_AGENT_PROMPT
        )
    
    def expand(self, intent_data: dict) -> dict:
        """
        Expand intent data into complete requirements
        
        Args:
            intent_data: Output from IntentAgent
            
        Returns:
            Dictionary with complete room requirements
        """
        try:
            # Format prompt with intent data
            prompt = self.prompt_template.format(
                intent_data=json.dumps(intent_data, indent=2)
            )
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response
            requirements = self._extract_json(response.content)
            
            # Validate structure
            self._validate_requirements(requirements)
            
            return requirements
            
        except Exception as e:
            print(f"Error in RequirementAgent: {e}")
            # Return default requirements on error
            return self._get_default_requirements()
    
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
    
    def _validate_requirements(self, requirements: dict):
        """Validate requirements structure"""
        required_keys = ["building_type", "total_area_sqft", "floor_count", "rooms"]
        
        for key in required_keys:
            if key not in requirements:
                raise ValueError(f"Missing required key: {key}")
        
        if not isinstance(requirements["rooms"], list):
            raise ValueError("rooms must be a list")
        
        for room in requirements["rooms"]:
            if "name" not in room or "min_area_sqft" not in room:
                raise ValueError("Each room must have 'name' and 'min_area_sqft'")
    
    def _get_default_requirements(self) -> dict:
        """Return default requirements for error cases"""
        return {
            "building_type": "residential",
            "total_area_sqft": 1000,
            "floor_count": 1,
            "rooms": [
                {"name": "Living Room", "min_area_sqft": 150},
                {"name": "Bedroom 1", "min_area_sqft": 120},
                {"name": "Bedroom 2", "min_area_sqft": 100},
                {"name": "Kitchen", "min_area_sqft": 80},
                {"name": "Bathroom 1", "min_area_sqft": 30},
                {"name": "Bathroom 2", "min_area_sqft": 25}
            ]
        }
