import { API_BASE_URL } from '../utils/constants';

export const generateDesign = async (prompt) => {
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

    return await response.json();
};

export const updateDesign = async (projectId, designData) => {
    const response = await fetch(`${API_BASE_URL}/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            project_id: projectId,
            design_data: designData
        })
    });

    if (!response.ok) {
        throw new Error(`Update failed: ${response.status}`);
    }

    return await response.json();
};

export const downloadFile = async (projectId, format) => {
    const response = await fetch(`${API_BASE_URL}/download/${projectId}/${format}`);

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

    a.download = filenames[format] || `download.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};
