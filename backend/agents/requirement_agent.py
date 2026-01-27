"""
Agent 2: Requirement Expansion Agent - Updated with better connectivity
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
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            timeout=120,
            max_retries=3,
            transport="rest"
        )
        self.prompt_template = PromptTemplate(
            input_variables=["intent_data"],
            template=REQUIREMENT_AGENT_PROMPT
        )
    
    def expand(self, intent_data: dict) -> dict:
        """
        Expand intent into complete requirements
        
        Args:
            intent_data: Structured intent from Agent 1
            
        Returns:
            Complete requirements with room list and dimensions
        """
        try:
            print(f"  Sending request to {self.llm.model}...")
            
            # Format prompt
            prompt = self.prompt_template.format(
                intent_data=json.dumps(intent_data, indent=2)
            )
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            print(f"  Received response ({len(response.content)} chars)")
            
            # Extract and validate
            requirements = self._extract_json(response.content)
            self._validate_requirements(requirements)
            
            return requirements
            
        except Exception as e:
            print(f"  ⚠️ Error in RequirementAgent: {e}")
            print(f"  Using fallback requirements")
            return self._get_default_requirements(intent_data)
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response"""
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Could not extract valid JSON")
    
    def _validate_requirements(self, reqs: dict):
        """Validate requirements structure"""
        required = ["building_type", "total_area_sqft", "floor_count", "rooms"]
        for key in required:
            if key not in reqs:
                raise ValueError(f"Missing: {key}")
    
    def _get_default_requirements(self, intent: dict) -> dict:
        """Fallback requirements"""
        bedroom_count = intent.get('bedroom_count', 2)
        
        # Default 2BHK layout
        rooms = [
            {"name": "Living Room", "area_sqft": 150, "type": "living"},
            {"name": "Kitchen", "area_sqft": 80, "type": "kitchen"},
        ]
        
        # Add bedrooms
        for i in range(bedroom_count):
            rooms.append({
                "name": f"Bedroom {i+1}",
                "area_sqft": 120 if i == 0 else 100,
                "type": "bedroom"
            })
        
        # Add bathrooms (1 per 2 bedrooms, min 1)
        bathroom_count = max(1, (bedroom_count + 1) // 2)
        for i in range(bathroom_count):
            rooms.append({
                "name": f"Bathroom {i+1}",
                "area_sqft": 30 if i == 0 else 25,
                "type": "bathroom"
            })
        
        total_area = sum(r['area_sqft'] for r in rooms) * 1.2  # +20% for circulation
        
        return {
            "building_type": intent.get('building_type', 'residential'),
            "total_area_sqft": int(total_area),
            "floor_count": intent.get('floor_count', 1),
            "rooms": rooms
        }
