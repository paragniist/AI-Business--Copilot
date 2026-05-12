'use client';

export function LoadingSpinner() {
  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-slate-800 rounded-lg max-w-md">
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce animation-delay-100" />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce animation-delay-200" />
      </div>
      <span className="text-sm text-slate-300">Thinking...</span>
    </div>
  );
}
