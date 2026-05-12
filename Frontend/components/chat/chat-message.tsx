'use client';

import { Message } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { DashboardRenderer } from './DashboardRenderer';

interface ChatMessageProps {
  message: Message;
}

const intentColors: Record<string, string> = {
  analysis:  'bg-purple-500/20 text-purple-300 border border-purple-500/40',
  lookup:    'bg-teal-500/20 text-teal-300 border border-teal-500/40',
  summarize: 'bg-amber-500/20 text-amber-300 border border-amber-500/40',
  dashboard: 'bg-blue-500/20 text-blue-300 border border-blue-500/40',
  other:     'bg-slate-500/20 text-slate-300 border border-slate-500/40',
};

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const intentLabel =
    message.intent &&
    message.intent.charAt(0).toUpperCase() + message.intent.slice(1);

  // ── Dashboard message ──────────────────────────────────────
  if (!isUser && message.dashboardCode) {
    return (
      <div className="flex justify-start mb-6">
        <div className="w-full max-w-4xl">
          {/* Intent badge */}
          <div className="mb-2 flex items-center gap-2">
            <Badge
              className="text-xs font-medium px-2.5 py-0.5 bg-blue-500/20 text-blue-300 border border-blue-500/40"
              variant="outline"
            >
              Dashboard
            </Badge>
            <span className="text-xs text-slate-500">
              Generated from your documents
            </span>
          </div>

          {/* Dashboard renderer */}
          <DashboardRenderer
            code={message.dashboardCode}
            title={message.dashboardTitle || 'Business Dashboard'}
          />

          {/* Timestamp */}
          <div className="text-xs text-slate-500 mt-1 text-right">
            {format(new Date(message.timestamp), 'HH:mm')}
          </div>
        </div>
      </div>
    );
  }

  // ── Regular text message ───────────────────────────────────
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div
        className={`max-w-3xl w-full ${
          isUser
            ? 'bg-gradient-to-r from-purple-600/80 to-teal-600/80 text-white rounded-2xl ml-12'
            : 'bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-100 rounded-2xl mr-12'
        } px-5 py-4 shadow-lg`}
      >
        {/* Intent badge */}
        {!isUser && intentLabel && (
          <div className="mb-3">
            <Badge
              className={`text-xs font-medium px-2.5 py-0.5 ${intentColors[message.intent || 'other']}`}
              variant="outline"
            >
              {intentLabel}
            </Badge>
          </div>
        )}

        {/* Message content */}
        <div className="prose prose-invert prose-sm max-w-none
          prose-headings:text-slate-100
          prose-p:text-slate-200 prose-p:leading-relaxed prose-p:my-1
          prose-strong:text-white
          prose-ul:text-slate-200 prose-ol:text-slate-200
          prose-li:text-slate-200 prose-li:my-0.5
          prose-code:text-teal-300 prose-code:bg-slate-900
          prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700
          prose-table:text-sm
          prose-th:text-slate-100 prose-th:bg-slate-700/50
          prose-td:text-slate-200 prose-td:border-slate-700
        ">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ children }) => (
                <div className="overflow-x-auto my-3 rounded-lg border border-slate-700">
                  <table className="w-full border-collapse text-sm">{children}</table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-slate-700/60">{children}</thead>
              ),
              th: ({ children }) => (
                <th className="px-3 py-2 text-left text-slate-100 font-semibold border-b border-slate-600">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-3 py-2 text-slate-200 border-b border-slate-700/50">
                  {children}
                </td>
              ),
              tr: ({ children }) => (
                <tr className="hover:bg-slate-700/20 transition-colors">{children}</tr>
              ),
              h1: ({ children }) => (
                <h1 className="text-xl font-bold text-white mt-4 mb-2 pb-1 border-b border-slate-700">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-lg font-bold text-slate-100 mt-4 mb-2">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-base font-semibold text-slate-200 mt-3 mb-1">{children}</h3>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-outside ml-4 space-y-1 my-2">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-outside ml-4 space-y-1 my-2">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="text-slate-200 leading-relaxed">{children}</li>
              ),
              p: ({ children }) => (
                <p className="text-slate-200 leading-relaxed my-1.5">{children}</p>
              ),
              strong: ({ children }) => (
                <strong className="text-white font-semibold">{children}</strong>
              ),
              code: ({ node, inline, children, ...props }: any) =>
                inline ? (
                  <code className="bg-slate-900 text-teal-300 px-1.5 py-0.5 rounded text-xs font-mono">
                    {children}
                  </code>
                ) : (
                  <pre className="bg-slate-900 border border-slate-700 p-3 rounded-lg overflow-x-auto my-2">
                    <code className="text-xs font-mono text-slate-200">{children}</code>
                  </pre>
                ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div className="text-xs opacity-50 mt-3 text-right">
          {format(new Date(message.timestamp), 'HH:mm')}
        </div>
      </div>
    </div>
  );
}