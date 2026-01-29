import React from 'react';
import { Loader2 } from 'lucide-react';
import type { LoadingState } from '../types';

interface Props {
  state: LoadingState;
}

const loadingMessages: Record<LoadingState, string> = {
  idle: '',
  thinking: 'Analyzing your request...',
  waiting_for_user: 'Waiting for clarification...',
  rendering: 'Generating design...',
  exporting: 'Preparing export...',
};

export const LoadingIndicator: React.FC<Props> = ({ state }) => {
  if (state === 'idle') return null;

  return (
    <div className="flex gap-3 mb-4">
      {/* Assistant Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 text-white flex items-center justify-center">
        <Loader2 size={18} className="animate-spin" />
      </div>

      {/* Loading Message */}
      <div className="flex items-center gap-2 bg-gray-100 rounded-2xl px-4 py-3">
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
        <span className="text-sm text-gray-600 ml-2">
          {loadingMessages[state]}
        </span>
      </div>
    </div>
  );
};
