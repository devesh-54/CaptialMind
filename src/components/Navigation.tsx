import React from 'react';
import { PageId } from '../types/dashboard';
import { 
  LayoutDashboard, 
  FileText, 
  ArrowDownLeft, 
  Building2, 
  Landmark, 
  Sliders, 
  Activity, 
  History,
  Database
} from 'lucide-react';

interface NavigationProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ currentPage, onSelectPage }) => {
  const navItems = [
    { id: 'command-center' as PageId, label: 'Command Center', icon: LayoutDashboard },
    { id: 'invoices' as PageId, label: 'Invoices', icon: FileText, badge: '5' },
    { id: 'receivables' as PageId, label: 'Receivables', icon: ArrowDownLeft },
    { id: 'suppliers' as PageId, label: 'Suppliers', icon: Building2 },
    { id: 'financing' as PageId, label: 'Financing', icon: Landmark },
    { id: 'scenario-simulator' as PageId, label: 'What If?', icon: Sliders, badge: 'SIM' },
    { id: 'agent-activity' as PageId, label: 'Agent Activity', icon: Activity },
    { id: 'decision-history' as PageId, label: 'Decision History', icon: History },
    { id: 'data-stream' as PageId, label: 'Data Ingestion', icon: Database, badge: 'LIVE' },
  ];

  return (
    <aside className="w-64 bg-[#090D16] border-r border-slate-800/80 flex flex-col justify-between select-none">
      <div className="p-4 space-y-6">
        <div>
          <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 mb-2 px-3">
            Treasury Navigation
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectPage(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-mono font-medium transition ${
                    isActive 
                      ? 'bg-blue-600/10 text-blue-400 border border-blue-500/30 shadow-sm' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      item.badge === 'LIVE' 
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800 animate-pulse'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      <div className="p-4 border-t border-slate-800/80 font-mono text-[11px]">
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span>Liquidity Guard</span>
            <span className="text-emerald-400 font-bold">100% OK</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full w-full"></div>
          </div>
          <div className="text-[10px] text-slate-500">
            Policy Floor: ₹15.0L
          </div>
        </div>
      </div>
    </aside>
  );
};
