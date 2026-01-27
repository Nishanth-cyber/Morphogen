// Configuration
const API_BASE_URL = 'http://localhost:8000';
const SCALE_FACTOR = 0.08; // 1mm = 0.08px for display
const GRID_SIZE = 50; // pixels

// Global state
let fabricCanvas = null;
let currentProjectId = null;
let currentDesignData = null;
let undoStack = [];
let redoStack = [];
let snapEnabled = true;
let gridVisible = true;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initializeCanvas();
    attachEventListeners();
    console.log('Generative Design Studio initialized');
});

// Initialize Fabric.js canvas
function initializeCanvas() {
    const canvasElement = document.getElementById('designCanvas');
    
    fabricCanvas = new fabric.Canvas(canvasElement, {
        width: 1000,
        height: 800,
        backgroundColor: '#ffffff',
        selection: true
    });
    
    // Draw grid
    drawGrid();
    
    // Canvas event listeners
    fabricCanvas.on('object:modified', handleObjectModified);
    fabricCanvas.on('selection:created', handleSelection);
    fabricCanvas.on('selection:updated', handleSelection);
    fabricCanvas.on('selection:cleared', handleSelectionCleared);
    fabricCanvas.on('object:moving', handleObjectMoving);
}

// Draw grid on canvas
function drawGrid() {
    if (!gridVisible) {
        return;
    }
    
    const width = fabricCanvas.getWidth();
    const height = fabricCanvas.getHeight();
    
    // Vertical lines
    for (let i = 0; i < width / GRID_SIZE; i++) {
        const line = new fabric.Line([i * GRID_SIZE, 0, i * GRID_SIZE, height], {
            stroke: '#e0e0e0',
            strokeWidth: 1,
            selectable: false,
            evented: false,
            excludeFromExport: true
        });
        fabricCanvas.add(line);
        fabricCanvas.sendToBack(line);
    }
    
    // Horizontal lines
    for (let i = 0; i < height / GRID_SIZE; i++) {
        const line = new fabric.Line([0, i * GRID_SIZE, width, i * GRID_SIZE], {
            stroke: '#e0e0e0',
            strokeWidth: 1,
            selectable: false,
            evented: false,
            excludeFromExport: true
        });
        fabricCanvas.add(line);
        fabricCanvas.sendToBack(line);
    }
}

// Attach event listeners
function attachEventListeners() {
    // Generate button
    document.getElementById('generateBtn').addEventListener('click', handleGenerate);
    
    // Save button
    document.getElementById('saveBtn').addEventListener('click', handleSave);
    
    // Export button and menu
    document.getElementById('exportBtn').addEventListener('click', toggleExportMenu);
    document.querySelectorAll('[data-format]').forEach(btn => {
        btn.addEventListener('click', (e) => handleExport(e.target.dataset.format));
    });
    
    // Toolbar buttons
    document.getElementById('deleteBtn').addEventListener('click', deleteSelected);
    document.getElementById('undoBtn').addEventListener('click', undo);
    document.getElementById('redoBtn').addEventListener('click', redo);
    document.getElementById('zoomInBtn').addEventListener('click', zoomIn);
    document.getElementById('zoomOutBtn').addEventListener('click', zoomOut);
    document.getElementById('fitBtn').addEventListener('click', fitToView);
    
    // Checkboxes
    document.getElementById('snapToGrid').addEventListener('change', (e) => {
        snapEnabled = e.target.checked;
    });
    
    document.getElementById('showGrid').addEventListener('change', (e) => {
        gridVisible = e.target.checked;
        fabricCanvas.clear();
        if (gridVisible) drawGrid();
        if (currentDesignData) renderDesign(currentDesignData);
    });
    
    // Close export menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.export-dropdown')) {
            document.getElementById('exportMenu').classList.remove('show');
        }
    });
}

