import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  FlaskConical,
  ShieldCheck,
  Activity,
} from 'lucide-react';
import clsx from 'clsx';

const nav = [
  { to: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard'  },
  { to: '/query',      icon: MessageSquare,   label: 'Ask Question' },
  { to: '/evaluation', icon: FlaskConical,    label: 'Evaluation'  },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-700">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <ShieldCheck size={18} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-100 leading-tight">
              Compliance
            </p>
            <p className="text-xs text-slate-400">Knowledge Agent</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/60'
              )
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-slate-700">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Activity size={12} className="text-emerald-500" />
          <span>RAG · BGE · Gemini</span>
        </div>
        <p className="text-xs text-slate-600 mt-1">v1.0.0 · RAGAS eval ready</p>
      </div>
    </aside>
  );
}
