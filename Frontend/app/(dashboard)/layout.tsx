'use client';
import { useEffect, useState } from 'react';
import { ChatSidebar } from '@/components/chat/chat-sidebar';
import { useDocuments } from '@/hooks/useDocuments';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { getHistory } from '@/lib/api';

async function getAuthToken(): Promise<string | null> {
  try {
    const { createClient } = await import('@/lib/supabase');
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch {
    return null;
  }
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isSignedIn } = useAuth();
  const { documents, removeDocument } = useDocuments();
  const [history, setHistory] = useState<any[]>([]);
  const router = useRouter();

  // Load history for sidebar
  useEffect(() => {
    async function fetchHistory() {
      try {
        const token = await getAuthToken();
        if (!token) return;
        const res = await getHistory(token);
        if (res.success && Array.isArray(res.data)) {
          setHistory(res.data);
        }
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    }
    if (isSignedIn) fetchHistory();
  }, [isSignedIn]);

  useEffect(() => {
    if (!isLoading && !isSignedIn) {
      router.push('/login');
    }
  }, [isLoading, isSignedIn, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin h-8 w-8 border-2 border-current border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isSignedIn) return null;

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <ChatSidebar
        documents={documents}
        history={history}
        onDeleteDocument={removeDocument}
      />
      <main className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-950 to-slate-900">
        {children}
      </main>
    </div>
  );
}