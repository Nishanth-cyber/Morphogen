# Morphogen Frontend

ChatGPT-style conversational UI for AI-powered engineering design generation.

## Features

- 💬 **Conversational Interface** - ChatGPT-like chat experience
- 🎨 **Live Preview** - Real-time SVG visualization
- 🔄 **Prompt-Based Editing** - Modify designs through natural language
- 📥 **Export Formats** - Download as DXF (AutoCAD) or IFC (BIM)
- ✅ **Validation Warnings** - Real-time engineering checks
- 🎯 **Clarification Loop** - Interactive question-answer workflow

## Quick Start

### Prerequisites

- Node.js 16+
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
client/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx
│   │   ├── ChatHistory.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   ├── LoadingIndicator.tsx
│   │   └── SVGPreview.tsx
│   ├── services/            # API services
│   │   └── api.ts
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── utils/               # Utility functions
│   │   └── helpers.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Usage

### Starting a Conversation

1. Type your design prompt in the input box
2. Example: "Generate a piping layout for a 50 MLD desalination plant"
3. Press Enter to send

### Clarification Questions

If the system needs more information:
1. Questions will appear in the chat
2. Answer them in the input box
3. The design will generate once all questions are answered

### Editing Designs

Once a design is generated:
1. Type edit instructions: "Move the pump 5 meters to the right"
2. The design will update automatically
3. View changes in the preview panel

### Exporting

Click the export buttons in the preview panel:
- **Export DXF** - For AutoCAD
- **Export IFC** - For BIM software (Revit, ArchiCAD)

## API Integration

The frontend communicates with the backend via these endpoints:

- `POST /api/generate` - Generate new design
- `POST /api/edit` - Edit existing design
- `POST /api/generate/dxf` - Export to DXF
- `POST /api/generate/ifc` - Export to IFC
- `GET /api/capabilities` - Get system capabilities
- `GET /health` - Health check

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

## Development

### Code Style

- TypeScript strict mode enabled
- ESLint for code quality
- Functional components with hooks
- Props interfaces for all components

### State Management

State is managed at the App level with React hooks:
- `messages` - Chat history
- `currentGeometryJSON` - Active design data
- `svgPreview` - SVG visualization
- `loadingState` - UI loading states

### Adding New Features

1. Create component in `src/components/`
2. Add types in `src/types/`
3. Update API service if needed
4. Import and use in `App.tsx`

## Troubleshooting

### Backend Connection Issues

If you see connection errors:
1. Ensure backend is running: `uvicorn main:app --reload`
2. Check proxy settings in `vite.config.ts`
3. Verify API URL in `.env`

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

## License

MIT License - See LICENSE file
