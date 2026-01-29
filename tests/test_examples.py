"""
Example Usage and Testing for Morphogen Enhanced
Run this to test the API endpoints and see example workflows
"""

import requests
import json
import base64

# Base URL for API
BASE_URL = "http://localhost:8000/api"

def test_health():
    """Test server health"""
    print("=" * 60)
    print("TEST 0: Server Health Check")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ Server is running!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Server returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("  Make sure server is running: uvicorn main:app --reload")
    
    print("\n" + "=" * 60 + "\n")

def test_capabilities():
    """Query system capabilities"""
    print("=" * 60)
    print("TEST 1: System Capabilities")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/capabilities")
        capabilities = response.json()
        
        print("\nSupported Domains:")
        for domain, info in capabilities.get('domains', {}).items():
            print(f"\n  {domain.upper()}:")
            print(f"    Subdomains: {', '.join(info.get('subdomains', []))}")
            print(f"    Features: {', '.join(info.get('features', []))}")
        
        print(f"\nExport Formats:")
        for fmt in capabilities.get('export_formats', []):
            print(f"  - {fmt}")
        
        print(f"\nValidation Features:")
        for feature in capabilities.get('validation', []):
            print(f"  - {feature}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60 + "\n")

def test_desalination_plant_simple():
    """
    Example: Simple desalination plant generation
    Note: This will likely return 'incomplete' requiring clarifications
    """
    print("=" * 60)
    print("TEST 2: Desalination Plant Generation (Simple)")
    print("=" * 60)
    
    prompt = "Generate a piping layout for a desalination plant with 50 MLD capacity"
    
    print(f"\nPrompt: {prompt}\n")
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json={
            "prompt": prompt
        })
        
        if response.status_code != 200:
            print(f"✗ Server returned status {response.status_code}")
            print(f"Response: {response.text}")
            return

        result = response.json()
        print(f"Status: {result.get('status', 'MISSING_STATUS')}\n")
        
        if 'status' not in result:
             print(f"Unexpected response format: {result}")
             return

        if result['status'] == 'incomplete':
            print("Missing information - Questions to answer:")
            for i, question in enumerate(result.get('questions', []), 1):
                print(f"  {i}. {question}")
            
            print("\nTo complete, provide clarification_answers in next request")
        
        elif result['status'] == 'complete':
            print("✓ Design generated successfully!")
            geometry = result.get('geometry', {})
            print(f"\nGeometry:")
            print(f"  - Equipment: {len(geometry.get('equipment', []))} items")
            print(f"  - Pipes: {len(geometry.get('pipes', []))} segments")
            print(f"  - Valves: {len(geometry.get('valves', []))} units")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60 + "\n")

def test_desalination_plant_complete():
    """
    Example: Complete desalination plant with all clarifications
    """
    print("=" * 60)
    print("TEST 3: Desalination Plant Generation (Complete)")
    print("=" * 60)
    
    prompt = "Generate a piping layout for a desalination plant with 50 MLD capacity"
    
    print(f"\nPrompt: {prompt}")
    print("\nProviding complete clarifications...\n")
    
    try:
        # Provide all required information upfront
        response = requests.post(f"{BASE_URL}/generate", json={
            "prompt": prompt,
            "clarification_answers": {
                "technology": "reverse_osmosis",
                "site_dimensions": [120, 60],
                "inlet_source": "seawater",
                "recovery_rate": 45
            }
        })
        
        result = response.json()
        print(f"Status: {result['status']}\n")
        
        if result['status'] == 'complete':
            print("✓ Design generation complete!")
            
            # Show plan summary
            plan = result.get('plan', {})
            if plan:
                print(f"\nPlant Details:")
                print(f"  Capacity: {plan.get('capacity')} {plan.get('capacity_unit')}")
                print(f"  Site: {plan.get('site_dimensions')} meters")
                print(f"  Inlet Flow: {plan.get('inlet_flow_rate')} MLD")
                print(f"  Product Flow: {plan.get('outlet_flow_rate')} MLD")
                print(f"  Brine Flow: {plan.get('brine_flow_rate')} MLD")
            
            # Show geometry summary
            geometry = result.get('geometry', {})
            print(f"\nGeometry Generated:")
            print(f"  - Equipment: {len(geometry.get('equipment', []))} items")
            print(f"  - Pipes: {len(geometry.get('pipes', []))} segments")
            print(f"  - Valves: {len(geometry.get('valves', []))} units")
            
            # Show warnings
            if result.get('warnings'):
                print(f"\n⚠ Validation Warnings:")
                for warning in result['warnings']:
                    print(f"  - {warning}")
            
            # Show exports
            artifacts = result.get('artifacts', {})
            if artifacts:
                print(f"\nExports Available:")
                if artifacts.get('ifc'):
                    ifc_size = len(base64.b64decode(artifacts['ifc']))
                    print(f"  - IFC (BIM): {ifc_size} bytes")
                if artifacts.get('dxf'):
                    print(f"  - DXF (CAD): {len(artifacts['dxf'])} characters")
                if artifacts.get('svg'):
                    print(f"  - SVG (Preview): {len(artifacts['svg'])} characters")
        
        else:
            print(f"Status: {result['status']}")
            if result.get('questions'):
                print("Questions:", result['questions'])
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60 + "\n")

def test_house_generation():
    """
    Example: Residential house generation
    """
    print("=" * 60)
    print("TEST 4: Residential House Generation")
    print("=" * 60)
    
    prompt = "Create a 2-bedroom house with kitchen, living room, and bathroom on a 15m x 12m plot"
    
    print(f"\nPrompt: {prompt}\n")
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json={
            "prompt": prompt
        })
        
        result = response.json()
        print(f"Status: {result['status']}\n")
        
        if result['status'] == 'complete':
            print("✓ Design generation complete!")
            
            geometry = result.get('geometry', {})
            print(f"\nGeometry Generated:")
            print(f"  - Walls: {len(geometry.get('walls', []))} segments")
            print(f"  - Doors: {len(geometry.get('doors', []))} units")
            print(f"  - Windows: {len(geometry.get('windows', []))} units")
        
        elif result['status'] == 'incomplete':
            print("Questions needed:")
            for q in result.get('questions', []):
                print(f"  - {q}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60 + "\n")

def run_all_tests():
    """Run all example tests"""
    
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         MORPHOGEN ENHANCED - EXAMPLE USAGE TESTS          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Run tests in sequence
    test_health()
    test_capabilities()
    test_desalination_plant_simple()
    
    # Uncomment to run full tests (requires LLM to be configured)
    # test_desalination_plant_complete()
    # test_house_generation()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60 + "\n")
    print("\nNOTE: Full generation tests require:")
    print("  1. LLM configured (Ollama or API keys)")
    print("  2. Server running: uvicorn main:app --reload")
    print("\n")

if __name__ == "__main__":
    run_all_tests()
