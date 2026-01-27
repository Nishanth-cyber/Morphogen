import React, { useEffect, useState } from 'react';

const PropertyPanel = ({ selectedObject, onUpdateProperty }) => {
    const [properties, setProperties] = useState(null);

    useEffect(() => {
        if (selectedObject) {
            setProperties({
                type: selectedObject.objectType || 'Unknown',
                id: selectedObject.id || 'N/A',
                // Flatten properties for easier form handling
                strokeWidth: selectedObject.strokeWidth || 0,
                width: selectedObject.width || 0,
                text: selectedObject.text || '',
                fontSize: selectedObject.fontSize || 16
            });
        } else {
            setProperties(null);
        }
    }, [selectedObject]);

    const handleChange = (key, value) => {
        // Optimistic update local state
        setProperties(prev => ({ ...prev, [key]: value }));
        // Propagate to parent
        onUpdateProperty(key, value);
    };

    if (!selectedObject || !properties) {
        return (
            <div className="property-panel">
                <h3>Properties</h3>
                <div id="propertyContent">
                    <p className="hint">Select an element to view properties</p>
                </div>
            </div>
        );
    }

    return (
        <div className="property-panel">
            <h3>Properties</h3>
            <div id="propertyContent">
                <div className="property-item">
                    <label>Type:</label>
                    <input type="text" value={properties.type} disabled />
                </div>
                <div className="property-item">
                    <label>ID:</label>
                    <input type="text" value={properties.id} disabled />
                </div>

                {properties.type === 'wall' && (
                    <div className="property-item">
                        <label>Thickness (px):</label>
                        <input
                            type="number"
                            value={properties.strokeWidth}
                            min="1"
                            max="10"
                            onChange={(e) => handleChange('strokeWidth', parseInt(e.target.value))}
                        />
                    </div>
                )}

                {(properties.type === 'door' || properties.type === 'window') && (
                    <div className="property-item">
                        <label>Width (px):</label>
                        <input
                            type="number"
                            value={properties.width}
                            min="10"
                            max="200"
                            onChange={(e) => handleChange('width', parseInt(e.target.value))}
                        />
                    </div>
                )}

                {properties.type === 'label' && (
                    <>
                        <div className="property-item">
                            <label>Text:</label>
                            <input
                                type="text"
                                value={properties.text}
                                onChange={(e) => handleChange('text', e.target.value)}
                            />
                        </div>
                        <div className="property-item">
                            <label>Font Size:</label>
                            <input
                                type="number"
                                value={properties.fontSize}
                                min="8"
                                max="48"
                                onChange={(e) => handleChange('fontSize', parseInt(e.target.value))}
                            />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default PropertyPanel;
