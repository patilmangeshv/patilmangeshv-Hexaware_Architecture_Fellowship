/**
 * Query Page
 * Ask a compliance question and get a grounded AI answer
 */

import { useState } from 'react';
import QueryInterface from '../components/query/QueryInterface.jsx';
import AnswerDisplay from '../components/query/AnswerDisplay.jsx';
import { useQuery } from '../hooks/useQuery.js';

export default function QueryPage() {
  const [submitted, setSubmitted] = useState(false);
  const { result, loading, error, submitQuery } = useQuery();

  async function handleSubmit(question, context) {
    setSubmitted(true);
    try {
      await submitQuery(question, context);
    } catch (e) {
      console.error('Query error:', e);
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 mb-1">
          Ask a Compliance Question
        </h1>
        <p className="text-sm text-slate-400">
          Query the compliance knowledge base. Retrieval + reranking + Gemini with citation enforcement.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input form */}
        <div className="lg:col-span-1">
          <div className="card">
            <h2 className="section-title mb-3">Ask Question</h2>
            <QueryInterface onSubmit={handleSubmit} loading={loading} />
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-2">
          {error && (
            <div className="bg-red-950/30 border border-red-700/50 rounded-lg p-4 text-red-200 text-sm">
              <strong>Error:</strong> {error}
            </div>
          )}
          {submitted && <AnswerDisplay result={result} loading={loading} />}
          {!submitted && (
            <div className="card text-center py-12 text-slate-400">
              <p className="text-sm">Enter a question to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
