/**
 * MetricGauge — SVG arc gauge (speedometer style)
 * startAngle=220°, arc spans 280° going clockwise through the top.
 * Angles use toPoint convention: 0°=top, increase clockwise.
 */

function polarToPoint(cx, cy, r, angleDeg) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
}

function arcPath(cx, cy, r, startDeg, endDeg) {
  const [sx, sy] = polarToPoint(cx, cy, r, startDeg);
  const [ex, ey] = polarToPoint(cx, cy, r, endDeg);
  const span = ((endDeg - startDeg) + 360) % 360;
  const large = span > 180 ? 1 : 0;
  return `M ${sx.toFixed(2)} ${sy.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${ex.toFixed(2)} ${ey.toFixed(2)}`;
}

const START = 220;
const TOTAL = 280;

export function scoreColor(score) {
  if (score >= 0.9) return '#10b981';
  if (score >= 0.75) return '#f59e0b';
  return '#ef4444';
}

export function scoreLabel(score) {
  if (score >= 0.9) return 'PASS';
  if (score >= 0.75) return 'WARN';
  return 'FAIL';
}

export default function MetricGauge({ score = 0, size = 130, strokeWidth = 10 }) {
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - strokeWidth - 2;
  const pct = Math.min(1, Math.max(0, score));
  const scoreEnd = START + TOTAL * pct;
  const color = scoreColor(pct);

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      aria-label={`Score: ${Math.round(pct * 100)}%`}
    >
      {/* Track */}
      <path
        d={arcPath(cx, cy, r, START, START + TOTAL)}
        fill="none"
        stroke="#334155"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />

      {/* Score arc */}
      {pct > 0.005 && (
        <path
          d={arcPath(cx, cy, r, START, scoreEnd)}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color}80)` }}
        />
      )}

      {/* Percentage */}
      <text
        x={cx}
        y={cy + 6}
        textAnchor="middle"
        fill="white"
        fontSize={size * 0.175}
        fontWeight="700"
        fontFamily="Inter, sans-serif"
      >
        {Math.round(pct * 100)}%
      </text>

      {/* PASS / WARN / FAIL */}
      <text
        x={cx}
        y={cy + 22}
        textAnchor="middle"
        fill={color}
        fontSize={size * 0.085}
        fontWeight="600"
        fontFamily="Inter, sans-serif"
        letterSpacing="1"
      >
        {scoreLabel(pct)}
      </text>
    </svg>
  );
}
