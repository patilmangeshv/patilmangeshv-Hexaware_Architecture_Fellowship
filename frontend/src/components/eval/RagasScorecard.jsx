/**
 * RagasScorecard — Golden Q&A set evaluation results
 */

import { TrendingUp, Clock, CheckCircle } from 'lucide-react';

export default function RagasScorecard({ scores = null, golden = [] }) {
  if (!scores) {
    return (
      <div className="card text-center py-8">
        <p className="text-sm text-slate-400">No evaluation results yet. Click "Run Evaluation" to start.</p>
      </div>
    );
  }

  const pct = (v) => (v * 100).toFixed(2);
  const isPassed = scores.faithfulness >= 0.90;

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricBox
          label="Faithfulness"
          value={pct(scores.faithfulness)}
          icon="✓"
          pass={scores.faithfulness >= 0.90}
        />
        <MetricBox
          label="Answer Relevancy"
          value={pct(scores.answer_relevancy)}
          icon="📎"
          pass={scores.answer_relevancy >= 0.80}
        />
        <MetricBox
          label="Context Recall"
          value={pct(scores.context_recall)}
          icon="🎯"
          pass={scores.context_recall >= 0.80}
        />
        <MetricBox
          label="Context Precision"
          value={pct(scores.context_precision)}
          icon="🔍"
          pass={scores.context_precision >= 0.80}
        />
      </div>

      {/* RAGAS Score + Overall */}
      <div className="card">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex flex-col items-center justify-center p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
            <TrendingUp size={20} className="text-indigo-400 mb-2" />
            <p className="text-xs text-slate-400 mb-1">RAGAS Score</p>
            <p className="text-3xl font-bold text-indigo-300">{pct(scores.ragas_score)}%</p>
          </div>

          <div className="flex flex-col items-center justify-center p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
            <p className="text-xs text-slate-400 mb-1">Questions Evaluated</p>
            <p className="text-3xl font-bold text-slate-300">{scores.num_questions}</p>
          </div>

          <div
            className="flex flex-col items-center justify-center p-4 rounded-lg border-2"
            style={{
              backgroundColor: isPassed ? '#10b98120' : '#ef444420',
              borderColor: isPassed ? '#10b98140' : '#ef444440',
            }}
          >
            <CheckCircle
              size={20}
              style={{ color: isPassed ? '#10b981' : '#ef4444' }}
              className="mb-2"
            />
            <p className="text-xs text-slate-400 mb-1">Pass Gate</p>
            <p
              className="text-lg font-bold"
              style={{ color: isPassed ? '#10b981' : '#ef4444' }}
            >
              {isPassed ? '✓ PASS' : '✗ FAIL'}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">≥ 0.90 faithfulness</p>
          </div>
        </div>
      </div>

      {/* Run info */}
      <div className="card bg-slate-900/50 text-xs text-slate-400 flex items-center gap-2">
        <Clock size={14} />
        <span>
          {scores.run_at
            ? new Date(scores.run_at).toLocaleString()
            : 'Unknown time'}
        </span>
        <span className="ml-auto px-2 py-1 rounded bg-slate-800 text-slate-300">
          {scores.method || 'ragas'} evaluation
        </span>
      </div>
    </div>
  );
}

function MetricBox({ label, value, icon, pass }) {
  const color = pass ? '#10b981' : '#ef4444';
  return (
    <div
      className="card text-center"
      style={{ borderColor: color + '40' }}
    >
      <p className="text-lg mb-1">{icon}</p>
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className="text-xl font-bold" style={{ color }}>
        {value}%
      </p>
    </div>
  );
}
