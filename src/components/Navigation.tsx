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
  History 
} from 'lucide-react';

interface NavigationProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ currentPage, onSelectPage }) => {
  const navItems: { id: PageId; label: string; icon: React.ReactNode; badge?: string }[] = [
    { id: 'command-center', label: 'Command Center', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'invoices', label: 'Invoices', icon: <FileText className="w-4 h-4" />, badge: '5' },
    { id: 'receivables', label: 'Receivables', icon: <ArrowDownLeft className="w-4 h-4" /> },
    { id: 'suppliers', label: 'Suppliers', icon: <Building2 className="w-4 h-4" /> },
    { id: 'financing', label: 'Financing', icon: <Landmark className="w-4 h-4" /> },
    { id: 'scenario-simulator', label: 'What If?', icon: <Sliders className="w-4 h-4" />, badge: 'SIM' },
    { id: 'agent-activity', label: 'Agent Activity', icon: <Activity className="w-4 h-4" /> },
    { id: 'decision-history', label: 'Decision History', icon: <History className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 bg-[#0B0F17] border-r border-slate-800/80 p-4 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16">
      <nav className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
          Treasury Navigation
        </div>
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className={isActive ? 'text-blue-400' : 'text-slate-500'}>{item.icon}</span>
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-bold ${
                  isActive ? 'bg-blue-500/30 text-blue-300' : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Safety Status */}
      <div className="p-3 bg-[#0F172A] border border-slate-800/80 rounded-lg">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span>Liquidity Guard</span>
          <span className="text-emerald-400 font-bold">100% OK</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
          <div className="bg-emerald-500 h-1.5 rounded-full w-full"></div>
        </div>
        <p className="text-[10px] text-slate-500 mt-2 font-mono">Policy Floor: ₹15.0L</p>
      </div>
    </aside>
  );
};
