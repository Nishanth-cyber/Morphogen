import React from 'react';
import { Zap, Settings, Info } from 'lucide-react';

interface Props {
  onShowInfo?: () => void;
  onShowSettings?: () => void;
}

export const Header: React.FC<Props> = ({ onShowInfo, onShowSettings }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Zap size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Morphogen</h1>
            <p className="text-xs text-gray-600">
              AI-Powered Design Generation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onShowInfo}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="About Morphogen"
          >
            <Info size={20} />
          </button>
          
          <button
            onClick={onShowSettings}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings size={20} />
          </button>
        </div>
      </div>
    </header>
  );
};