// Handle generate button click
async function handleGenerate() {
    const prompt = document.getElementById('prompt').value.trim();
    
    if (!prompt) {
        showStatus('Please enter a building description', 'error');
        return;
    }
    
    const btn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    // Show loading state
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    showStatus('Generating design... This may take 30-60 seconds', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            currentProjectId = result.project_id;
            currentDesignData = result.design_data;
            
            // Show editor section
            document.getElementById('editorSection').style.display = 'block';
            document.getElementById('projectInfo').style.display = 'block';
            
            // Update project info
            document.getElementById('projectId').textContent = currentProjectId;
            document.getElementById('buildingType').textContent = 
                currentDesignData.metadata.building_type || 'N/A';
            document.getElementById('totalArea').textContent = 
                currentDesignData.metadata.total_area || 'N/A';
            
            // Render design on canvas
            renderDesign(currentDesignData);
            
            // Save initial state
            saveState();
            
            showStatus('Design generated successfully!', 'success');
            
            // Scroll to editor
            document.getElementById('editorSection').scrollIntoView({ 
                behavior: 'smooth' 
            });
        } else {
            throw new Error(result.error || 'Generation failed');
        }
        
    } catch (error) {
        console.error('Generation error:', error);
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        // Reset button state
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Render design on canvas
function renderDesign(designData) {
    // Clear canvas (keep grid)
    const objects = fabricCanvas.getObjects();
    objects.forEach(obj => {
        if (!obj.excludeFromExport) {
            fabricCanvas.remove(obj);
        }
    });
    
    const elements = designData.elements;
    
    // Draw external boundary
    if (elements.external_boundary) {
        const points = elements.external_boundary.points.map(p => ({
            x: p[0] * SCALE_FACTOR,
            y: p[1] * SCALE_FACTOR
        }));
        
        const boundary = new fabric.Polyline(points, {
            stroke: '#000000',
            strokeWidth: 3,
            fill: 'transparent',
            selectable: false,
            evented: false,
            objectType: 'boundary'
        });
        
        fabricCanvas.add(boundary);
    }
    
    // Draw walls
    if (elements.walls) {
        elements.walls.forEach((wall, index) => {
            const line = new fabric.Line([
                wall.start[0] * SCALE_FACTOR,
                wall.start[1] * SCALE_FACTOR,
                wall.end[0] * SCALE_FACTOR,
                wall.end[1] * SCALE_FACTOR
            ], {
                stroke: '#000000',
                strokeWidth: wall.thickness * SCALE_FACTOR || 2,
                selectable: true,
                hasControls: true,
                hasBorders: true,
                objectType: 'wall',
                id: wall.id || `wall_${index}`,
                wallData: wall
            });
            
            fabricCanvas.add(line);
        });
    }
    
    // Draw doors
    if (elements.doors) {
        elements.doors.forEach((door, index) => {
            const rect = new fabric.Rect({
                left: door.position[0] * SCALE_FACTOR,
                top: door.position[1] * SCALE_FACTOR,
                width: door.width * SCALE_FACTOR,
                height: 20,
                fill: '#0066cc',
                stroke: '#004499',
                strokeWidth: 2,
                selectable: true,
                objectType: 'door',
                id: door.id || `door_${index}`,
                doorData: door
            });
            
            fabricCanvas.add(rect);
        });
    }
    
    // Draw windows
    if (elements.windows) {
        elements.windows.forEach((window, index) => {
            const rect = new fabric.Rect({
                left: window.position[0] * SCALE_FACTOR,
                top: window.position[1] * SCALE_FACTOR,
                width: window.width * SCALE_FACTOR,
                height: 15,
                fill: '#66ccff',
                stroke: '#3399cc',
                strokeWidth: 2,
                selectable: true,
                objectType: 'window',
                id: window.id || `window_${index}`,
                windowData: window
            });
            
            fabricCanvas.add(rect);
        });
    }
    
    // Draw room labels and boundaries
    if (elements.rooms) {
        elements.rooms.forEach((room, index) => {
            // Room boundary (dashed rectangle)
            const roomRect = new fabric.Rect({
                left: room.bounds.x * SCALE_FACTOR,
                top: room.bounds.y * SCALE_FACTOR,
                width: room.bounds.width * SCALE_FACTOR,
                height: room.bounds.height * SCALE_FACTOR,
                stroke: '#cccccc',
                strokeWidth: 1,
                strokeDashArray: [5, 5],
                fill: 'transparent',
                selectable: false,
                evented: false,
                objectType: 'roomBoundary'
            });
            
            fabricCanvas.add(roomRect);
            
            // Room label
            const text = new fabric.Text(room.name, {
                left: room.label_position[0] * SCALE_FACTOR,
                top: room.label_position[1] * SCALE_FACTOR,
                fontSize: 16,
                fill: '#333333',
                fontFamily: 'Arial',
                originX: 'center',
                originY: 'center',
                selectable: true,
                objectType: 'label',
                id: room.id || `room_${index}`,
                roomData: room
            });
            
            fabricCanvas.add(text);
            
            // Room area label
            if (room.area) {
                const areaText = new fabric.Text(`${room.area} sq.ft`, {
                    left: room.label_position[0] * SCALE_FACTOR,
                    top: (room.label_position[1] + 500) * SCALE_FACTOR,
                    fontSize: 12,
                    fill: '#666666',
                    fontFamily: 'Arial',
                    originX: 'center',
                    originY: 'center',
                    selectable: false,
                    evented: false,
                    objectType: 'areaLabel'
                });
                
                fabricCanvas.add(areaText);
            }
        });
    }
    
    fabricCanvas.renderAll();
    fitToView();
}

// Handle object modification
function handleObjectModified(e) {
    saveState();
    updateDesignDataFromCanvas();
}

// Handle object moving (with snap to grid)
function handleObjectMoving(e) {
    if (!snapEnabled) return;
    
    const obj = e.target;
    
    obj.set({
        left: Math.round(obj.left / GRID_SIZE) * GRID_SIZE,
        top: Math.round(obj.top / GRID_SIZE) * GRID_SIZE
    });
}

// Handle selection
function handleSelection(e) {
    const selected = fabricCanvas.getActiveObject();
    if (!selected) return;
    
    showProperties(selected);
}

// Handle selection cleared
function handleSelectionCleared() {
    const propertyContent = document.getElementById('propertyContent');
    propertyContent.innerHTML = '<p class="hint">Select an element to view properties</p>';
}

// Show properties panel
function showProperties(obj) {
    const propertyContent = document.getElementById('propertyContent');
    
    let html = `
        <div class="property-item">
            <label>Type:</label>
            <input type="text" value="${obj.objectType || 'Unknown'}" disabled>
        </div>
        <div class="property-item">
            <label>ID:</label>
            <input type="text" value="${obj.id || 'N/A'}" disabled>
        </div>
    `;
    
    // Type-specific properties
    if (obj.objectType === 'wall') {
        html += `
            <div class="property-item">
                <label>Thickness (px):</label>
                <input type="number" id="wallThickness" value="${obj.strokeWidth}" min="1" max="10">
            </div>
        `;
    } else if (obj.objectType === 'door' || obj.objectType === 'window') {
        html += `
            <div class="property-item">
                <label>Width (px):</label>
                <input type="number" id="elementWidth" value="${obj.width}" min="10" max="200">
            </div>
        `;
    } else if (obj.objectType === 'label') {
        html += `
            <div class="property-item">
                <label>Text:</label>
                <input type="text" id="labelText" value="${obj.text}">
            </div>
            <div class="property-item">
                <label>Font Size:</label>
                <input type="number" id="fontSize" value="${obj.fontSize}" min="8" max="48">
            </div>
        `;
    }
    
    propertyContent.innerHTML = html;
    
    // Attach property change listeners
    const wallThickness = document.getElementById('wallThickness');
    if (wallThickness) {
        wallThickness.addEventListener('change', (e) => {
            obj.set('strokeWidth', parseInt(e.target.value));
            fabricCanvas.renderAll();
            saveState();
        });
    }
    
    const elementWidth = document.getElementById('elementWidth');
    if (elementWidth) {
        elementWidth.addEventListener('change', (e) => {
            obj.set('width', parseInt(e.target.value));
            fabricCanvas.renderAll();
            saveState();
        });
    }
    
    const labelText = document.getElementById('labelText');
    if (labelText) {
        labelText.addEventListener('change', (e) => {
            obj.set('text', e.target.value);
            fabricCanvas.renderAll();
            saveState();
        });
    }
    
    const fontSize = document.getElementById('fontSize');
    if (fontSize) {
        fontSize.addEventListener('change', (e) => {
            obj.set('fontSize', parseInt(e.target.value));
            fabricCanvas.renderAll();
            saveState();
        });
    }
}

// Update design data from canvas changes
function updateDesignDataFromCanvas() {
    if (!currentDesignData) return;
    
    const objects = fabricCanvas.getObjects();
    
    // Update walls
    const walls = objects.filter(obj => obj.objectType === 'wall');
    currentDesignData.elements.walls = walls.map((wall, index) => ({
        id: wall.id || `wall_${index}`,
        type: 'line',
        start: [wall.x1 / SCALE_FACTOR, wall.y1 / SCALE_FACTOR],
        end: [wall.x2 / SCALE_FACTOR, wall.y2 / SCALE_FACTOR],
        layer: 'walls',
        thickness: wall.strokeWidth / SCALE_FACTOR
    }));
    
    // Update doors
    const doors = objects.filter(obj => obj.objectType === 'door');
    currentDesignData.elements.doors = doors.map((door, index) => ({
        id: door.id || `door_${index}`,
        type: 'door',
        position: [door.left / SCALE_FACTOR, door.top / SCALE_FACTOR],
        width: door.width / SCALE_FACTOR,
        orientation: door.doorData?.orientation || 'horizontal',
        layer: 'doors'
    }));
    
    // Update windows
    const windows = objects.filter(obj => obj.objectType === 'window');
    currentDesignData.elements.windows = windows.map((window, index) => ({
        id: window.id || `window_${index}`,
        type: 'window',
        position: [window.left / SCALE_FACTOR, window.top / SCALE_FACTOR],
        width: window.width / SCALE_FACTOR,
        orientation: window.windowData?.orientation || 'horizontal',
        layer: 'windows'
    }));
    
    // Update room labels
    const labels = objects.filter(obj => obj.objectType === 'label');
    currentDesignData.elements.rooms = currentDesignData.elements.rooms.map((room, index) => {
        const label = labels.find(l => l.id === room.id);
        if (label) {
            room.name = label.text;
            room.label_position = [label.left / SCALE_FACTOR, label.top / SCALE_FACTOR];
        }
        return room;
    });
}

// Handle save
async function handleSave() {
    if (!currentProjectId || !currentDesignData) {
        showStatus('No project to save', 'error');
        return;
    }
    
    showStatus('Saving changes...', 'info');
    
    try {
        updateDesignDataFromCanvas();
        
        const response = await fetch(`${API_BASE_URL}/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_id: currentProjectId,
                design_data: currentDesignData
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('✅ Project saved! All files updated (.lsp, .dxf, .dwg)', 'success');
        } else {
            throw new Error(result.error || 'Save failed');
        }
        
    } catch (error) {
        console.error('Save error:', error);
        showStatus(`Save error: ${error.message}`, 'error');
    }
}

// Toggle export menu
function toggleExportMenu(e) {
    e.stopPropagation();
    document.getElementById('exportMenu').classList.toggle('show');
}

// Handle export
async function handleExport(format) {
    if (!currentProjectId) {
        showStatus('No project to export', 'error');
        return;
    }
    
    document.getElementById('exportMenu').classList.remove('show');
    showStatus(`Downloading ${format.toUpperCase()} file...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/download/${currentProjectId}/${format}`);
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        const filenames = {
            'lsp': 'floorplan.lsp',
            'dxf': 'floorplan.dxf',
            'dwg': 'floorplan.dwg',
            'json': 'design.json'
        };
        
        a.download = filenames[format];
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showStatus(`✅ ${format.toUpperCase()} file downloaded successfully!`, 'success');
        
    } catch (error) {
        console.error('Export error:', error);
        showStatus(`Export error: ${error.message}`, 'error');
    }
}

// Toolbar functions
function deleteSelected() {
    const active = fabricCanvas.getActiveObject();
    if (active) {
        fabricCanvas.remove(active);
        saveState();
        updateDesignDataFromCanvas();
    }
}

function saveState() {
    const json = fabricCanvas.toJSON(['objectType', 'id', 'wallData', 'doorData', 'windowData', 'roomData']);
    undoStack.push(JSON.stringify(json));
    redoStack = [];
    
    // Limit undo stack
    if (undoStack.length > 50) {
        undoStack.shift();
    }
}

function undo() {
    if (undoStack.length > 1) {
        redoStack.push(undoStack.pop());
        const state = undoStack[undoStack.length - 1];
        fabricCanvas.loadFromJSON(state, () => {
            fabricCanvas.renderAll();
            updateDesignDataFromCanvas();
        });
    }
}

function redo() {
    if (redoStack.length > 0) {
        const state = redoStack.pop();
        undoStack.push(state);
        fabricCanvas.loadFromJSON(state, () => {
            fabricCanvas.renderAll();
            updateDesignDataFromCanvas();
        });
    }
}

function zoomIn() {
    const zoom = fabricCanvas.getZoom();
    fabricCanvas.setZoom(zoom * 1.1);
}

function zoomOut() {
    const zoom = fabricCanvas.getZoom();
    fabricCanvas.setZoom(zoom * 0.9);
}

function fitToView() {
    const objects = fabricCanvas.getObjects().filter(obj => !obj.excludeFromExport);
    if (objects.length === 0) return;
    
    const group = new fabric.Group(objects);
    const bounds = group.getBoundingRect();
    
    const canvasWidth = fabricCanvas.getWidth();
    const canvasHeight = fabricCanvas.getHeight();
    
    const zoomX = canvasWidth / bounds.width;
    const zoomY = canvasHeight / bounds.height;
    const zoom = Math.min(zoomX, zoomY) * 0.9;
    
    fabricCanvas.setZoom(zoom);
    fabricCanvas.absolutePan({
        x: (canvasWidth - bounds.width * zoom) / 2 - bounds.left * zoom,
        y: (canvasHeight - bounds.height * zoom) / 2 - bounds.top * zoom
    });
    
    // Destroy temporary group
    group.destroy();
    fabricCanvas.renderAll();
}

// Show status message
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message show ${type}`;
    
    setTimeout(() => {
        statusEl.classList.remove('show');
    }, 5000);
}
