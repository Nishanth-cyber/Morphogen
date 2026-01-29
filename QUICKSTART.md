# Quick Start Guide - Morphogen Enhanced

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- Git
- Ollama (for local LLM) OR API keys for Claude/Gemini

---

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd D:\Projects\Working\Morphogen

# Create virtual environment
cd server
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure LLM

### Option A: Use Ollama (Local, Free)

```bash
# Install Ollama from https://ollama.ai

# Pull a model
ollama pull llama3.2

# Verify it's running
curl http://localhost:11434/api/tags
```

### Option B: Use Cloud LLM (Faster, Paid)

Edit `.env` file in the server directory:
```env
# For Claude
USE_CLAUDE=true
ANTHROPIC_API_KEY=your_anthropic_key_here

# OR for Gemini
USE_GEMINI=true
GOOGLE_API_KEY=your_google_key_here
```

---

## Step 3: Run the Server

```bash
# Make sure you're in the server directory
cd D:\Projects\Working\Morphogen\server

# Run the FastAPI server
uvicorn main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Step 4: Test the API

### Using curl:

```bash
# Check health
curl http://localhost:8000/health

# Get capabilities
curl http://localhost:8000/api/capabilities

# Generate a design
curl -X POST http://localhost:8000/api/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Generate a piping layout for a 50 MLD desalination plant\"}"
```

### Using Python:

```python
import requests

# Simple example
response = requests.post(
    "http://localhost:8000/api/generate",
    json={"prompt": "Create a 2-bedroom house"}
)

result = response.json()
print(result['status'])  # 'incomplete' or 'complete'

# If incomplete, provide clarifications
if result['status'] == 'incomplete':
    print("Questions:", result['questions'])
```

---

## Step 5: Example Workflow

### Example 1: Desalination Plant (Full Flow)

**Request 1 (Initial):**
```json
POST /api/generate
{
  "prompt": "Generate a piping layout for a desalination plant with 50 MLD capacity"
}
```

**Response 1:**
```json
{
  "status": "incomplete",
  "questions": [
    "What desalination technology should be used? (RO, MSF, MED)",
    "What are the site dimensions in meters?",
    "What is the water source? (seawater or brackish)"
  ]
}
```

**Request 2 (With clarifications):**
```json
POST /api/generate
{
  "prompt": "Generate a piping layout for a desalination plant with 50 MLD capacity",
  "clarification_answers": {
    "technology": "reverse_osmosis",
    "site_dimensions": [120, 60],
    "inlet_source": "seawater"
  }
}
```

---

## Opening the Output Files

### IFC Files (BIM)
1. **Autodesk Revit**
   - File → Open → Select .ifc file
   
2. **Free Viewers:**
   - BIM Vision: https://bimvision.eu
   - IFC.js Viewer: https://ifcjs.github.io/hello-world/

### DXF Files (CAD)
1. **AutoCAD**
   - File → Open → Select .dxf file
   
2. **Free Alternatives:**
   - DraftSight: https://www.draftsight.com
   - LibreCAD: https://librecad.org

### SVG Files (Preview)
- Open directly in any web browser

---

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/capabilities` | GET | List supported domains and features |
| `/api/generate` | POST | Generate design (returns JSON) |
| `/api/generate/ifc` | POST | Generate design (returns IFC file) |
| `/api/generate/dxf` | POST | Generate design (returns DXF file) |
| `/api/edit` | POST | Edit existing design |

---

## Common Issues & Solutions

### Issue: "Connection refused"
**Solution:** Make sure the server is running:
```bash
cd D:\Projects\Working\Morphogen\server
uvicorn main:app --reload
```

### Issue: "Ollama not responding"
**Solution:** 
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Issue: "Module not found"
**Solution:** Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

1. **Explore Examples:**
   Check the tests directory for usage examples

2. **Try Different Prompts:**
   - "Generate a water treatment plant for 100,000 people"
   - "Create a 3-bedroom villa with pool"
   - "Design a warehouse with loading docks"

3. **Read Documentation:**
   - [README.md](README.md) - Full documentation
   - [ENHANCEMENTS.md](ENHANCEMENTS.md) - Technical details
   - [COMPARISON.md](COMPARISON.md) - Before/after analysis

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                    MORPHOGEN ENHANCED                    │
├─────────────────────────────────────────────────────────┤
│ Start Server:                                           │
│   uvicorn main:app --reload                             │
│                                                         │
│ Generate Design:                                        │
│   POST /api/generate                                    │
│   Body: {"prompt": "your prompt here"}                  │
│                                                         │
│ Outputs:                                                │
│   - IFC (BIM - Revit, ArchiCAD)                         │
│   - DXF (CAD - AutoCAD)                                 │
│   - SVG (Web Preview)                                   │
│                                                         │
│ Supported Domains:                                      │
│   - Industrial (desalination, water treatment)          │
│   - Residential (houses, apartments)                    │
│   - Commercial (offices, warehouses)                    │
└─────────────────────────────────────────────────────────┘
```

Happy Designing! 🎨🏗️
