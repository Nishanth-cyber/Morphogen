import React, { useEffect } from 'react';

const StatusMessage = ({ message, type, onClose }) => {
    useEffect(() => {
        if (message) {
            const timer = setTimeout(() => {
                onClose();
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [message, onClose]);

    if (!message) return null;

    return (
        <div className={`status-message ${type}`}>
            <div className="status-content">
                <span className="status-text">{message}</span>
                <button className="status-close" onClick={onClose} aria-label="Close">
                    ×
                </button>
            </div>
        </div>
    );
};

export default StatusMessage;
