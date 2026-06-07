import MetricGauge, { scoreColor, scoreLabel } from './MetricGauge.jsx';

const METRIC_META = {
  faithfulness:      { label: 'Faithfulness',      min: 0.90, description: 'Answer supported by retrieved context' },
  answer_relevancy:  { label: 'Answer Relevancy',  min: 0.80, description: 'Answer relevance to the question' },
  context_recall:    { label: 'Context Recall',    min: 0.80, description: 'Ground truth covered by context' },
  context_precision: { label: 'Context Precision', min: 0.80, description: 'Precision of retrieved context' },
  ragas_score:       { label: 'RAGAS Score',       min: 0.85, description: 'Harmonic mean of all metrics' },
};

export default function MetricCard({ metric, score, animate = true }) {
  const meta = METRIC_META[metric] ?? { label: metric, min: 0.80, description: '' };
  const color = scoreColor(score ?? 0);
  const label = scoreLabel(score ?? 0);
  const passRate = Math.min(100, Math.round(((score ?? 0) / (meta.min || 1)) * 100));

  return (
    <div
      className={`bg-slate-800 border border-slate-700 rounded-xl p-5 flex flex-col items-center
                  transition-all duration-200 hover:border-slate-600 hover:shadow-xl hover:-translate-y-0.5
                  ${animate ? 'animate-slide-up' : ''}`}
    >
      {/* Gauge */}
      <MetricGauge score={score ?? 0} size={128} />

      {/* Label */}
      <h3 className="mt-3 text-sm font-semibold text-slate-100 text-center">
        {meta.label}
      </h3>

      {/* Description */}
      <p className="text-xs text-slate-500 text-center mt-1 leading-relaxed">
        {meta.description}
      </p>

      {/* Threshold bar */}
      <div className="w-full mt-3">
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Score</span>
          <span>Min: {(meta.min * 100).toFixed(0)}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-slate-700 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${Math.round((score ?? 0) * 100)}%`,
              backgroundColor: color,
            }}
          />
        </div>
        {/* Threshold marker */}
        <div className="relative mt-0.5 h-2">
          <div
            className="absolute top-0 w-px h-2 bg-slate-500"
            style={{ left: `${meta.min * 100}%` }}
            title={`Min: ${meta.min}`}
          />
        </div>
      </div>

      {/* Badge */}
      <span
        className={`mt-2 text-xs font-semibold px-2 py-0.5 rounded-full`}
        style={{
          color,
          backgroundColor: `${color}18`,
          border: `1px solid ${color}40`,
        }}
      >
        {score !== null && score !== undefined
          ? `${score.toFixed(4)} · ${label}`
          : 'No data'}
      </span>
    </div>
  );
}
