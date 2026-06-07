/**
 * FailureModeRegister — Comprehensive failure mode analysis table
 */

export default function FailureModeRegister({ modes = [] }) {
  if (modes.length === 0) {
    return (
      <div className="card text-center py-8 text-slate-400 text-sm">
        No failure modes loaded.
      </div>
    );
  }

  const severityColor = (sev) => {
    const map = { Critical: '#ef4444', High: '#f59e0b', Medium: '#3b82f6', Low: '#10b981' };
    return map[sev] || '#94a3b8';
  };

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="px-3 py-2.5 text-left font-semibold text-slate-400">ID</th>
            <th className="px-3 py-2.5 text-left font-semibold text-slate-400">Mode</th>
            <th className="px-3 py-2.5 text-left font-semibold text-slate-400">Description</th>
            <th className="px-3 py-2.5 text-center font-semibold text-slate-400">Severity</th>
            <th className="px-3 py-2.5 text-center font-semibold text-slate-400">Likelihood</th>
            <th className="px-3 py-2.5 text-left font-semibold text-slate-400">Mitigation</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {modes.map((m) => (
            <tr key={m.id} className="hover:bg-slate-700/10 transition-colors">
              <td className="px-3 py-2 font-mono text-indigo-400 font-medium">{m.id}</td>
              <td className="px-3 py-2 font-medium text-slate-100">{m.mode}</td>
              <td className="px-3 py-2 text-slate-300 max-w-xs">{m.description}</td>
              <td className="px-3 py-2 text-center">
                <span
                  className="px-2 py-0.5 rounded-full font-medium"
                  style={{
                    color: severityColor(m.severity),
                    backgroundColor: severityColor(m.severity) + '18',
                    border: `1px solid ${severityColor(m.severity)}40`,
                  }}
                >
                  {m.severity}
                </span>
              </td>
              <td className="px-3 py-2 text-center text-slate-400">{m.likelihood}</td>
              <td className="px-3 py-2 text-slate-400 text-xs leading-relaxed">{m.mitigation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
