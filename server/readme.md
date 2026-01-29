# Morphogen Enhanced - AI-Powered Generative Design System

## Overview
Morphogen is a generative AI system that converts natural language prompts into BIM-compatible engineering designs. It specifically targets industrial facilities like desalination plants, enabling engineers to generate piping layouts, equipment arrangements, and architectural schematics through simple text commands.

## Problem Statement (AI-3)
**Generative Design (Text-to-Design)**: Develop a generative AI system where an engineer can type a natural language prompt such as "Generate a piping layout for a desalination plant with X capacity" and the model outputs a BIM-compatible schematic or AutoCAD draft.

## Key Features

### ✅ Current Enhancements
1. **Industrial Piping Support**
   - Desalination plant layouts
   - Process unit placement
   - Pipe routing with flow directions
   - Equipment positioning (pumps, tanks, RO units)
   - Valve placement

2. **Enhanced Geometry Schema**
   - Support for pipes (with diameters and flow)
   - Equipment objects (type, dimensions, capacity)
   - Valves and fittings
   - Annotations and labels

3. **BIM Compatibility**
   - IFC (Industry Foundation Classes) export
   - DXF (AutoCAD) export with layers
   - SVG visualization
   - Metadata preservation

4. **Domain Intelligence**
   - Engineering rules validation
   - Flow continuity checks
   - Spacing requirements
   - Industry standards compliance

5. **Multi-Agent Architecture**
   - Intent Classification
   - Completeness Checking
   - Engineering Planning
   - Geometry Generation
   - Validation & Export

## Architecture

```
User Prompt → Intent Agent → Completeness Agent → Planning Agent → Geometry Agent → Validators → Exporters
                                                                                                      ↓
                                                                               IFC | DXF | SVG | JSON
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend)
- Ollama (for local LLM) OR API keys for cloud LLMs

### Backend Setup
```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

## Usage Examples

### Example 1: Desalination Plant
```
Prompt: "Generate a piping layout for a desalination plant with 50 MLD capacity using reverse osmosis technology"

Output:
- Process units: Intake → Pretreatment → RO → Post-treatment
- Piping network with appropriate diameters
- Equipment placement
- IFC file for BIM software
- DXF file for AutoCAD
```

### Example 2: Building Layout
```
Prompt: "Create a 2-bedroom house with kitchen, living room, and bathroom"

Output:
- Room layout with walls
- Door placements
- Basic dimensions
- Architectural drawing exports
```

## API Endpoints

### Generate Design
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "Generate a piping layout for a desalination plant with 50 MLD capacity"
}
```

### Edit Design
```http
POST /api/edit
Content-Type: application/json

{
  "geometry": { ... existing geometry ... },
  "instruction": "Move the RO unit 5 meters to the right"
}
```

## Technology Stack

- **Backend**: FastAPI, Python
- **LLM**: Ollama (llama3.2) / Claude / Gemini
- **Export**: ezdxf, ifcopenshell
- **Frontend**: React, TailwindCSS
- **Validation**: Pydantic schemas

## Project Structure

```
morphogen_enhanced/
├── server/
│   ├── agents/           # AI agents for different tasks
│   │   ├── intent_agent.py
│   │   ├── planning_agent.py
│   │   ├── completeness_agent.py
│   │   ├── geometry_agent.py
│   │   └── prompts.py
│   ├── exporters/        # Export formats
│   │   ├── dxf.py
│   │   ├── svg.py
│   │   └── ifc.py
│   ├── schemas/          # Data models
│   │   ├── geometry.py
│   │   └── industrial.py
│   ├── services/         # Core services
│   │   ├── ollama_client.py
│   │   └── validators.py
│   └── routes/           # API routes
├── client/               # React frontend
└── docs/                 # Documentation
```

## Engineering Domains Supported

1. **Industrial**
   - Desalination plants
   - Water treatment facilities
   - Chemical processing
   - Power plants

2. **Residential**
   - Single-family homes
   - Apartments
   - Villas

3. **Commercial**
   - Offices
   - Retail spaces
   - Warehouses

## Validation Rules

### Industrial Piping
- Minimum spacing between pipes: 500mm
- Maximum pipe length without support: 6000mm
- Flow continuity: inlet flow = outlet flow
- Equipment clearance: minimum 1500mm

### Building Layout
- Wall continuity (closed boundaries)
- Door placement on walls
- Minimum room dimensions
- Accessibility requirements

## Export Formats

### IFC (BIM)
- Full 3D geometry
- Object properties
- Relationships
- Industry standard for BIM software

### DXF (AutoCAD)
- Layered 2D drawings
- Precise coordinates
- Compatible with all CAD software

### SVG
- Visual preview
- Web-compatible
- Scalable graphics

## Configuration

### LLM Selection
Choose between:
1. **Ollama (Local)** - Free, private, slower
2. **Claude API** - Fast, accurate, paid
3. **Google Gemini** - Balanced, paid

Edit `.env`:
```env
# For Ollama
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# For Claude
USE_CLAUDE=false
ANTHROPIC_API_KEY=your_key_here

# For Gemini
USE_GEMINI=false
GOOGLE_API_KEY=your_key_here
```

## Future Enhancements

1. **3D Geometry Generation**
2. **Parametric Design**
3. **Multi-floor Buildings**
4. **Structural Analysis Integration**
5. **Cost Estimation**
6. **Material Specifications**
7. **Real-time Collaboration**
8. **Version Control**

## Contributing
Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## License
MIT License - See LICENSE file

## Contact
For questions and support, please open an issue on GitHub.

## Acknowledgments
Built for the AI-3 Generative Design challenge, focusing on transforming natural language into engineering-grade designs.