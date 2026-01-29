import React from 'react';
import { User, Bot, AlertCircle, CheckCircle2 } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../types';
import { formatTime } from '../utils/helpers';

interface Props {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const isError = message.metadata?.isError;

  return (
    <div
      className={`flex gap-3 mb-4 ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-blue-500 text-white'
            : isSystem
            ? 'bg-yellow-500 text-white'
            : 'bg-gray-700 text-white'
        }`}
      >
        {isUser ? (
          <User size={18} />
        ) : isSystem ? (
          <AlertCircle size={18} />
        ) : (
          <Bot size={18} />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`flex flex-col max-w-[70%] ${
          isUser ? 'items-end' : 'items-start'
        }`}
      >
        {/* Message Bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-500 text-white'
              : isError
              ? 'bg-red-50 text-red-900 border border-red-200'
              : isSystem
              ? 'bg-yellow-50 text-yellow-900 border border-yellow-200'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>

          {/* Questions Section */}
          {message.questions && message.questions.length > 0 && (
            <div className="mt-3 space-y-2">
              <p className="text-xs font-medium opacity-75">
                Please provide:
              </p>
              {message.questions.map((question, idx) => (
                <div
                  key={idx}
                  className="text-sm bg-white bg-opacity-50 rounded-lg px-3 py-2"
                >
                  {idx + 1}. {question}
                </div>
              ))}
            </div>
          )}

          {/* Warnings Section */}
          {message.warnings && message.warnings.length > 0 && (
            <div className="mt-3 space-y-1">
              <p className="text-xs font-medium opacity-75 flex items-center gap-1">
                <AlertCircle size={12} />
                Validation Warnings:
              </p>
              {message.warnings.map((warning, idx) => (
                <div
                  key={idx}
                  className="text-xs bg-white bg-opacity-50 rounded px-2 py-1"
                >
                  • {warning}
                </div>
              ))}
            </div>
          )}

          {/* Success Indicator */}
          {message.metadata?.hasDesign && (
            <div className="mt-2 flex items-center gap-1 text-xs opacity-75">
              <CheckCircle2 size={12} />
              <span>Design generated successfully</span>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-500 mt-1 px-2">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
};
