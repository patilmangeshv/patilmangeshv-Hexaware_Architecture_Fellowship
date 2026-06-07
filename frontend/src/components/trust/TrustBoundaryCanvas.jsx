/**
 * Trust Boundary Canvas — 2x2 grid visualization
 * Shows AI autonomous, AI-assisted, Human-required, and Sensitive zones
 * Plus the 10-item Failure Mode Register
 */

import { Shield, AlertTriangle, Check, Lock } from 'lucide-react';

const SEVERITY_COLOR = {
  Critical: '#ef4444',
  High: '#f59e0b',
  Medium: '#3b82f6',
  Low: '#10b981',
};

export default function TrustBoundaryCanvas({ data = null }) {
  const zones = data?.zones ?? [];
  const failureModes = data?.failure_modes ?? [];

  return (
    <div className="space-y-8">
      {/* Trust Boundary Canvas */}
      <div>
        <h2 className="section-title">
          <Shield size={18} className="text-indigo-400" />
          Trust Boundary Canvas
        </h2>
        <p className="text-sm text-slate-400 mb-4">
          Zones: Red = Sensitive (never to AI) · Orange = Human-Required · Blue = AI-Assisted · Green = AI Autonomous
        </p>

        {/* 2x2 Grid */}
        <div className="grid grid-cols-2 gap-4">
          {zones.map((zone) => (
            <div
              key={zone.id}
              className="card relative overflow-hidden border-2"
              style={{ borderColor: zone.color + '40' }}
            >
              {/* Background accent */}
              <div
                className="absolute inset-0 opacity-5"
                style={{ backgroundColor: zone.color }}
              />

              {/* Content */}
              <div className="relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-sm" style={{ color: zone.color }}>
                      {zone.label}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {zone.description}
                    </p>
                  </div>
                  <div
                    className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: zone.color + '20', color: zone.color }}
                  >
                    {zone.id === 'ai_autonomous' && <Check size={14} />}
                    {zone.id === 'ai_assisted' && <Shield size={14} />}
                    {zone.id === 'human_required' && <AlertTriangle size={14} />}
                    {zone.id === 'sensitive_protected' && <Lock size={14} />}
                  </div>
                </div>

                {/* Capabilities */}
                <ul className="space-y-1.5">
                  {zone.capabilities.map((cap, i) => (
                    <li
                      key={i}
                      className="text-xs text-slate-300 flex items-start gap-2"
                    >
                      <span
                        className="w-1 h-1 rounded-full flex-shrink-0 mt-1.5"
                        style={{ backgroundColor: zone.color }}
                      />
                      <span>{cap}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Failure Mode Register */}
      <div>
        <h2 className="section-title">
          <AlertTriangle size={18} className="text-amber-500" />
          Failure Mode Register
        </h2>
        <p className="text-sm text-slate-400 mb-4">
          Minimum 8 failure modes. Row 1: Regulatory Misstatement (guarded by faithfulness ≥ 0.90).
        </p>

        {/* Table */}
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-400 font-mono">
                  ID
                </th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-400">
                  Failure Mode
                </th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-400">
                  Description
                </th>
                <th className="text-center px-4 py-2.5 text-xs font-semibold text-slate-400">
                  Severity
                </th>
                <th className="text-center px-4 py-2.5 text-xs font-semibold text-slate-400">
                  Likelihood
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {failureModes.slice(0, 10).map((fm) => (
                <tr key={fm.id} className="hover:bg-slate-700/20 transition-colors">
                  <td className="px-4 py-2.5 font-mono text-xs text-indigo-400 font-medium">
                    {fm.id}
                  </td>
                  <td className="px-4 py-2.5 font-medium text-slate-100">
                    {fm.mode}
                  </td>
                  <td className="px-4 py-2.5 text-slate-300 max-w-xs">
                    <span className="text-xs leading-relaxed">{fm.description}</span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span
                      className="px-2 py-0.5 text-xs font-semibold rounded-full"
                      style={{
                        color: SEVERITY_COLOR[fm.severity],
                        backgroundColor: SEVERITY_COLOR[fm.severity] + '18',
                        border: `1px solid ${SEVERITY_COLOR[fm.severity]}40`,
                      }}
                    >
                      {fm.severity}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center text-xs text-slate-400">
                    {fm.likelihood}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Footer note */}
          <div className="px-4 py-3 bg-slate-900/50 border-t border-slate-700 text-xs text-slate-500">
            <strong>Mitigation Strategy (Row 1):</strong> Regulatory Misstatement mitigated by citation enforcement in
            prompt + RAGAS faithfulness gate at ≥ 0.90.
          </div>
        </div>
      </div>
    </div>
  );
}
