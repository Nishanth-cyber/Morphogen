import axios from 'axios';
import type { GenerateRequest, GenerateResponse, EditRequest } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 3600000, // 1 hour for complex designs
});

export const morphogenAPI = {
  /**
   * Generate a new design from a prompt
   */
  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await api.post<GenerateResponse>('/generate', request);
    return response.data;
  },

  /**
   * Edit existing geometry with a prompt
   */
  async edit(request: EditRequest): Promise<GenerateResponse> {
    const response = await api.post<GenerateResponse>('/edit', request);
    return response.data;
  },

  /**
   * Export design to DXF format
   */
  async exportDXF(geometry: Record<string, any>): Promise<Blob> {
    const response = await api.post('/generate/dxf',
      { geometry },
      { responseType: 'blob' }
    );
    return response.data;
  },

  /**
   * Export design to IFC format
   */
  async exportIFC(geometry: Record<string, any>): Promise<Blob> {
    const response = await api.post('/generate/ifc',
      { geometry },
      { responseType: 'blob' }
    );
    return response.data;
  },

  /**
   * Get system capabilities
   */
  async getCapabilities(): Promise<any> {
    const response = await api.get('/capabilities');
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await axios.get('/health');
    return response.data;
  }
};
