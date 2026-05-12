from langchain_groq import ChatGroq
from workflows.state import BusinessState
from dotenv import load_dotenv
import json

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

def dashboard_agent(state: BusinessState) -> BusinessState:
    print("[Dashboard] Generating dashboard code...")

    data = state.get("extracted_data", {})
    data_json = json.dumps(data, indent=2)

    prompt = f"""You are a React dashboard code generator for browser environments.
Generate a Dashboard React component using this business data.

DATA:
{data_json}

STRICT RULES — follow exactly or the dashboard will break:
1. NO import statements — React, useEffect, useRef, useState are available as globals
2. Use React.useEffect, React.useRef, React.useState (not destructured imports)
3. Chart.js is available as window.Chart — use: new Chart(canvas, config)
4. Use inline styles only — no Tailwind, no CSS classes
5. Function must be named exactly: function Dashboard()
6. No export statement
7. Use canvas elements for charts with React.useRef

Here is the EXACT template to follow — fill in the data:

function Dashboard() {{
  const revenue = {data_json};

  const chartRef = React.useRef(null);
  const chartInstance = React.useRef(null);

  React.useEffect(() => {{
    if (chartRef.current) {{
      if (chartInstance.current) {{
        chartInstance.current.destroy();
      }}
      const ctx = chartRef.current.getContext('2d');
      chartInstance.current = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: /* FILL IN labels from data e.g. ['Q1','Q2','Q3','Q4'] */,
          datasets: [{{
            label: /* FILL IN chart title */,
            data: /* FILL IN numbers from data e.g. [3.4, 3.2, 2.9, 2.9] */,
            backgroundColor: ['#0F6E56','#534AB7','#854F0B','#B84236'],
            borderRadius: 6,
          }}]
        }},
        options: {{
          responsive: true,
          plugins: {{
            legend: {{ labels: {{ color: '#e2e8f0' }} }},
            title: {{
              display: true,
              text: /* FILL IN chart title */,
              color: '#e2e8f0',
              font: {{ size: 14 }}
            }}
          }},
          scales: {{
            x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#1e293b' }} }},
            y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#1e293b' }} }}
          }}
        }}
      }});
    }}
    return () => {{
      if (chartInstance.current) {{
        chartInstance.current.destroy();
      }}
    }};
  }}, []);

  const kpiCards = /* FILL IN array of objects like: */
    [
      /* fill from metrics in data, e.g.: */
      /* {{ label: 'Total Revenue', value: '$12.4M', trend: 'down', change: '-8%' }}, */
    ];

  return (
    <div style={{{{ backgroundColor: '#0f172a', minHeight: '100vh', padding: '20px', fontFamily: 'Arial, sans-serif' }}}}>
      <h1 style={{{{ color: '#e2e8f0', fontSize: '20px', marginBottom: '20px', fontWeight: 'bold' }}}}>
        /* FILL IN dashboard title from data */
      </h1>

      /* KPI Cards row */
      <div style={{{{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}}}>
        {{kpiCards.map((card, i) => (
          <div key={{i}} style={{{{
            backgroundColor: '#1e293b',
            borderRadius: '12px',
            padding: '16px 20px',
            flex: '1',
            minWidth: '140px',
            border: '1px solid #334155'
          }}}}>
            <div style={{{{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}}}>{{card.label}}</div>
            <div style={{{{ color: '#e2e8f0', fontSize: '24px', fontWeight: 'bold' }}}}>{{card.value}}</div>
            {{card.change && (
              <div style={{{{ color: card.trend === 'up' ? '#10b981' : '#ef4444', fontSize: '12px', marginTop: '4px' }}}}>
                {{card.trend === 'up' ? '▲' : '▼'}} {{card.change}}
              </div>
            )}}
          </div>
        ))}}
      </div>

      /* Chart */
      <div style={{{{ backgroundColor: '#1e293b', borderRadius: '12px', padding: '20px', border: '1px solid #334155' }}}}>
        <canvas ref={{chartRef}} style={{{{ maxHeight: '280px' }}}}></canvas>
      </div>
    </div>
  );
}}

Now generate the complete Dashboard function with the actual data filled in.
Return ONLY the function code. No imports. No export. Start with: function Dashboard() {{
"""

    dashboard_code = llm.invoke(prompt).content.strip()

    # Remove markdown fences
    if "```" in dashboard_code:
        lines = dashboard_code.split("\n")
        clean_lines = [l for l in lines if not l.strip().startswith("```")]
        dashboard_code = "\n".join(clean_lines).strip()

    # Remove any import statements the LLM added anyway
    clean_lines = []
    for line in dashboard_code.split("\n"):
        if line.strip().startswith("import ") or line.strip().startswith("export "):
            continue
        clean_lines.append(line)
    dashboard_code = "\n".join(clean_lines).strip()

    print("[Dashboard] Code generated")
    print(f"[Dashboard] Code preview: {dashboard_code[:200]}")
    return {**state, "dashboard_code": dashboard_code}