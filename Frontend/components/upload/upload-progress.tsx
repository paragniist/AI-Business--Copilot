'use client';

import { Upload } from 'lucide-react';

interface UploadProgressProps {
  fileName: string;
  progress: number;
}

export function UploadProgress({ fileName, progress }: UploadProgressProps) {
  return (
    <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
      <div className="flex items-center gap-3 mb-2">
        <Upload className="h-4 w-4 text-blue-400 animate-bounce" />
        <span className="text-sm font-semibold text-white truncate">{fileName}</span>
        <span className="text-xs text-slate-400">{progress}%</span>
      </div>
      <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
        <div
          className="bg-gradient-to-r from-blue-500 to-blue-400 h-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
