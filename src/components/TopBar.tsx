import React from 'react';
import { RefreshCw, ChevronDown, Activity } from 'lucide-react';

interface TopBarProps {
  onReoptimize: () => void;
  isOptimizing: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({ onReoptimize, isOptimizing }) => {
  return (
    <header className="h-16 bg-[#0F172A]/95 border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-30 backdrop-blur-md">
      {/* Brand & Context */}
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-mono font-bold text-white shadow-lg shadow-blue-500/20 text-sm">
            CP
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-100 text-base tracking-tight">CashPilot</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                AI ENGINE
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono hidden sm:block">Autonomous Working-Capital Management</p>
          </div>
        </div>

        {/* Company Selector */}
        <div className="hidden md:flex items-center space-x-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-md cursor-pointer hover:border-slate-700 transition">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span className="text-xs font-medium text-slate-300">Acme Manufacturing Pvt Ltd</span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
        </div>
      </div>

      {/* Live Agent Controls */}
      <div className="flex items-center space-x-4">
        {/* Agent Status Pill */}
        <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-mono font-bold text-emerald-400 tracking-wider">ACTIVE</span>
          <span className="text-slate-600 text-xs">•</span>
          <span className="text-[11px] text-slate-400 font-mono">Last optimized 14s ago</span>
        </div>

        {/* Re-optimize CTA */}
        <button
          onClick={onReoptimize}
          disabled={isOptimizing}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition shadow-md shadow-blue-600/20 ${
            isOptimizing ? 'opacity-70 cursor-not-allowed' : ''
          }`}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isOptimizing ? 'animate-spin' : ''}`} />
          <span>{isOptimizing ? 'Re-optimizing...' : 'Re-optimize'}</span>
        </button>
      </div>
    </header>
  );
};
