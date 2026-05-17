'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, Plus, FileText, Clock, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LogoutButton } from '@/components/auth/logout-button';
import { UserAvatar } from '@/components/common/user-avatar';
import { useAuth } from '@/hooks/useAuth';
import { Document, Message } from '@/lib/types';
import { useState } from 'react';
import { format } from 'date-fns';

interface ChatSidebarProps {
  documents: Document[];
  history?: any[];
  onDeleteDocument?: (id: string) => void;
  onSelectHistory?: (item: any) => void;
}

export function ChatSidebar({
  documents,
  history = [],
  onDeleteDocument,
  onSelectHistory,
}: ChatSidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const [expandedDocs, setExpandedDocs] = useState(true);
  const [expandedHistory, setExpandedHistory] = useState(true);

  const isActive = (href: string) => pathname === href;

  return (
    <div className="w-64 h-screen bg-sidebar border-r border-sidebar-border flex flex-col overflow-hidden">

      {/* Header */}
      <div className="p-4 border-b border-sidebar-border bg-gradient-to-r from-sidebar-primary/20 via-sidebar-accent/20 to-sidebar-primary/20">
        <Link href="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition">
          <div className="p-2 bg-gradient-to-r from-primary to-secondary rounded-lg">
            <Brain className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-sidebar-foreground">AI Copilot</h1>
            <p className="text-xs text-sidebar-foreground/60">Business Analyst</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">

        {/* New Chat */}
        <Link href="/dashboard">
          <Button
            variant={isActive('/dashboard') ? 'default' : 'ghost'}
            className={`w-full justify-start ${
              isActive('/dashboard')
                ? 'bg-gradient-to-r from-sidebar-primary to-sidebar-accent text-sidebar-primary-foreground'
                : 'text-sidebar-foreground hover:bg-sidebar-accent/20'
            }`}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </Link>

        {/* Upload PDF */}
        <Link href="/upload">
          <Button
            variant={isActive('/upload') ? 'default' : 'ghost'}
            className={`w-full justify-start ${
              isActive('/upload')
                ? 'bg-gradient-to-r from-sidebar-primary to-sidebar-accent text-sidebar-primary-foreground'
                : 'text-sidebar-foreground hover:bg-sidebar-accent/20'
            }`}
          >
            <FileText className="h-4 w-4 mr-2" />
            Upload PDF
          </Button>
        </Link>

        {/* ── Query History ─────────────────────────── */}
        {history.length > 0 && (
          <div className="mt-4 pt-3 border-t border-sidebar-border/50">
            <button
              onClick={() => setExpandedHistory(!expandedHistory)}
              className="flex items-center gap-2 text-xs font-semibold text-sidebar-foreground/70 hover:text-sidebar-foreground w-full px-2 py-1.5 transition"
            >
              <Clock className="h-3 w-3" />
              Recent Queries ({history.length})
              <span className="ml-auto">{expandedHistory ? '▾' : '▸'}</span>
            </button>

            {expandedHistory && (
              <div className="mt-1 space-y-0.5">
                {history.slice(0, 15).map((item: any) => (
                  <button
                    key={item.id}
                    onClick={() => onSelectHistory?.(item)}
                    className="w-full text-left px-2 py-2 rounded hover:bg-sidebar-accent/20 group transition"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare className="h-3 w-3 mt-0.5 text-sidebar-foreground/40 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-sidebar-foreground/80 truncate group-hover:text-sidebar-foreground transition leading-relaxed">
                          {item.query?.length > 40
                            ? item.query.substring(0, 40) + '...'
                            : item.query || 'Query'}
                        </p>
                        {item.created_at && (
                          <p className="text-xs text-sidebar-foreground/40 mt-0.5">
                            {format(new Date(item.created_at), 'MMM d, HH:mm')}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── My Documents ──────────────────────────── */}
        {documents.length > 0 && (
          <div className="mt-4 pt-3 border-t border-sidebar-border/50">
            <button
              onClick={() => setExpandedDocs(!expandedDocs)}
              className="flex items-center gap-2 text-xs font-semibold text-sidebar-foreground/70 hover:text-sidebar-foreground w-full px-2 py-1.5 transition"
            >
              <FileText className="h-3 w-3" />
              My Documents ({documents.length})
              <span className="ml-auto">{expandedDocs ? '▾' : '▸'}</span>
            </button>

            {expandedDocs && (
              <div className="mt-1 space-y-0.5">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between gap-2 px-2 py-2 rounded hover:bg-sidebar-accent/20 group text-xs text-sidebar-foreground/70 hover:text-sidebar-foreground transition"
                  >
                    <FileText className="h-3 w-3 flex-shrink-0" />
                    <span className="truncate flex-1">{doc.name}</span>
                    {onDeleteDocument && (
                      <button
                        onClick={() => onDeleteDocument(doc.id)}
                        className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition text-xs"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>

      {/* User Section */}
      <div className="border-t border-sidebar-border p-4 space-y-3">
        <div className="flex items-center gap-3 px-1">
          <UserAvatar
            name={user?.name}
            email={user?.email}
            avatarUrl={user?.avatar_url}
          />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-sidebar-foreground truncate">
              {user?.name || user?.email}
            </p>
            <p className="text-xs text-sidebar-foreground/60 truncate">
              {user?.email}
            </p>
          </div>
        </div>
        <LogoutButton />
      </div>

    </div>
  );
}