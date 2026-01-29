import React from 'react';
import { FileQuestion, Download, RotateCcw } from 'lucide-react';

interface Props {
  svgContent: string | null;
  onExportDXF?: () => void;
  onExportIFC?: () => void;
  onReset?: () => void;
  isExporting?: boolean;
}

export const SVGPreview: React.FC<Props> = ({
  svgContent,
  onExportDXF,
  onExportIFC,
  onReset,
  isExporting = false,
}) => {
  if (!svgContent) {
    return <EmptyPreview />;
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
        <h3 className="font-medium text-gray-900">Design Preview</h3>
        
        <div className="flex gap-2">
          {onExportDXF && (
            <button
              onClick={onExportDXF}
              disabled={isExporting}
              className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
              title="Export to AutoCAD DXF"
            >
              <Download size={16} />
              Export DXF
            </button>
          )}
          
          {onExportIFC && (
            <button
              onClick={onExportIFC}
              disabled={isExporting}
              className="px-3 py-1.5 text-sm bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
              title="Export to BIM IFC"
            >
              <Download size={16} />
              Export IFC
            </button>
          )}
          
          {onReset && (
            <button
              onClick={onReset}
              className="px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center gap-2 transition-colors"
              title="Reset design"
            >
              <RotateCcw size={16} />
              Reset
            </button>
          )}
        </div>
      </div>

      {/* SVG Display */}
      <div className="flex-1 overflow-auto p-4 flex items-center justify-center">
        <div
          className="bg-white rounded-lg shadow-sm p-4 max-w-full"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      </div>

      {/* Info Bar */}
      <div className="px-4 py-2 bg-white border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Use chat to edit: "Move the pump 5 meters to the right"
        </p>
      </div>
    </div>
  );
};

const EmptyPreview: React.FC = () => (
  <div className="h-full flex flex-col items-center justify-center bg-gray-50 text-center p-8">
    <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mb-4">
      <FileQuestion size={40} className="text-gray-400" />
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      No design yet
    </h3>
    <p className="text-gray-600 max-w-sm">
      Start a conversation to generate your first design. The preview will
      appear here automatically.
    </p>
  </div>
);
