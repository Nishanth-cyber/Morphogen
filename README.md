# Generative Design Studio

AI-Powered Floor Plan Generation for AutoCAD - Convert natural language descriptions into professional CAD drawings.

## Features

✅ **Natural Language Input** - Describe your building in plain English  
✅ **Multi-Agent AI System** - 5 specialized agents for intelligent design generation  
✅ **Interactive Canvas Editor** - Drag, resize, and modify generated designs  
✅ **Multiple Export Formats** - AutoLISP (.lsp), DXF, DWG, and JSON  
✅ **Real-time Updates** - All file formats update when you edit  
✅ **Grid Snapping** - Precise alignment and measurements  
✅ **Undo/Redo** - Full editing history  

---

## System Architecture

```
User Input (Natural Language)
        ↓
┌───────────────────────────────┐
│   Multi-Agent AI Pipeline     │
│                               │
│  Agent 1: Intent Understanding │
│  Agent 2: Requirement Expansion│
│  Agent 3: Engineering Rules   │
│  Agent 4: Layout Planning     │
│  Agent 5: Dual Output Gen     │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│    File Management System     │
│                               │
│  • design.json (master data)  │
│  • floorplan.lsp (AutoLISP)   │
│  • floorplan.dxf (interchange)│
│  • floorplan.dwg (AutoCAD)    │
└───────────────────────────────┘
        ↓
Web Canvas Editor (Fabric.js)
```

---

## Installation

### Prerequisites

- Python 3.9+
- Node.js (optional, for frontend development)
- Google API Key (Gemini)
- ODA File Converter (for DWG export)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the `backend` directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-pro
TEMPERATURE=0.7
```

5. **Install ODA File Converter (for DWG export):**

Download from: https://www.opendesign.com/guestfiles/oda_file_converter

Install to default location: `C:/Program Files/ODA/ODAFileConverter/`

### Frontend Setup

The frontend is vanilla HTML/CSS/JS - no build process needed!

Just open `frontend/index.html` in a browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

Then visit: http://localhost:3000

---

## Usage

### 1. Start the Backend Server

```bash
cd backend
python main.py
```

Server will start at: http://localhost:8000  
API Docs at: http://localhost:8000/docs

### 2. Open the Frontend

Open `frontend/index.html` in your browser

### 3. Generate a Design

Enter a description like:
- "Build me a 2-bedroom house"
- "Design a 3-bedroom home with attached garage"
- "I need a small residential building with open kitchen"

Click "Generate Design" and wait 30-60 seconds.

### 4. Edit the Design

- **Move elements:** Click and drag
- **Resize:** Use corner handles
- **Delete:** Select and press Delete key or use toolbar
- **Change properties:** Select element and use property panel

### 5. Save Changes

Click "💾 Save Changes" to update all file formats:
- design.json
- floorplan.lsp
- floorplan.dxf
- floorplan.dwg

### 6. Export Files

Click "📥 Export" and choose format:
- **AutoLISP (.lsp)** - Load directly in AutoCAD
- **DXF (.dxf)** - Universal CAD format
- **DWG (.dwg)** - Native AutoCAD format
- **JSON (.json)** - Raw design data

---

## API Endpoints

### Generate Design
```http
POST /generate
Content-Type: application/json

{
  "prompt": "Design a 2-bedroom house"
}
```

### Update Design
```http
PUT /update
Content-Type: application/json

