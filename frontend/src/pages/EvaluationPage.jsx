/**
 * Evaluation Page
 * Run and view RAGAS evaluation on the golden Q&A set
 */

import { useState, useEffect } from 'react';
import { FlaskConical, PlayCircle, RotateCw } from 'lucide-react';
import RagasScorecard from '../components/eval/RagasScorecard.jsx';
import FailureModeRegister from '../components/eval/FailureModeRegister.jsx';
import { useEvaluation } from '../hooks/useEvaluation.js';
import { getTrustCanvas } from '../api/client.js';

export default function EvaluationPage() {
  const { scores, history, running, error, runEval, fetchScores } = useEvaluation();
  const [canvas, setCanvas] = useState(null);

  useEffect(() => {
    getTrustCanvas().then(setCanvas).catch(() => {});
  }, []);

  async function handleRunEval() {
    try {
      await runEval();
    } catch (e) {
      console.error('Eval error:', e);
    }
  }

  const failureModes = canvas?.failure_modes ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2 mb-1">
          <FlaskConical size={24} className="text-indigo-400" />
          RAGAS Evaluation
        </h1>
        <p className="text-sm text-slate-400">
          Benchmark the RAG pipeline on the 10-question golden evaluation set.
          Target: faithfulness ≥ 0.90 to pass.
        </p>
      </div>

      {/* Run button */}
      <button
        onClick={handleRunEval}
        disabled={running}
        className="btn-primary flex items-center gap-2"
      >
        {running ? (
          <>
            <RotateCw size={16} className="animate-spin" />
            Running RAGAS evaluation…
          </>
        ) : (
          <>
            <PlayCircle size={16} />
            Run Evaluation
          </>
        )}
      </button>

      {error && (
        <div className="bg-red-950/30 border border-red-700/50 rounded-lg p-4 text-red-200 text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Current scores */}
      <div>
        <h2 className="section-title">Latest Results</h2>
        <RagasScorecard scores={scores} />
      </div>

      {/* History */}
      {history.length > 0 && (
        <div>
          <h2 className="section-title">
            Evaluation History
            <span className="ml-2 text-xs font-normal text-slate-500 bg-slate-700 px-2 py-0.5 rounded">
              {history.length} runs
            </span>
          </h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="px-4 py-2 text-left font-semibold text-slate-400">Run At</th>
                  <th className="px-4 py-2 text-center font-semibold text-slate-400">Faithfulness</th>
                  <th className="px-4 py-2 text-center font-semibold text-slate-400">Answer Relevancy</th>
                  <th className="px-4 py-2 text-center font-semibold text-slate-400">Context Recall</th>
                  <th className="px-4 py-2 text-center font-semibold text-slate-400">Context Precision</th>
                  <th className="px-4 py-2 text-center font-semibold text-slate-400">RAGAS Score</th>
                  <th className="px-4 py-2 text-center font-semibold text-slate-400">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {history.map((h, i) => (
                  <tr key={i} className="hover:bg-slate-700/10">
                    <td className="px-4 py-2 text-slate-400">
                      {new Date(h.run_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-center">{(h.faithfulness * 100).toFixed(2)}%</td>
                    <td className="px-4 py-2 text-center">{(h.answer_relevancy * 100).toFixed(2)}%</td>
                    <td className="px-4 py-2 text-center">{(h.context_recall * 100).toFixed(2)}%</td>
                    <td className="px-4 py-2 text-center">{(h.context_precision * 100).toFixed(2)}%</td>
                    <td className="px-4 py-2 text-center font-bold text-indigo-300">
                      {(h.ragas_score * 100).toFixed(2)}%
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          h.passed
                            ? 'bg-emerald-900/30 text-emerald-300 border border-emerald-700/50'
                            : 'bg-red-900/30 text-red-300 border border-red-700/50'
                        }`}
                      >
                        {h.passed ? '✓ PASS' : '✗ FAIL'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Failure mode register */}
      <div>
        <h2 className="section-title">Failure Mode Register</h2>
        <FailureModeRegister modes={failureModes} />
      </div>
    </div>
  );
}
