'use client';

import { Document } from '@/lib/types';
import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';

interface PdfListProps {
  documents: Document[];
  onDelete?: (id: string) => void;
}

export function PdfList({ documents, onDelete }: PdfListProps) {
  if (documents.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-400">No documents uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-3 bg-slate-800 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
        >
          <div className="flex-1">
            <h4 className="font-semibold text-white text-sm">{doc.name}</h4>
            <p className="text-xs text-slate-400">
              Uploaded {formatDistanceToNow(doc.uploaded_at, { addSuffix: true })} • {(doc.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
          {onDelete && (
            <Button
              onClick={() => onDelete(doc.id)}
              variant="ghost"
              size="sm"
              className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}
