"""
Quick fix script to update all agents with better connectivity settings
Run this once to update all agent files
"""

import os
import re

def update_agent_file(filepath):
    """Update agent file with new LLM initialization"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the old initialization
    old_pattern = r'self\.llm = ChatGoogleGenerativeAI\(\s*model=model_name,\s*google_api_key=api_key,\s*temperature=temperature\s*\)'
    
    # New initialization with better settings
    new_init = '''self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            timeout=120,
            max_retries=3,
            transport="rest"
        )'''
    
    # Replace
    content = re.sub(old_pattern, new_init, content)
    
    # Update default model name
    content = content.replace(
        'model_name: str = "gemini-pro"',
        'model_name: str = "gemini-1.5-flash"'
    )
    
    # Add print statements after invoke
    if 'response = self.llm.invoke(prompt)' in content and 'print(f"  Sending request' not in content:
        content = content.replace(
            'response = self.llm.invoke(prompt)',
            'print(f"  Sending request to {self.llm.model}...")\n            response = self.llm.invoke(prompt)\n            print(f"  Received response ({len(response.content)} chars)")'
        )
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated: {filepath}")

if __name__ == "__main__":
    agents_dir = "agents"
    agent_files = [
        "intent_agent.py",
        "requirement_agent.py", 
        "rules_agent.py",
        "layout_agent.py",
        "autolisp_agent.py"
    ]
    
    for agent_file in agent_files:
        filepath = os.path.join(agents_dir, agent_file)
        if os.path.exists(filepath):
            try:
                update_agent_file(filepath)
            except Exception as e:
                print(f"✗ Failed to update {agent_file}: {e}")
    
    print("\nAll agents updated!")
    print("Please restart your server: python main.py")
