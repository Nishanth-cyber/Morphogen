"""
Agent 1: Intent Understanding Agent
Parses natural language and extracts construction intent
"""

import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from templates.prompts import INTENT_AGENT_PROMPT


class IntentAgent:
    """
    Understands user construction intent and extracts structured information
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )
        self.prompt_template = PromptTemplate(
            input_variables=["user_input"],
            template=INTENT_AGENT_PROMPT
        )
    
    def parse(self, user_input: str) -> dict:
        """
        Parse user input and extract intent
        
        Args:
            user_input: Natural language construction request
            
        Returns:
            Dictionary with extracted intent information
        """
        try:
            # Format prompt
            prompt = self.prompt_template.format(user_input=user_input)
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response
            intent_data = self._extract_json(response.content)
            
            # Validate structure
            self._validate_intent(intent_data)
            
            return intent_data
            
        except Exception as e:
            print(f"Error in IntentAgent: {e}")
            # Return default intent on error
            return self._get_default_intent()
    
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
    
    def _validate_intent(self, intent: dict):
        """Validate intent structure"""
        required_keys = [
            "building_type",
            "scale",
            "explicit_rooms",
            "bedroom_count",
            "floor_count",
            "area_sqft",
            "special_requirements"
        ]
        
        for key in required_keys:
            if key not in intent:
                raise ValueError(f"Missing required key: {key}")
    
    def _get_default_intent(self) -> dict:
        """Return default intent for error cases"""
        return {
            "building_type": "residential",
            "scale": "medium",
            "explicit_rooms": [],
            "bedroom_count": 2,
            "floor_count": 1,
            "area_sqft": None,
            "special_requirements": []
        }
