import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { ChatHistory } from './components/ChatHistory';
import { ChatInput } from './components/ChatInput';
import { SVGPreview } from './components/SVGPreview';
import { morphogenAPI } from './services/api';
import { createMessage, downloadBlob } from './utils/helpers';
import type { AppState, ChatMessage, GeometryData } from './types';

const initialState: AppState = {
  messages: [],
  currentGeometryJSON: null,
  currentPlan: null,
  svgPreview: null,
  pendingQuestions: [],
  loadingState: 'idle',
  error: null,
};

export const App: React.FC = () => {
  const [state, setState] = useState<AppState>(initialState);

  const addMessage = useCallback((message: ChatMessage) => {
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }));
  }, []);

  const setLoading = useCallback((loadingState: AppState['loadingState']) => {
    setState((prev) => ({ ...prev, loadingState }));
  }, []);

  const handleSendMessage = useCallback(async (content: string) => {
    // Add user message
    const userMessage = createMessage('user', content);
    addMessage(userMessage);

    setLoading('thinking');

    try {
      // Determine if this is an initial prompt or a clarification answer
      const isEdit = state.currentGeometryJSON !== null && !state.pendingQuestions.length;
      
      if (isEdit) {
        // Edit existing design
        const response = await morphogenAPI.edit({
          geometry: state.currentGeometryJSON as any,
          instruction: content,
        });

        if (response.status === 'complete') {
          setState((prev) => ({
            ...prev,
            currentGeometryJSON: response.geometry || null,
            svgPreview: response.artifacts?.svg || null,
            loadingState: 'idle',
          }));

          addMessage(
            createMessage(
              'assistant',
              'Design updated successfully. Check the preview on the right.',
              { hasDesign: true }
            )
          );

          if (response.warnings && response.warnings.length > 0) {
            addMessage({
              ...createMessage('system', 'Validation completed'),
              warnings: response.warnings,
            });
          }
        }
      } else {
        // Generate new design or provide clarification
        const request: any = {
          prompt: content,
        };

        if (state.pendingQuestions.length > 0) {
          request.previous_plan = state.currentPlan;
          request.clarification_answers = { answer: content };
        }

        const response = await morphogenAPI.generate(request);

        if (response.status === 'incomplete') {
          // Need clarification
          setState((prev) => ({
            ...prev,
            pendingQuestions: response.questions || [],
            currentPlan: response.plan || null,
            loadingState: 'waiting_for_user',
          }));

          addMessage({
            ...createMessage(
              'assistant',
              'I need more information to generate your design:'
            ),
            questions: response.questions,
          });
        } else if (response.status === 'complete') {
          // Design complete
          setState((prev) => ({
            ...prev,
            currentGeometryJSON: response.geometry || null,
            currentPlan: response.plan || null,
            svgPreview: response.artifacts?.svg || null,
            pendingQuestions: [],
            loadingState: 'idle',
          }));

          addMessage(
            createMessage(
              'assistant',
              'Design generated successfully! You can view it on the right or request changes.',
              { hasDesign: true }
            )
          );

          if (response.warnings && response.warnings.length > 0) {
            addMessage({
              ...createMessage('system', 'Validation warnings detected'),
              warnings: response.warnings,
            });
          }
        }
      }
    } catch (error: any) {
      console.error('Error:', error);
      setLoading('idle');
      
      addMessage(
        createMessage(
          'assistant',
          `Error: ${error.response?.data?.detail || error.message || 'Something went wrong. Please try again.'}`,
          { isError: true }
        )
      );
    }
  }, [state.currentGeometryJSON, state.pendingQuestions, state.currentPlan, addMessage, setLoading]);

  const handleExportDXF = useCallback(async () => {
    if (!state.currentGeometryJSON) return;

    setLoading('exporting');
    try {
      const blob = await morphogenAPI.exportDXF(state.currentGeometryJSON as any);
      downloadBlob(blob, `design-${Date.now()}.dxf`);
      
      addMessage(
        createMessage('system', 'DXF file downloaded successfully.')
      );
    } catch (error: any) {
      console.error('Export error:', error);
      addMessage(
        createMessage(
          'assistant',
          `Export failed: ${error.message}`,
          { isError: true }
        )
      );
    } finally {
      setLoading('idle');
    }
  }, [state.currentGeometryJSON, addMessage, setLoading]);

  const handleExportIFC = useCallback(async () => {
    if (!state.currentGeometryJSON) return;

    setLoading('exporting');
    try {
      const blob = await morphogenAPI.exportIFC(state.currentGeometryJSON as any);
      downloadBlob(blob, `design-${Date.now()}.ifc`);
      
      addMessage(
        createMessage('system', 'IFC file downloaded successfully.')
      );
    } catch (error: any) {
      console.error('Export error:', error);
      addMessage(
        createMessage(
          'assistant',
          `Export failed: ${error.message}`,
          { isError: true }
        )
      );
    } finally {
      setLoading('idle');
    }
  }, [state.currentGeometryJSON, addMessage, setLoading]);

  const handleReset = useCallback(() => {
    if (confirm('Are you sure you want to start over? This will clear the current design.')) {
      setState(initialState);
      addMessage(
        createMessage('system', 'Conversation reset. Start a new design!')
      );
    }
  }, [addMessage]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header />

      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className="flex-1 flex flex-col bg-white border-r border-gray-200">
          <ChatHistory
            messages={state.messages}
            loadingState={state.loadingState}
          />
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={state.loadingState !== 'idle' && state.loadingState !== 'waiting_for_user'}
          />
        </div>

        {/* Preview Panel */}
        <div className="w-1/2 flex flex-col">
          <SVGPreview
            svgContent={state.svgPreview}
            onExportDXF={handleExportDXF}
            onExportIFC={handleExportIFC}
            onReset={handleReset}
            isExporting={state.loadingState === 'exporting'}
          />
        </div>
      </div>
    </div>
  );
};
