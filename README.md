# Generative Engineering Design System
## Text-to-AutoCAD Floor Plan Generator

This project converts natural language descriptions into executable AutoCAD floor plans using a multi-agent AI system built with LangChain.

## Project Structure

```
AutoCAD/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── intent_agent.py          # Agent 1: Intent Understanding
│   │   ├── requirement_agent.py     # Agent 2: Requirement Expansion
│   │   ├── rules_agent.py           # Agent 3: Engineering Rules
│   │   ├── layout_agent.py          # Agent 4: Spatial Layout Planning
│   │   └── autolisp_agent.py        # Agent 5: AutoLISP Code Generation
│   ├── templates/
│   │   └── prompts.py               # All prompt templates
│   ├── output/                       # Generated .lsp files
│   ├── config.py                     # Configuration
│   ├── pipeline.py                   # Main agent pipeline
│   └── app.py                        # Flask API server
├── frontend/
│   ├── index.html                    # Main UI
│   ├── styles.css                    # Styling
│   └── script.js                     # Frontend logic
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the Backend Server

```bash
cd backend
python app.py
```

Server will start at `http://localhost:5000`

### 4. Open the Frontend

Open `frontend/index.html` in your web browser.

## Usage

1. Enter a natural language description like:
   - "Build me a 2-bedroom house"
   - "Design a small residential building"
   - "Create a 3BHK apartment layout"

2. Click "Generate Floor Plan"

3. Download the generated `.lsp` file

4. In AutoCAD:
   - Type: `(load "C:/path/to/output.lsp")`
   - Type: `GENPLAN`
   - Your floor plan will appear!

## Features

### Included
- 2D residential floor plans
- Automatic room layout generation
- Standard architectural rules
- AutoLISP code generation
- Support for 1-4 bedroom configurations

### Not Included (MVP)
- Multi-story buildings
- 3D modeling
- Furniture placement
- Windows (doors only)
- Commercial buildings

## Agent Architecture

1. **Intent Agent**: Parses user input and extracts building requirements
2. **Requirement Agent**: Fills missing details with engineering defaults
3. **Rules Agent**: Validates dimensions against architectural standards
4. **Layout Agent**: Generates 2D spatial coordinates
5. **AutoLISP Agent**: Converts geometry to executable AutoCAD code

## Technology Stack

- **Backend**: Python 3.9+, LangChain, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Model**: Google Gemini (via LangChain)
- **Output**: AutoLISP (.lsp)

## Troubleshooting

**Problem**: AutoLISP file doesn't load
- Ensure AutoCAD version 2010+
- Check file path has no special characters
- Verify file encoding is UTF-8

**Problem**: Backend server won't start
- Check if port 5000 is available
- Verify Google API key is set correctly
- Ensure all dependencies are installed

## License

MIT License - Free for educational and commercial use
