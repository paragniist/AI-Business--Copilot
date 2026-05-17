'use client';

import { Brain } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <div className="p-6 bg-slate-800/50 rounded-full">
        <Brain className="h-16 w-16 text-blue-400" />
      </div>
      <h2 className="text-2xl font-bold text-white text-center">Start a conversation</h2>
      <p className="text-slate-400 text-center max-w-md">
        Ask anything about your business data. I&apos;ll analyze PDFs, look up information, and provide insights.
      </p>
    </div>
  );
}
