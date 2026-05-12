export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: 'analysis' | 'lookup' | 'summarize' | 'dashboard' | 'other';
  timestamp: Date;
  chat_id?: string;
  dashboardCode?: string;    // ← NEW
  dashboardTitle?: string;   // ← NEW
}

export interface Document {
  id: string;
  name: string;
  url?: string;
  size: number;
  uploaded_at: Date;
  user_id: string;
}

export interface Chat {
  id: string;
  user_id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  intent?: string;
  isDashboard?: boolean;      // ← NEW
  dashboardCode?: string;     // ← NEW
  dashboardTitle?: string;    // ← NEW
}