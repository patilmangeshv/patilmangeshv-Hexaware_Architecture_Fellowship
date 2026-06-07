import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, RefreshCw, Database } from 'lucide-react';
import { getHealth, triggerIngest } from '../../api/client.js';

const PAGE_TITLES = {
  '/dashboard':  'Dashboard',
  '/query':      'Ask a Compliance Question',
  '/evaluation': 'RAGAS Evaluation',
};

export default function Header() {
  const { pathname } = useLocation();
  const [health, setHealth] = useState(null);
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState('');

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {});
  }, []);

  async function handleIngest() {
    setIngesting(true);
    setIngestMsg('');
    try {
      const r = await triggerIngest();
      setIngestMsg(`✓ ${r.documents_processed} docs · ${r.chunks_created} chunks`);
      const h = await getHealth();
      setHealth(h);
    } catch (e) {
      setIngestMsg(`✗ ${e.message}`);
    } finally {
      setIngesting(false);
    }
  }

  return (
    <header className="h-14 bg-slate-800 border-b border-slate-700 px-6 flex items-center justify-between shrink-0">
      {/* Title */}
      <div>
        <h1 className="text-base font-semibold text-slate-100">
          {PAGE_TITLES[pathname] ?? 'Compliance Agent'}
        </h1>
        {health && (
          <p className="text-xs text-slate-500 mt-0.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1 align-middle" />
            {health.collection_count.toLocaleString()} chunks in ChromaDB
          </p>
        )}
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {ingestMsg && (
          <span className="text-xs text-slate-400 hidden sm:block">{ingestMsg}</span>
        )}
        <button
          onClick={handleIngest}
          disabled={ingesting}
          title="Re-ingest documents from ./data/"
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-md bg-slate-700 hover:bg-slate-600
                     text-slate-300 transition-colors disabled:opacity-50"
        >
          {ingesting ? (
            <RefreshCw size={13} className="animate-spin" />
          ) : (
            <Database size={13} />
          )}
          {ingesting ? 'Ingesting…' : 'Re-ingest'}
        </button>
        <button className="w-8 h-8 rounded-lg bg-slate-700 hover:bg-slate-600 flex items-center justify-center transition-colors">
          <Bell size={15} className="text-slate-400" />
        </button>
      </div>
    </header>
  );
}
