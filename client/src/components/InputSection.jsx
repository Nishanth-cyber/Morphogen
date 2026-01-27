import React, { useState } from 'react';

const InputSection = ({ onGenerate, isGenerating }) => {
    const [prompt, setPrompt] = useState('');

    const handleGenerate = () => {
        if (!prompt.trim()) return;
        onGenerate(prompt);
    };

    return (
        <section className="input-section">
            <div className="input-box">
                <label htmlFor="prompt">Describe your building:</label>
                <textarea
                    id="prompt"
                    placeholder="Example: Design a 3-bedroom house with open kitchen and attached garage"
                    rows="3"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    disabled={isGenerating}
                ></textarea>
                <button
                    id="generateBtn"
                    className="btn-primary"
                    onClick={handleGenerate}
                    disabled={isGenerating}
                >
                    <span id="btnText" style={{ display: isGenerating ? 'none' : 'inline' }}>
                        Generate Design
                    </span>
                    {isGenerating && <span id="btnLoader" className="loader"></span>}
                </button>
            </div>
        </section>
    );
};

export default InputSection;
