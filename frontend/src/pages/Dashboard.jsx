/**
 * Dashboard Page
 * RAGAS metric cards + Trust Boundary Canvas
 */

import { useState, useEffect } from 'react';
import { BarChart, AlertTriangle } from 'lucide-react';
import MetricCard from '../components/metrics/MetricCard.jsx';
import AverageProgress from '../components/metrics/AverageProgress.jsx';
import TrustBoundaryCanvas from '../components/trust/TrustBoundaryCanvas.jsx';
import { getEvalScores, getTrustCanvas } from '../api/client.js';

export default function Dashboard() {
  const [scores, setScores] = useState(null);
  const [canvas, setCanvas] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [scoresData, canvasData] = await Promise.all([
          getEvalScores(),
          getTrustCanvas(),
        ]);
        setScores(scoresData.latest);
        setCanvas(canvasData);
      } catch (e) {
        console.error('Failed to load dashboard:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-2 border-slate-600 border-t-indigo-500 mx-auto mb-4 animate-spin" />
          <p className="text-slate-400">Loading dashboard…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2 mb-1">
          <BarChart size={24} className="text-indigo-400" />
          Dashboard
        </h1>
        <p className="text-sm text-slate-400">
          RAGAS evaluation metrics and Trust Boundary architecture
        </p>
      </div>

      {/* No data notice */}
      {!scores && (
        <div className="bg-amber-950/30 border border-amber-700/50 rounded-lg p-4 flex gap-3">
          <AlertTriangle size={18} className="text-amber-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-200">
            <strong>No evaluation results yet.</strong> Run the RAGAS evaluation on the golden Q&A set
            to see scores. Go to the{' '}
            <span className="font-mono text-amber-100">Evaluation</span> tab.
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      {scores && (
        <>
          <div>
            <h2 className="section-title">
              <BarChart size={18} className="text-indigo-400" />
              RAGAS Metrics
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <MetricCard metric="faithfulness" score={scores.faithfulness} />
              <MetricCard metric="answer_relevancy" score={scores.answer_relevancy} />
              <MetricCard metric="context_recall" score={scores.context_recall} />
              <MetricCard metric="context_precision" score={scores.context_precision} />
              <MetricCard metric="ragas_score" score={scores.ragas_score} />
            </div>
          </div>

          <AverageProgress scores={scores} />
        </>
      )}

      {/* Trust Canvas */}
      <TrustBoundaryCanvas data={canvas} />
    </div>
  );
}