{
  "project_id": "abc12345",
  "design_data": { ... }
}
```

### Get Project
```http
GET /project/{project_id}
```

### List All Projects
```http
GET /projects
```

### Download File
```http
GET /download/{project_id}/{file_type}
```
file_type: `lsp`, `dxf`, `dwg`, or `json`

### Delete Project
```http
DELETE /project/{project_id}
```

### Health Check
```http
GET /health
```

---

## File Structure

```
Morphogen/
├── backend/
│   ├── agents/                 # AI agents
│   │   ├── intent_agent.py
│   │   ├── requirement_agent.py
│   │   ├── rules_agent.py
│   │   ├── layout_agent.py
│   │   └── autolisp_agent.py
│   ├── converters/             # Format converters
│   │   ├── json_to_autolisp.py
│   │   ├── json_to_dxf.py
│   │   └── dxf_to_dwg.py
│   ├── projects/               # Generated projects
│   │   └── project_xxxxx/
│   │       ├── design.json
│   │       ├── floorplan.lsp
│   │       ├── floorplan.dxf
│   │       └── floorplan.dwg
│   ├── main.py                 # FastAPI server
│   ├── pipeline.py             # Agent orchestration
│   ├── file_manager.py         # File operations
│   ├── config.py               # Configuration
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Main UI
│   ├── styles.css              # Styling
│   └── script.js               # Canvas editor logic
└── README.md
```

---

## How It Works

### Agent Pipeline

1. **Intent Understanding Agent**
   - Parses natural language input
   - Extracts building type, room count, scale
   - Example output: `{building_type: "residential", bedroom_count: 2}`

2. **Requirement Expansion Agent**
   - Fills missing details with defaults
   - Defines room list and sizes
   - Example: 2BHK → Living room, 2 bedrooms, kitchen, 2 bathrooms

3. **Engineering Rules Agent**
   - Applies architectural standards
   - Validates dimensions (min room sizes, wall thickness)
   - Ensures code compliance

4. **Layout Planning Agent**
   - Converts requirements to 2D coordinates
   - Places rooms logically
   - Generates walls, doors, windows

5. **Dual Output Generator**
   - Produces JSON for frontend rendering
   - Generates AutoLISP code for AutoCAD
   - Both formats stay synchronized

### File Management

When you **generate** a design:
1. JSON data saved as master record
2. AutoLISP code generated from JSON
3. DXF file created using ezdxf library
4. DWG file converted from DXF (ODA Converter)

When you **edit** in canvas:
1. Changes tracked in JSON structure
2. Click "Save" to update backend
3. All 4 file formats regenerated automatically

---

## Using AutoLISP Files

### In AutoCAD

1. Open AutoCAD
2. Type: `APPLOAD`
3. Browse to `floorplan.lsp`
4. Load the file
5. Type: `GENPLAN`
6. Floor plan appears!

### AutoLISP Code Structure

```lisp
(defun c:GENPLAN ( / )
  ;; Create layers
  (command "._LAYER" "N" "WALLS" "C" "7" "WALLS" "")
  
  ;; Draw external boundary
  (command "._PLINE" "0,0" "10000,0" ...)
  
  ;; Draw walls, doors, labels
  ...
  
  ;; Zoom to fit
  (command "._ZOOM" "E")
)
```

---

## Troubleshooting

### DWG Conversion Fails

**Problem:** "Warning: ODA File Converter not found"

**Solution:** 
1. Download ODA Converter: https://www.opendesign.com/guestfiles/oda_file_converter
2. Install to default location
3. Restart backend server

If converter still not found, manually edit `converters/dxf_to_dwg.py` and add your installation path.

### Backend Won't Start

**Problem:** "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** "Google API Key error"

**Solution:** Check `.env` file has valid `GOOGLE_API_KEY`

### Frontend Canvas Not Rendering

**Problem:** Design generates but canvas is blank

**Solution:**
1. Check browser console for errors
2. Ensure Fabric.js loaded (check network tab)
3. Try refreshing page

### CORS Errors

**Problem:** "Access-Control-Allow-Origin" error

**Solution:** Backend already has CORS enabled. If still issues:
1. Serve frontend through HTTP server (not file://)
2. Check `API_BASE_URL` in `script.js` matches backend URL

---

## Configuration

### config.py

```python
class Config:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-1.5-pro')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    OUTPUT_DIR = 'output'
```

### Frontend Constants

In `script.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
const SCALE_FACTOR = 0.08;  // 1mm = 0.08px
const GRID_SIZE = 50;        // pixels
```

---

## Development

### Adding New Room Types

Edit `agents/requirement_agent.py`:

```python
ROOM_DEFAULTS = {
    'residential': {
        'living_room': 150,
        'bedroom': 120,
        'kitchen': 80,
        # Add new room types here
        'study': 100,
        'gym': 150
    }
}
```

### Customizing Canvas

Edit `frontend/script.js`:

```javascript
function initializeCanvas() {
    fabricCanvas = new fabric.Canvas('designCanvas', {
        width: 1200,  // Change canvas size
        height: 900,
        backgroundColor: '#f5f5f5'  // Change background
    });
}
```

### Adding Export Formats

1. Create converter in `backend/converters/`
2. Add endpoint in `main.py`
3. Update frontend export menu

---

## License

MIT License - See LICENSE file

---

## Credits

- **AI Models:** Google Gemini
- **Canvas Library:** Fabric.js
- **DXF Library:** ezdxf
- **DWG Conversion:** ODA File Converter
- **Backend Framework:** FastAPI
- **Frontend:** Vanilla JavaScript

---

## Support

For issues, questions, or feature requests:
1. Check this README
2. Review API docs at http://localhost:8000/docs
3. Check browser/server console for errors

---

## Roadmap

- [ ] Multi-floor support
- [ ] Furniture placement
- [ ] 3D visualization
- [ ] Structural calculations
- [ ] Cost estimation
- [ ] Building code validation by region
- [ ] Collaborative editing
- [ ] Cloud deployment

---

**Built with ❤️ for architects and engineers**
