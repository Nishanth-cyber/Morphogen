import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { fabric } from 'fabric';
import { GRID_SIZE, SCALE_FACTOR } from '../utils/constants';

const CanvasEditor = forwardRef(({ onSelectionChange, onObjectModified }, ref) => {
    const canvasRef = useRef(null);
    const fabricRef = useRef(null);
    const gridVisibleRef = useRef(true);
    const snapEnabledRef = useRef(true);

    // Initialize Canvas
    useEffect(() => {
        if (!canvasRef.current) return;

        console.log('🎨 Initializing Fabric Canvas');
        const canvas = new fabric.Canvas(canvasRef.current, {
            width: 1000,
            height: 800,
            backgroundColor: '#ffffff',
            selection: true
        });

        fabricRef.current = canvas;

        // Draw initial grid
        drawGrid();

        // Events
        canvas.on('object:modified', (e) => {
            console.log('✏️ Object modified:', e.target.objectType);
            if (onObjectModified) onObjectModified();
        });

        canvas.on('object:moving', (e) => {
            if (snapEnabledRef.current) {
                const obj = e.target;
                obj.set({
                    left: Math.round(obj.left / GRID_SIZE) * GRID_SIZE,
                    top: Math.round(obj.top / GRID_SIZE) * GRID_SIZE
                });
            }
        });

        const handleSelection = () => {
            const active = canvas.getActiveObject();
            console.log('👆 Selection changed:', active ? active.objectType : 'none');
            if (onSelectionChange) onSelectionChange(active);
        };

        canvas.on('selection:created', handleSelection);
        canvas.on('selection:updated', handleSelection);
        canvas.on('selection:cleared', () => {
            if (onSelectionChange) onSelectionChange(null);
        });

        console.log('✅ Canvas initialized successfully');

        return () => {
            console.log('🧹 Disposing Fabric Canvas');
            canvas.dispose();
            fabricRef.current = null;
        };
    }, []);

    // Helper: Draw Grid
    const drawGrid = () => {
        const canvas = fabricRef.current;
        if (!canvas) return;

        // Clear existing grid lines
        const objects = canvas.getObjects();
        objects.forEach(obj => {
            if (obj.excludeFromExport) {
                canvas.remove(obj);
            }
        });

        if (!gridVisibleRef.current) return;

        const width = canvas.getWidth();
        const height = canvas.getHeight();

        // Vertical lines
        for (let i = 0; i <= width / GRID_SIZE; i++) {
            const line = new fabric.Line([i * GRID_SIZE, 0, i * GRID_SIZE, height], {
                stroke: '#e2e8f0',
                strokeWidth: 1,
                selectable: false,
                evented: false,
                excludeFromExport: true
            });
            canvas.add(line);
            canvas.sendToBack(line);
        }

        // Horizontal lines
        for (let i = 0; i <= height / GRID_SIZE; i++) {
            const line = new fabric.Line([0, i * GRID_SIZE, width, i * GRID_SIZE], {
                stroke: '#e2e8f0',
                strokeWidth: 1,
                selectable: false,
                evented: false,
                excludeFromExport: true
            });
            canvas.add(line);
            canvas.sendToBack(line);
        }

        canvas.requestRenderAll();
    };

    // Expose methods to parent
    useImperativeHandle(ref, () => ({
        renderDesign: (designData) => {
            console.log("🐛 DEBUG: renderDesign called");
            const canvas = fabricRef.current;
            if (!canvas || !designData || !designData.elements) {
                console.error("❌ DEBUG: Invalid canvas or data");
                return;
            }

            // DEBUG: Test Rectangle - Shows if canvas is rendering AT ALL
            const debugRect = new fabric.Rect({
                left: 50, top: 50, width: 100, height: 100,
                fill: 'red', stroke: 'black', strokeWidth: 5,
                objectType: 'debug'
            });
            canvas.add(debugRect);
            console.log("🐛 DEBUG: Added red test rectangle at 50,50");

            // Clear existing objects (keep grid)
            const objects = canvas.getObjects();
            objects.forEach(obj => {
                if (!obj.excludeFromExport) {
                    canvas.remove(obj);
                }
            });

            const elements = designData.elements;

            // Draw external boundary
            if (elements.external_boundary && elements.external_boundary.points) {
                const points = elements.external_boundary.points.map(p => ({
                    x: p[0] * SCALE_FACTOR,
                    y: p[1] * SCALE_FACTOR
                }));

                const boundary = new fabric.Polyline(points, {
                    stroke: '#1e293b',
                    strokeWidth: 3,
                    fill: 'transparent',
                    selectable: false,
                    evented: false,
                    objectType: 'boundary'
                });
                canvas.add(boundary);
            }

            // Draw walls
            if (elements.walls && elements.walls.length > 0) {
                elements.walls.forEach((wall, index) => {
                    const x1 = wall.start[0] * SCALE_FACTOR;
                    const y1 = wall.start[1] * SCALE_FACTOR;
                    const x2 = wall.end[0] * SCALE_FACTOR;
                    const y2 = wall.end[1] * SCALE_FACTOR;

                    const line = new fabric.Line([x1, y1, x2, y2], {
                        stroke: '#1e293b',
                        strokeWidth: (wall.thickness * SCALE_FACTOR) || 2,
                        selectable: true,
                        hasControls: true,
                        hasBorders: true,
                        objectType: 'wall',
                        id: wall.id || `wall_${index}`,
                        wallData: wall
                    });
                    canvas.add(line);
                });
            }

            // Draw doors
            if (elements.doors && elements.doors.length > 0) {
                elements.doors.forEach((door, index) => {
                    const rect = new fabric.Rect({
                        left: door.position[0] * SCALE_FACTOR,
                        top: door.position[1] * SCALE_FACTOR,
                        width: door.width * SCALE_FACTOR,
                        height: 20,
                        fill: '#3b82f6',
                        stroke: '#1e40af',
                        strokeWidth: 2,
                        selectable: true,
                        objectType: 'door',
                        id: door.id || `door_${index}`,
                        doorData: door
                    });
                    canvas.add(rect);
                });
            }

            // Draw windows
            if (elements.windows && elements.windows.length > 0) {
                elements.windows.forEach((window, index) => {
                    const rect = new fabric.Rect({
                        left: window.position[0] * SCALE_FACTOR,
                        top: window.position[1] * SCALE_FACTOR,
                        width: window.width * SCALE_FACTOR,
                        height: 15,
                        fill: '#60a5fa',
                        stroke: '#2563eb',
                        strokeWidth: 2,
                        selectable: true,
                        objectType: 'window',
                        id: window.id || `window_${index}`,
                        windowData: window
                    });
                    canvas.add(rect);
                });
            }

            // Draw room labels
            if (elements.rooms && elements.rooms.length > 0) {
                elements.rooms.forEach((room, index) => {
                    // Room boundary (dashed)
                    if (room.bounds) {
                        const roomRect = new fabric.Rect({
                            left: room.bounds.x * SCALE_FACTOR,
                            top: room.bounds.y * SCALE_FACTOR,
                            width: room.bounds.width * SCALE_FACTOR,
                            height: room.bounds.height * SCALE_FACTOR,
                            stroke: '#94a3b8',
                            strokeWidth: 1,
                            strokeDashArray: [5, 5],
                            fill: 'transparent',
                            selectable: false,
                            evented: false,
                            objectType: 'roomBoundary'
                        });
                        canvas.add(roomRect);
                    }

                    // Room label
                    const text = new fabric.Text(room.name || 'Room', {
                        left: room.label_position[0] * SCALE_FACTOR,
                        top: room.label_position[1] * SCALE_FACTOR,
                        fontSize: 16,
                        fill: '#1e293b',
                        fontFamily: 'Inter, Arial, sans-serif',
                        fontWeight: '600',
                        originX: 'center',
                        originY: 'center',
                        selectable: true,
                        objectType: 'label',
                        id: room.id || `room_${index}`,
                        roomData: room
                    });
                    canvas.add(text);

                    // Area label
                    if (room.area) {
                        const areaText = new fabric.Text(`${room.area} sq.ft`, {
                            left: room.label_position[0] * SCALE_FACTOR,
                            top: (room.label_position[1] + 300) * SCALE_FACTOR,
                            fontSize: 12,
                            fill: '#64748b',
                            fontFamily: 'Inter, Arial, sans-serif',
                            originX: 'center',
                            originY: 'center',
                            selectable: false,
                            evented: false,
                            objectType: 'areaLabel'
                        });
                        canvas.add(areaText);
                    }
                });
            }

            canvas.renderAll();

            // Auto-fit to view
            setTimeout(() => {
                const allObjs = canvas.getObjects().filter(o => !o.excludeFromExport);
                if (allObjs.length > 0) {
                    const group = new fabric.Group(allObjs);
                    const bounds = group.getBoundingRect();

                    const zoomX = canvas.getWidth() / bounds.width;
                    const zoomY = canvas.getHeight() / bounds.height;
                    const zoom = Math.min(zoomX, zoomY, 2) * 0.85; // Limit max zoom to 2x

                    canvas.setZoom(zoom);
                    canvas.absolutePan({
                        x: (canvas.getWidth() - bounds.width * zoom) / 2 - bounds.left * zoom,
                        y: (canvas.getHeight() - bounds.height * zoom) / 2 - bounds.top * zoom
                    });
                    group.destroy();
                    canvas.renderAll();
                }
            }, 100);
        },

        toggleGrid: (visible) => {
            gridVisibleRef.current = visible;
            drawGrid();
        },

        toggleSnap: (enabled) => {
            snapEnabledRef.current = enabled;
        },

        zoomIn: () => {
            const canvas = fabricRef.current;
            if (!canvas) return;
            const newZoom = canvas.getZoom() * 1.1;
            canvas.setZoom(Math.min(newZoom, 5));
            canvas.renderAll();
        },

        zoomOut: () => {
            const canvas = fabricRef.current;
            if (!canvas) return;
            const newZoom = canvas.getZoom() * 0.9;
            canvas.setZoom(Math.max(newZoom, 0.1));
            canvas.renderAll();
        },

        fitToView: () => {
            const canvas = fabricRef.current;
            if (!canvas) return;

            const allObjs = canvas.getObjects().filter(o => !o.excludeFromExport);
            if (allObjs.length === 0) return;

            const group = new fabric.Group(allObjs);
            const bounds = group.getBoundingRect();
            const zoom = Math.min(
                canvas.getWidth() / bounds.width,
                canvas.getHeight() / bounds.height
            ) * 0.85;

            canvas.setZoom(zoom);
            canvas.absolutePan({
                x: (canvas.getWidth() - bounds.width * zoom) / 2 - bounds.left * zoom,
                y: (canvas.getHeight() - bounds.height * zoom) / 2 - bounds.top * zoom
            });
            group.destroy();
            canvas.renderAll();
        },

        deleteSelected: () => {
            const canvas = fabricRef.current;
            if (!canvas) return;
            const active = canvas.getActiveObject();
            if (active) {
                console.log('🗑️ Deleting:', active.objectType);
                canvas.remove(active);
                if (onObjectModified) onObjectModified();
            }
        },

        toJSON: () => {
            const canvas = fabricRef.current;
            if (!canvas) return null;
            return JSON.stringify(
                canvas.toJSON(['objectType', 'id', 'wallData', 'doorData', 'windowData', 'roomData'])
            );
        },

        loadFromJSON: (json) => {
            const canvas = fabricRef.current;
            if (!canvas) return;
            canvas.loadFromJSON(json, () => {
                canvas.renderAll();
                drawGrid();
            });
        },

        getRef: () => fabricRef.current
    }));

    return (
        <div className="canvas-wrapper">
            <canvas ref={canvasRef} id="designCanvas" />
        </div>
    );
});

CanvasEditor.displayName = 'CanvasEditor';

export default CanvasEditor;
