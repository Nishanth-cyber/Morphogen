import React, { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import InputSection from './components/InputSection';
import AgentProgress from './components/AgentProgress';
import CanvasEditor from './components/CanvasEditor';
import Toolbar from './components/Toolbar';
import PropertyPanel from './components/PropertyPanel';
import StatusMessage from './components/StatusMessage';
import { generateDesign, updateDesign, downloadFile } from './api/client';
import { updateDesignDataFromCanvas } from './utils/designUtils';

function App() {
  // State
  const [projectInfo, setProjectInfo] = useState(null);
  const [status, setStatus] = useState({ message: '', type: '' });
  const [isGenerating, setIsGenerating] = useState(false);

  // Editor State
  const [selectedObject, setSelectedObject] = useState(null);
  const [showGrid, setShowGrid] = useState(true);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [showSaveMenu, setShowSaveMenu] = useState(false);

  // Refs
  const canvasRef = useRef(null);
  const agentRef = useRef(null);

  // History
  const undoStack = useRef([]);
  const redoStack = useRef([]);

  // Handlers
  const showStatus = (message, type = 'info') => {
    console.log(`📢 Status [${type}]:`, message);
    setStatus({ message, type });
  };

  const handleGenerate = async (prompt) => {
    setIsGenerating(true);
    agentRef.current?.startSimulation();

    // 1. Initial "Thinking" Phase (Simulated)
    agentRef.current?.updateStep(1, { status: 'active', desc: 'Analyzing request...' });

    // Simulate short delay then move to next step to show activity before API call
    setTimeout(() => {
      agentRef.current?.updateStep(1, { status: 'completed', result: 'Intent understood' });
      agentRef.current?.updateStep(2, { status: 'active', desc: 'Consulting design engine...' });
    }, 1500);

    try {
      const result = await generateDesign(prompt);

      if (result.success) {
        // Validate design data structure
        if (!result.design_data || !result.design_data.elements) {
          throw new Error('Invalid design data structure received from server');
        }

        const designData = result.design_data;
        const metadata = designData.metadata || {};
        const elements = designData.elements;

        // 2. Populate Agents with Real Data
        // Step 1: Intent
        agentRef.current?.updateStep(1, {
          status: 'completed',
          result: `Type: ${metadata.building_type || 'Residential'}, Bedrooms: ${metadata.bedroom_count || 'N/A'}`
        });

        // Step 2: Requirements
        const totalArea = metadata.total_area || 'N/A';
        const roomCount = elements.rooms ? elements.rooms.length : 0;
        agentRef.current?.updateStep(2, {
          status: 'completed',
          result: `Area: ${totalArea}, Rooms: ${roomCount}`
        });

        // Step 3: Rules
        agentRef.current?.updateStep(3, {
          status: 'completed',
          result: 'Dimensions & codes validated'
        });

        // Step 4: Layout
        agentRef.current?.updateStep(4, {
          status: 'completed',
          result: 'Layout optimized'
        });

        // Complete flow
        agentRef.current?.completeAll();

        setProjectInfo({
          id: result.project_id,
          designData: designData,
          buildingType: metadata.building_type || 'N/A',
          totalArea: metadata.total_area || 'N/A'
        });

        // Render on canvas after animation completes
        setTimeout(() => {
          canvasRef.current?.renderDesign(designData);
          saveState();

          const editorSection = document.getElementById('editorSection');
          if (editorSection) {
            editorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }

          showStatus('Design generated successfully!', 'success');
        }, 3500); // Wait for agent animations

      } else {
        throw new Error(result.message || 'Generation failed');
      }
    } catch (error) {
      showStatus(`Error: ${error.message}`, 'error');
      agentRef.current?.reset();
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectionChange = (obj) => {
    setSelectedObject(obj);
  };

  const handleObjectModified = () => {
    saveState();
  };

  const handleUpdateProperty = (key, value) => {
    const canvas = canvasRef.current?.getRef();
    const active = canvas?.getActiveObject();
    if (active) {
      console.log(`✏️ Updating property ${key} =`, value);

      // Update fabric object
      if (key === 'strokeWidth') active.set('strokeWidth', value);
      if (key === 'width') active.set('width', value);
      if (key === 'text') active.set('text', value);
      if (key === 'fontSize') active.set('fontSize', value);

      canvas.requestRenderAll();
      saveState();
    }
  };

  // Toolbar Actions
  const handleDelete = () => {
    console.log('🗑️ Delete action');
    canvasRef.current?.deleteSelected();
    saveState();
  };

  const handleZoomIn = () => {
    console.log('🔍 Zoom in');
    canvasRef.current?.zoomIn();
  };

  const handleZoomOut = () => {
    console.log('🔍 Zoom out');
    canvasRef.current?.zoomOut();
  };

  const handleFit = () => {
    console.log('🎯 Fit to view');
    canvasRef.current?.fitToView();
  };

  const handleUndo = () => {
    if (undoStack.current.length > 1) {
      console.log('↩️ Undo');
      const current = undoStack.current.pop();
      redoStack.current.push(current);
      const prev = undoStack.current[undoStack.current.length - 1];
      canvasRef.current?.loadFromJSON(prev);
    }
  };

  const handleRedo = () => {
    if (redoStack.current.length > 0) {
      console.log('↪️ Redo');
      const next = redoStack.current.pop();
      undoStack.current.push(next);
      canvasRef.current?.loadFromJSON(next);
    }
  };

  const saveState = () => {
    const json = canvasRef.current?.toJSON();
    if (json) {
      undoStack.current.push(json);
      redoStack.current = [];
      if (undoStack.current.length > 50) undoStack.current.shift();
      console.log('💾 State saved, history size:', undoStack.current.length);
    }
  };

  const handleDownload = async (format) => {
    if (!projectInfo) {
      showStatus('No project to save', 'error');
      return;
    }

    try {
      console.log(`💾 Downloading ${format.toUpperCase()}...`);
      showStatus(`Converting to ${format.toUpperCase()}...`, 'info');
      setShowSaveMenu(false);

      // Sync canvas state to design data
      const canvas = canvasRef.current?.getRef();
      const updatedDesignData = updateDesignDataFromCanvas(projectInfo.designData, canvas);

      if (updatedDesignData) {
        console.log('📤 Updating project on server...');
        setProjectInfo(prev => ({ ...prev, designData: updatedDesignData }));
        await updateDesign(projectInfo.id, updatedDesignData);
      }

      console.log('⬇️ Downloading file...');
      await downloadFile(projectInfo.id, format);
      showStatus(`Downloaded ${format.toUpperCase()} successfully!`, 'success');

    } catch (error) {
      console.error('❌ Save error:', error);
      showStatus(`Save failed: ${error.message}`, 'error');
    }
  };

  // Close save menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showSaveMenu && !event.target.closest('.save-dropdown')) {
        setShowSaveMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showSaveMenu]);

  return (
    <div className="container">
      <Header />
      <InputSection onGenerate={handleGenerate} isGenerating={isGenerating} />
      <AgentProgress ref={agentRef} />

      <StatusMessage
        message={status.message}
        type={status.type}
        onClose={() => setStatus({ message: '', type: '' })}
      />

      {projectInfo && (
        <section id="editorSection" className="editor-section" style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="save-dropdown" style={{ display: 'inline-block' }}>
            <button
              className="btn-success"
              onClick={() => setShowSaveMenu(!showSaveMenu)}
              style={{ fontSize: '1.2rem', padding: '1rem 2rem' }}
            >
              💾 Save Design ▼
            </button>
            {showSaveMenu && (
              <div className="save-menu show" style={{ textAlign: 'left', minWidth: '300px' }}>
                <div className="save-menu-header">Select format to download:</div>
                <button className="save-option" onClick={() => handleDownload('lsp')}>
                  <span className="format-icon">📄</span>
                  <span>AutoLISP Script (.lsp)</span>
                </button>
                <button className="save-option" onClick={() => handleDownload('dxf')}>
                  <span className="format-icon">📐</span>
                  <span>DXF Drawing (.dxf)</span>
                </button>
              </div>
            )}
          </div>
          <p style={{ marginTop: '1rem', color: '#64748b' }}>
            Design generated successfully. Select a format to download.
          </p>
        </section>
      )}
    </div>
  );
}

export default App;
