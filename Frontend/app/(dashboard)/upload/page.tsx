'use client';

import { useState } from 'react';
import { PdfDropzone } from '@/components/upload/pdf-dropzone';
import { PdfList } from '@/components/upload/pdf-list';
import { UploadProgress } from '@/components/upload/upload-progress';
import { useDocuments } from '@/hooks/useDocuments';
import { useToast } from '@/hooks/use-toast';

export default function UploadPage() {
  const { documents, addDocument, removeDocument, isLoading, uploadProgress } =
    useDocuments();
  const { toast } = useToast();
  const [uploadingFile, setUploadingFile] = useState<string | null>(null);

  const handleFilesSelected = async (files: File[]) => {
    for (const file of files) {
      if (file.type !== 'application/pdf') {
        toast({
          title: 'Invalid file',
          description: 'Please upload PDF files only',
          variant: 'destructive',
        });
        continue;
      }

      if (file.size > 100 * 1024 * 1024) {
        toast({
          title: 'File too large',
          description: 'Files must be less than 100MB',
          variant: 'destructive',
        });
        continue;
      }

      setUploadingFile(file.name);
      const success = await addDocument(file);
      
      if (success) {
        toast({
          title: 'Upload successful',
          description: `${file.name} has been uploaded`,
        });
      } else {
        toast({
          title: 'Upload failed',
          description: `Failed to upload ${file.name}`,
          variant: 'destructive',
        });
      }
      
      setUploadingFile(null);
    }
  };

  return (
    <div className="flex flex-col h-full p-8">
      <div className="max-w-3xl mx-auto w-full">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Upload Documents</h1>
          <p className="text-slate-400">
            Upload PDF files to analyze them with AI
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-12">
          <PdfDropzone
            onFilesSelected={handleFilesSelected}
            isLoading={isLoading}
          />
        </div>

        {/* Progress */}
        {uploadingFile && uploadProgress > 0 && (
          <div className="mb-12">
            <h2 className="text-lg font-semibold text-white mb-4">Uploading</h2>
            <UploadProgress fileName={uploadingFile} progress={uploadProgress} />
          </div>
        )}

        {/* Documents List */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">
            Your Documents ({documents.length})
          </h2>
          <PdfList
            documents={documents}
            onDelete={removeDocument}
          />
        </div>
      </div>
    </div>
  );
}
