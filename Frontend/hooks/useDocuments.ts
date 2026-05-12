'use client';

import { useState, useCallback } from 'react';
import { Document } from '@/lib/types';
import { uploadPDF } from '@/lib/api';
import { useAuth } from './useAuth';

interface UseDocumentsReturn {
  documents: Document[];
  isLoading: boolean;
  uploadProgress: number;
  addDocument: (file: File) => Promise<boolean>;
  removeDocument: (id: string) => void;
  loadDocuments: () => Promise<void>;
}

export function useDocuments(): UseDocumentsReturn {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { user } = useAuth();

  const addDocument = useCallback(
    async (file: File): Promise<boolean> => {
      if (!user || !file.type.includes('pdf')) {
        console.error('[v0] Invalid file or no user');
        return false;
      }

      setIsLoading(true);
      setUploadProgress(0);

      try {
        const token = await getAuthToken();
        if (!token) {
          console.error('[v0] No auth token');
          return false;
        }

        setUploadProgress(50);
        const response = await uploadPDF(file, token);

        if (response.success) {
          const newDoc: Document = {
            id: response.data?.file_id || `doc-${Date.now()}`,
            name: response.data?.name || file.name,
            size: file.size,
            uploaded_at: new Date(),
            user_id: user.id,
          };
          setDocuments((prev) => [...prev, newDoc]);
          setUploadProgress(100);
          return true;
        } else {
          console.error('[v0] Upload failed:', response.error);
          return false;
        }
      } catch (error) {
        console.error('[v0] Error uploading document:', error);
        return false;
      } finally {
        setIsLoading(false);
        setUploadProgress(0);
      }
    },
    [user]
  );

  const removeDocument = useCallback((id: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  }, []);

  const loadDocuments = useCallback(async () => {
    if (!user) return;

    try {
      const token = await getAuthToken();
      if (!token) return;

      // This would typically fetch from an API endpoint
      // For now, documents are managed locally
      console.log('[v0] Documents loaded for user:', user.id);
    } catch (error) {
      console.error('[v0] Failed to load documents:', error);
    }
  }, [user]);

  return {
    documents,
    isLoading,
    uploadProgress,
    addDocument,
    removeDocument,
    loadDocuments,
  };
}

async function getAuthToken(): Promise<string | null> {
  try {
    const { createClient } = await import('@/lib/supabase');
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (error) {
    console.error('[v0] Failed to get auth token:', error);
    return null;
  }
}
