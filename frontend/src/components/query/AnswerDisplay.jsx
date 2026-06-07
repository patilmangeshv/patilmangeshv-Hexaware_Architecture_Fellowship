/**
 * AnswerDisplay — Shows AI response with citations + metadata
 */

import { AlertCircle, Zap, FileText, Gauge } from 'lucide-react';
import clsx from 'clsx';

const TRIAGE_COLORS = {
  auto:      { bg: '#10b98120', border: '#10b98140', icon: '✅', label: 'Auto - High Confidence' },
  review:    { bg: '#f59e0b20', border: '#f59e0b40', icon: '⚠️', label: 'Review - Medium Confidence' },
  escalate:  { bg: '#ef444420', border: '#ef444440', icon: '🚨', label: 'Escalated - Low Confidence' },
};

export default function AnswerDisplay({ result = null, loading = false }) {
  if (loading) {
    return (
      <div className="card flex items-center justify-center py-8">
        <div className="text-center">
          <div className="w-10 h-10 rounded-full border-2 border-slate-600 border-t-indigo-500 mx-auto mb-3 animate-spin" />
          <p className="text-sm text-slate-400">Searching knowledge base…</p>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const triage = TRIAGE_COLORS[result.triage_level] || TRIAGE_COLORS.auto;
  const conf = result.confidence;

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Triage badge + Confidence */}
      <div
        className="card flex items-start justify-between"
        style={{ backgroundColor: triage.bg, borderColor: triage.border, borderWidth: '1px' }}
      >
        <div>
          <p className="text-xs font-semibold text-slate-300 mb-1">
            {triage.icon} {triage.label}
          </p>
          <p className="text-xs text-slate-500">
            {result.escalated
              ? 'Confidence below threshold. Contact compliance@bank.com.'
              : result.context_type && `Context: ${result.context_type}`}
          </p>
        </div>
        <div className="flex flex-col items-end">
          <div className="text-2xl font-bold" style={{ color: getConfColor(conf) }}>
            {(conf * 100).toFixed(0)}%
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Confidence</p>
        </div>
      </div>

      {/* Answer */}
      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <Zap size={16} className="text-amber-500" />
          <h3 className="text-sm font-semibold text-slate-100">Answer</h3>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
          {result.answer}
        </p>
      </div>

      {/* Reasoning */}
      {result.reasoning && (
        <div className="card bg-slate-900/50">
          <p className="text-xs font-semibold text-slate-400 mb-2">Reasoning Chain</p>
          <p className="text-xs text-slate-400 leading-relaxed italic">
            {result.reasoning}
          </p>
        </div>
      )}

      {/* Chunks used */}
      {result.chunks_used && result.chunks_used.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <FileText size={16} className="text-blue-400" />
            <h3 className="text-sm font-semibold text-slate-100">
              Retrieved Context ({result.chunks_used.length} chunks)
            </h3>
          </div>
          <div className="space-y-2">
            {result.chunks_used.map((chunk, i) => (
              <div key={i} className="p-2.5 bg-slate-900/30 rounded-lg border border-slate-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono text-indigo-400">{chunk.source}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {chunk.context_type}
                  </span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">{chunk.text}</p>
                <div className="mt-1.5 flex items-center gap-2">
                  <Gauge size={12} className="text-slate-500" />
                  <span className="text-xs text-slate-500">
                    Relevance: <strong style={{ color: '#6366f1' }}>{(chunk.reranker_score * 100).toFixed(0)}%</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {result.sources && result.sources.length > 0 && (
        <div className="card bg-slate-900/50">
          <p className="text-xs font-semibold text-slate-400 mb-2">📚 Source Documents</p>
          <div className="flex flex-wrap gap-2">
            {result.sources.map((src, i) => (
              <span key={i} className="badge badge-blue text-xs">
                {src}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Escalation note */}
      {result.escalated && (
        <div className="card border-red-700/50 bg-red-950/20 flex gap-3">
          <AlertCircle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-300 mb-1">Escalation Required</p>
            <p className="text-xs text-red-400/80 leading-relaxed">
              This query has been escalated to a Compliance Officer for human review due to low confidence.
              Please contact compliance@bank.com for assistance.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function getConfColor(conf) {
  if (conf >= 0.9) return '#10b981';
  if (conf >= 0.75) return '#f59e0b';
  return '#ef4444';
}
