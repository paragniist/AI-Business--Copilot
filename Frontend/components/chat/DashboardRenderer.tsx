'use client';

interface DashboardRendererProps {
  code: string;
  title: string;
}

export function DashboardRenderer({ code, title }: DashboardRendererProps) {
  const html = generateHTML(code);

  return (
    <div className="w-full rounded-xl border border-slate-700 overflow-hidden shadow-lg">
      {/* Header bar */}
      <div className="bg-slate-800 px-4 py-2.5 flex items-center gap-2 border-b border-slate-700">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500/70" />
          <div className="w-3 h-3 rounded-full bg-amber-500/70" />
          <div className="w-3 h-3 rounded-full bg-teal-500/70" />
        </div>
        <span className="text-xs text-slate-300 font-medium ml-2">{title}</span>
        <span className="ml-auto text-xs text-slate-500 italic">
          AI Generated Dashboard
        </span>
      </div>

      {/* Dashboard iframe */}
      <iframe
        srcDoc={html}
        className="w-full border-0 bg-slate-900"
        style={{ height: '500px' }}
        sandbox="allow-scripts"
        title={title}
      />
    </div>
  );
}

function generateHTML(componentCode: string): string {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0f172a;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 16px;
    }
    .error {
      background: #1e293b;
      border: 1px solid #ef4444;
      border-radius: 8px;
      padding: 16px;
      color: #ef4444;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    const { useEffect, useRef, useState } = React;

    ${componentCode}

    try {
      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<Dashboard />);
    } catch(e) {
      document.getElementById('root').innerHTML =
        '<div class="error">Dashboard render error: ' + e.message + '</div>';
    }
  </script>
</body>
</html>`;
}