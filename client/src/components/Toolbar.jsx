import React from 'react';

const Toolbar = ({
    onDelete,
    onUndo,
    onRedo,
    onZoomIn,
    onZoomOut,
    onFit,
    showGrid,
    snapToGrid,
    onToggleGrid,
    onToggleSnap
}) => {
    return (
        <div className="toolbar">
            <button className="tool-btn" onClick={onDelete} title="Delete Selected">🗑️ Delete</button>
            <button className="tool-btn" onClick={onUndo} title="Undo">↶ Undo</button>
            <button className="tool-btn" onClick={onRedo} title="Redo">↷ Redo</button>
            <div className="separator"></div>
            <button className="tool-btn" onClick={onZoomIn} title="Zoom In">🔍+ Zoom In</button>
            <button className="tool-btn" onClick={onZoomOut} title="Zoom Out">🔍- Zoom Out</button>
            <button className="tool-btn" onClick={onFit} title="Fit to View">⛶ Fit</button>
            <div className="separator"></div>
            <label className="tool-label">
                <input
                    type="checkbox"
                    checked={snapToGrid}
                    onChange={(e) => onToggleSnap(e.target.checked)}
                />
                Snap to Grid
            </label>
            <label className="tool-label">
                <input
                    type="checkbox"
                    checked={showGrid}
                    onChange={(e) => onToggleGrid(e.target.checked)}
                />
                Show Grid
            </label>
        </div>
    );
};

export default Toolbar;
