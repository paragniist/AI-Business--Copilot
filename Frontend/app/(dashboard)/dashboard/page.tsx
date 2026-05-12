'use client';
import { useEffect, useRef, useState } from 'react';
import { ChatMessage } from '@/components/chat/chat-message';
import { ChatInput } from '@/components/chat/chat-input';
import { EmptyState } from '@/components/chat/empty-state';
import { LoadingSpinner } from '@/components/chat/loading-spinner';
import { useChat } from '@/hooks/useChat';
import { Message } from '@/lib/types';

export default function DashboardPage() {
  const {
    messages,
    isLoading,
    currentQuery,
    setCurrentQuery,
    sendQuery,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-2">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-slate-800/80 border border-slate-700/50 rounded-2xl px-5 py-4">
                  <LoadingSpinner />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-800 bg-slate-950/50 backdrop-blur-sm p-4">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSend={sendQuery}
            isLoading={isLoading}
            value={currentQuery}
            onChange={setCurrentQuery}
          />
          <p className="text-xs text-slate-500 text-center mt-2">
            AI Business Copilot — answers based on your uploaded documents
          </p>
        </div>
      </div>
    </div>
  );
}