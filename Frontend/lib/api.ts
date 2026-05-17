import { ApiResponse, Message } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  console.warn('[v0] NEXT_PUBLIC_API_URL environment variable is not set');
}

// ── Generic JSON request helper ───────────────────────────────
async function makeRequest<T = any>(
  endpoint: string,
  options: RequestInit & { token?: string } = {}
): Promise<ApiResponse<T>> {
  const { token, ...fetchOptions } = options;

  const headers = new Headers(fetchOptions.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  headers.set('Content-Type', 'application/json');

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: `API error: ${response.status} - ${errorText}` };
    }

    const data = await response.json();
    return { success: true, data, intent: data.intent };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// ── Analyze query ─────────────────────────────────────────────
export async function analyzeQuery(
  query: string,
  token: string
): Promise<ApiResponse<{ response: string; intent?: string; type?: string; dashboard_code?: string }>> {
  const res = await makeRequest('/analyze', {
    token,
    method: 'POST',
    body: JSON.stringify({ query }),
  });

  // Handle dashboard response
  if (res.success && res.data?.type === 'dashboard') {
    return {
      ...res,
      isDashboard: true,
      dashboardCode: res.data.dashboard_code,
      dashboardTitle: res.data.title,
    };
  }

  return res;
}

// ── Get history ───────────────────────────────────────────────
export async function getHistory(
  token: string
): Promise<ApiResponse<Message[]>> {
  return makeRequest('/history', {
    token,
    method: 'GET',
  });
}

// ── Upload PDF ────────────────────────────────────────────────
export async function uploadPDF(
  file: File,
  token: string
): Promise<ApiResponse<{ file_id: string; name: string }>> {
  if (!file.type.includes('pdf')) {
    return { success: false, error: 'Only PDF files are supported' };
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_URL}/ingest`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: `Upload failed: ${response.status} - ${errorText}` };
    }

    const data = await response.json();
    return {
      success: true,
      data: {
        file_id: data.filename || file.name,
        name: data.filename || file.name,
      },
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Upload failed',
    };
  }
}