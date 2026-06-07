/**
 * QueryInterface — Ask a compliance question
 * With optional DDD context selector
 */

import { useState } from 'react';
import { Search, Loader } from 'lucide-react';
import clsx from 'clsx';

const CONTEXTS = [
  { value: null, label: 'All Contexts' },
  { value: 'Policy', label: 'Policy' },
  { value: 'Audit', label: 'Audit Findings' },
  { value: 'Regulation', label: 'Regulatory' },
];

export default function QueryInterface({ onSubmit, loading = false }) {
  const [question, setQuestion] = useState('');
  const [context, setContext] = useState(null);

  function handleSubmit(e) {
    e.preventDefault();
    if (!question.trim()) return;
    onSubmit(question, context);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Context selector */}
      <div className="flex gap-2">
        <label htmlFor="context" className="label">
          Filter:
        </label>
        <div className="flex gap-2 flex-wrap">
          {CONTEXTS.map((c) => (
            <button
              key={c.value}
              type="button"
              onClick={() => setContext(c.value)}
              className={clsx(
                'px-3 py-1 text-xs font-medium rounded-lg transition-all duration-150',
                context === c.value
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              )}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Question input */}
      <div>
        <label className="label mb-2 block">Your Question</label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="E.g., What are the KYC requirements for onboarding a new customer?"
          rows={4}
          className="input font-sm"
          disabled={loading}
        />
        <p className="text-xs text-slate-500 mt-1">
          {question.length}/2000 characters
        </p>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!question.trim() || loading}
        className="btn-primary w-full justify-center"
      >
        {loading ? <Loader size={16} className="animate-spin" /> : <Search size={16} />}
        {loading ? 'Retrieving context…' : 'Ask Compliance Officer'}
      </button>
    </form>
  );
}
