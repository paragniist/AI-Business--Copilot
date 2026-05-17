'use client';

import { useState, useCallback } from 'react';
import { Message } from '@/lib/types';
import { analyzeQuery, getHistory } from '@/lib/api';
import { useAuth } from './useAuth';

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  currentQuery: string;
  setCurrentQuery: (query: string) => void;
  sendQuery: (query: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  clearMessages: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const { user } = useAuth();

  const loadHistory = useCallback(async () => {
    if (!user) return;
    try {
      const token = await getAuthToken();
      if (!token) return;
      const response = await getHistory(token);
      if (response.success && Array.isArray(response.data)) {
        const historyMessages = response.data.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp || Date.now()),
        }));
        setMessages(historyMessages);
      }
    } catch (error) {
      console.error('[v0] Failed to load history:', error);
    }
  }, [user]);

  const sendQuery = useCallback(
    async (query: string) => {
      if (!user || !query.trim()) return;

      setIsLoading(true);
      try {
        const token = await getAuthToken();
        if (!token) {
          console.error('[v0] No auth token available');
          return;
        }

        // Add user message
        const userMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'user',
          content: query,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setCurrentQuery('');

        // Get AI response
        const response = await analyzeQuery(query, token);

        if (response.success) {
          // ── Dashboard response ─────────────────────────────
          if (response.isDashboard) {
            const dashboardMessage: Message = {
              id: `msg-${Date.now()}-dashboard`,
              role: 'assistant',
              content: 'Dashboard generated from your documents',
              intent: 'dashboard',
              timestamp: new Date(),
              dashboardCode: response.dashboardCode,
              dashboardTitle: response.dashboardTitle || 'Business Dashboard',
            };
            setMessages((prev) => [...prev, dashboardMessage]);

          // ── Text response ──────────────────────────────────
          } else {
            const assistantMessage: Message = {
              id: `msg-${Date.now()}-response`,
              role: 'assistant',
              content: response.data?.response || 'No response',
              intent: response.intent as any,
              timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
          }

        } else {
          const errorMessage: Message = {
            id: `msg-${Date.now()}-error`,
            role: 'assistant',
            content: `Error: ${response.error || 'Failed to process query'}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      } catch (error) {
        console.error('[v0] Error sending query:', error);
        const errorMessage: Message = {
          id: `msg-${Date.now()}-error`,
          role: 'assistant',
          content: 'An unexpected error occurred',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [user]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentQuery('');
  }, []);

  return {
    messages,
    isLoading,
    currentQuery,
    setCurrentQuery,
    sendQuery,
    loadHistory,
    clearMessages,
  };
}

async function getAuthToken(): Promise<string | null> {
  try {
    const { createClient } = await import('@/lib/supabase');
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (error) {
    console.error('[v0] Failed to get auth token:', error);
    return null;
  }
}