'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function HomePage() {
  const router = useRouter();
  const { isSignedIn, isLoading, isConfigured } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      // If Supabase is not configured, go straight to login
      if (!isConfigured) {
        router.replace('/login');
      } else {
        router.replace(isSignedIn ? '/dashboard' : '/login');
      }
    }
  }, [isSignedIn, isLoading, isConfigured, router]);

  return null;
}
