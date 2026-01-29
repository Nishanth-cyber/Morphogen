// API Types
export interface GenerateRequest {
  prompt: string;
  previous_plan?: Record<string, any>;
  clarification_answers?: Record<string, any>;
}

export interface GenerateResponse {
  status: 'incomplete' | 'complete';
  plan?: Record<string, any>;
  geometry?: GeometryData;
  missing_fields?: string[];
  questions?: string[];
  artifacts?: {
    svg?: string;
    dxf?: string;
    ifc?: string;
  };
  warnings?: string[];
}

export interface EditRequest {
  geometry: Record<string, any>;
  instruction: string;
}

export interface GeometryData {
  units: string;
  domain?: string;
  walls?: any[];
  doors?: any[];
  windows?: any[];
  pipes?: any[];
  equipment?: any[];
  valves?: any[];
  process_units?: any[];
  annotations?: any[];
}

// Chat Message Types
export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  questions?: string[];
  warnings?: string[];
  metadata?: {
    isError?: boolean;
    isLoading?: boolean;
    hasDesign?: boolean;
  };
}

// Application State
export type LoadingState = 'idle' | 'thinking' | 'waiting_for_user' | 'rendering' | 'exporting';

export interface AppState {
  messages: ChatMessage[];
  currentGeometryJSON: GeometryData | null;
  currentPlan: Record<string, any> | null;
  svgPreview: string | null;
  pendingQuestions: string[];
  loadingState: LoadingState;
  error: string | null;
}

// Clarification Answer
export interface ClarificationAnswer {
  question: string;
  answer: string;
}
