'use client';

import { useState, useRef } from 'react';
import { Upload, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PdfDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  isLoading?: boolean;
}

export function PdfDropzone({ onFilesSelected, isLoading }: PdfDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files).filter((file) =>
      file.type === 'application/pdf'
    );

    if (files.length > 0) {
      onFilesSelected(files);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      onFilesSelected(files);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        isDragging
          ? 'border-blue-400 bg-blue-500/10'
          : 'border-slate-600 bg-slate-800/50 hover:border-slate-500'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileInputChange}
        className="hidden"
        disabled={isLoading}
      />

      <div className="flex justify-center mb-4">
        <div className="p-4 bg-blue-500/20 rounded-full">
          <Upload className="h-8 w-8 text-blue-400" />
        </div>
      </div>

      <h3 className="text-lg font-semibold text-white mb-2">Drop PDFs here</h3>
      <p className="text-slate-400 mb-4">or</p>

      <Button
        onClick={() => inputRef.current?.click()}
        disabled={isLoading}
        variant="outline"
      >
        Browse Files
      </Button>

      <p className="text-xs text-slate-500 mt-4">
        Supported format: PDF (Max 100MB per file)
      </p>
    </div>
  );
}
