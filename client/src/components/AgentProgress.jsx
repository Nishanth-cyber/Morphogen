import React, { useEffect, useState, useImperativeHandle, forwardRef } from 'react';

const AgentProgress = forwardRef((props, ref) => {
    const [steps, setSteps] = useState([
        { id: 1, name: 'Intent Agent', desc: 'Understanding intent...', status: 'pending', result: '' },
        { id: 2, name: 'Requirement Agent', desc: 'Expanding requirements...', status: 'pending', result: '' },
        { id: 3, name: 'Rules Agent', desc: 'Applying rules...', status: 'pending', result: '' },
        { id: 4, name: 'Layout Agent', desc: 'Creating layout...', status: 'pending', result: '' }
    ]);
    const [visible, setVisible] = useState(false);

    useImperativeHandle(ref, () => ({
        startSimulation: () => {
            setVisible(true);
            setSteps(prev => prev.map((s, i) => ({
                ...s,
                status: i === 0 ? 'active' : 'pending',
                result: ''
            })));
        },
        updateStep: (id, data) => {
            setSteps(prev => prev.map(s =>
                s.id === id ? { ...s, ...data } : s
            ));
        },
        completeAll: () => {
            setSteps(prev => prev.map(s => ({ ...s, status: 'completed' })));
            setTimeout(() => setVisible(false), 4000); // Keep visible longer to read results
        },
        reset: () => {
            setVisible(false);
            setSteps(prev => prev.map(s => ({ ...s, status: 'pending', result: '' })));
        }
    }));

    if (!visible) return null;

    return (
        <div className="agent-progress">
            <h3>Authentication & Design Agents</h3>
            <div className="agent-flow">
                {steps.map((step, index) => (
                    <React.Fragment key={step.id}>
                        <div className={`agent-step ${step.status}`}>
                            <div className="agent-icon">
                                <span className="agent-number">{step.id}</span>
                                {step.status === 'active' && <div className="agent-spinner"></div>}
                            </div>
                            <div className="agent-info">
                                <h4>{step.name}</h4>
                                <p>{step.desc}</p>
                                {step.result && (
                                    <div className="agent-result">
                                        ✓ {step.result}
                                    </div>
                                )}
                            </div>
                        </div>
                        {index < steps.length - 1 && <div className="flow-arrow">→</div>}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
});

AgentProgress.displayName = 'AgentProgress';

export default AgentProgress;
