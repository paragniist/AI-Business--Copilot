'use client';

import { Brain, Sparkles } from 'lucide-react';
import { GoogleLoginButton } from '@/components/auth/google-login-button';

export default function LoginPage() {
  return (
    <div className="relative flex items-center justify-center min-h-screen bg-background overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '0ms' }}></div>
        <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-secondary/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1000ms' }}></div>
        <div className="absolute top-1/2 right-0 w-72 h-72 bg-accent/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '500ms' }}></div>
      </div>

      <div className="relative w-full max-w-md px-6 z-10">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary via-secondary to-accent rounded-full blur-2xl opacity-40 -z-10"></div>
            <div className="p-4 bg-card rounded-full border border-border/50">
              <Brain className="h-12 w-12 text-primary" />
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent mb-2">AI Business Copilot</h1>
          <p className="text-muted-foreground text-lg flex items-center justify-center gap-2">
            <Sparkles className="h-4 w-4" />
            Your AI-powered business analyst
          </p>
        </div>

        <div className="bg-card/80 backdrop-blur-sm p-8 rounded-2xl border border-border/50 shadow-2xl">
          <GoogleLoginButton />
          <p className="text-xs text-muted-foreground text-center mt-6">
            We use Supabase for secure authentication
          </p>
        </div>

        <p className="text-muted-foreground text-xs text-center mt-8">
          Your data is encrypted and secure
        </p>
      </div>
    </div>
  );
}
