import { SCALE_FACTOR } from './constants';

export const updateDesignDataFromCanvas = (designData, canvas) => {
    if (!designData || !canvas) return null;

    const objects = canvas.getObjects();
    const newDesignData = JSON.parse(JSON.stringify(designData)); // Deep copy

    // Update walls
    const walls = objects.filter(obj => obj.objectType === 'wall');
    newDesignData.elements.walls = walls.map((wall, index) => ({
        id: wall.id || `wall_${index}`,
        type: 'line',
        start: [wall.x1 / SCALE_FACTOR, wall.y1 / SCALE_FACTOR],
        end: [wall.x2 / SCALE_FACTOR, wall.y2 / SCALE_FACTOR],
        layer: 'walls',
        thickness: wall.strokeWidth / SCALE_FACTOR
    }));

    // Update doors
    const doors = objects.filter(obj => obj.objectType === 'door');
    newDesignData.elements.doors = doors.map((door, index) => ({
        id: door.id || `door_${index}`,
        type: 'door',
        position: [door.left / SCALE_FACTOR, door.top / SCALE_FACTOR],
        width: door.width / SCALE_FACTOR,
        orientation: door.doorData?.orientation || 'horizontal',
        layer: 'doors'
    }));

    // Update windows
    const windows = objects.filter(obj => obj.objectType === 'window');
    newDesignData.elements.windows = windows.map((window, index) => ({
        id: window.id || `window_${index}`,
        type: 'window',
        position: [window.left / SCALE_FACTOR, window.top / SCALE_FACTOR],
        width: window.width / SCALE_FACTOR,
        orientation: window.windowData?.orientation || 'horizontal',
        layer: 'windows'
    }));

    // Update room labels
    const labels = objects.filter(obj => obj.objectType === 'label');
    if (newDesignData.elements.rooms) {
        newDesignData.elements.rooms = newDesignData.elements.rooms.map((room) => {
            const label = labels.find(l => l.id === room.id);
            if (label) {
                room.name = label.text;
                room.label_position = [label.left / SCALE_FACTOR, label.top / SCALE_FACTOR];
            }
            return room;
        });
    }

    return newDesignData;
};
