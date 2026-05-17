'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (query: string) => Promise<void>;
  isLoading: boolean;
  value: string;
  onChange: (value: string) => void;
}

export function ChatInput({
  onSend,
  isLoading,
  value,
  onChange,
}: ChatInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      await onSend(value.trim());
    }
  };

  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  return (
    <form
      onSubmit={handleSubmit}
      className="flex gap-2 p-4 bg-slate-800 border-t border-slate-700"
    >
      <Input
        ref={inputRef}
        type="text"
        placeholder="Ask anything about your business data..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={isLoading}
        className="flex-1 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
      />
      <Button
        type="submit"
        disabled={isLoading || !value.trim()}
        size="icon"
        className="bg-blue-600 hover:bg-blue-700"
      >
        {isLoading ? (
          <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </form>
  );
}
