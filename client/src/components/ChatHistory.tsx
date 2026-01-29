import React, { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { LoadingIndicator } from './LoadingIndicator';
import type { ChatMessage as ChatMessageType, LoadingState } from '../types';
import { scrollToBottom } from '../utils/helpers';

interface Props {
  messages: ChatMessageType[];
  loadingState: LoadingState;
}

export const ChatHistory: React.FC<Props> = ({ messages, loadingState }) => {
  const chatEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom(containerRef.current);
  }, [messages, loadingState]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-6 space-y-4"
    >
      {messages.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </>
      )}

      {loadingState !== 'idle' && <LoadingIndicator state={loadingState} />}

      <div ref={chatEndRef} />
    </div>
  );
};

const EmptyState: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-full text-center px-4">
    <div className="mb-4">
      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg
          className="w-8 h-8 text-blue-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Welcome to Morphogen
      </h3>
      <p className="text-gray-600 max-w-md">
        AI-powered generative design for engineering projects. Describe what
        you want to build, and I'll help you create it.
      </p>
    </div>

    <div className="bg-gray-50 rounded-xl p-4 max-w-lg">
      <p className="text-sm font-medium text-gray-900 mb-2">
        Try these examples:
      </p>
      <ul className="text-sm text-gray-600 space-y-1 text-left">
        <li>• Generate a piping layout for a 50 MLD desalination plant</li>
        <li>• Create a 2-bedroom house with kitchen and living room</li>
        <li>• Design a warehouse with loading docks</li>
      </ul>
    </div>
  </div>
);
