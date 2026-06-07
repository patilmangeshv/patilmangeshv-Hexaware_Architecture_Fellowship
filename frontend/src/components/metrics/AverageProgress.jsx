/**
 * AverageProgress — Shows all RAGAS metrics with progress bars
 * Displays cumulative pass rate and average scores
 */

const METRICS = [
  { key: 'faithfulness',      label: 'Faithfulness',      min: 0.90 },
  { key: 'answer_relevancy',  label: 'Answer Relevancy',  min: 0.80 },
  { key: 'context_recall',    label: 'Context Recall',    min: 0.80 },
  { key: 'context_precision', label: 'Context Precision', min: 0.80 },
];

function getColor(score, min) {
  if (score >= min) return { bg: '#10b981', light: '#10b98118' };
  if (score >= 0.7) return { bg: '#f59e0b', light: '#f59e0b18' };
  return { bg: '#ef4444', light: '#ef444418' };
}

export default function AverageProgress({ scores = {} }) {
  const values = METRICS.map((m) => scores[m.key] ?? 0);
  const avg = values.length > 0 ? values.reduce((a, b) => a + b) / values.length : 0;
  const passCount = values.filter((v, i) => v >= METRICS[i].min).length;
  const passRate = (passCount / METRICS.length) * 100;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-semibold text-slate-100">Score Breakdown</h3>
        <span className="text-xs text-slate-400">
          {passCount}/{METRICS.length} metrics passing
        </span>
      </div>

      {/* Average Card */}
      <div className="mb-5 p-3 rounded-lg bg-slate-900/50 border border-slate-700/50">
        <p className="text-xs text-slate-400 mb-1">Average Score</p>
        <p className="text-2xl font-bold text-indigo-400">{(avg * 100).toFixed(1)}%</p>
        <p className="text-xs text-slate-500 mt-1">
          {passCount === METRICS.length
            ? '✓ All metrics passing'
            : `${passCount} of ${METRICS.length} passing`}
        </p>
      </div>

      {/* Metrics */}
      <div className="space-y-3">
        {METRICS.map((m) => {
          const v = scores[m.key] ?? 0;
          const c = getColor(v, m.min);
          const isPassing = v >= m.min;
          return (
            <div key={m.key}>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-300 font-medium">{m.label}</span>
                <span className="text-slate-400">
                  {isPassing ? '✓' : '✗'} {(v * 100).toFixed(1)}% (min {(m.min * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-1.5 rounded-full overflow-hidden bg-slate-700">
                <div
                  className="h-full transition-all duration-500"
                  style={{ width: `${v * 100}%`, backgroundColor: c.bg }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-4 text-xs">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: '#10b981' }} />
          <span className="text-slate-400">Pass (≥ min)</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: '#f59e0b' }} />
          <span className="text-slate-400">Warn (0.70+)</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: '#ef4444' }} />
          <span className="text-slate-400">Fail (&lt; 0.70)</span>
        </span>
      </div>
    </div>
  );
}
