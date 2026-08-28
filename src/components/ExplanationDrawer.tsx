import React from 'react';
import { X, ArrowRight, ShieldAlert } from 'lucide-react';
import { PageId } from '../types/dashboard';

interface ExplanationDrawerProps {
  invoiceId: string | null;
  onClose: () => void;
  onNavigate: (page: PageId) => void;
}

export const ExplanationDrawer: React.FC<ExplanationDrawerProps> = ({ invoiceId, onClose, onNavigate }) => {
  if (!invoiceId) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-[#0B0F17] border-l border-slate-800 h-full p-6 overflow-y-auto flex flex-col justify-between shadow-2xl animate-in slide-in-from-right duration-200">
        
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between border-b border-slate-800 pb-4">
            <div>
              <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 text-[10px] font-mono font-bold uppercase border border-blue-800">
                Decision Audit & Reasoning
              </span>
              <h2 className="text-lg font-bold text-slate-100 mt-1 font-mono">{invoiceId}</h2>
              <p className="text-xs text-slate-400">Supplier: Tata Steel Processing (Strategic Tier-1)</p>
            </div>
            <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* 1. Chosen Action */}
          <div className="bg-[#0F172A] border border-slate-800 p-4 rounded-lg space-y-1">
            <div className="text-[10px] uppercase font-bold text-slate-500 font-mono">Recommended AI Action</div>
            <div className="text-base font-bold text-emerald-400 font-mono">
              Pay Now (₹9,20,000)
            </div>
            <p className="text-xs text-slate-300">
              Captures ₹23,000 discount before deadline (Aug 30, 2026).
            </p>
          </div>

          {/* 2. Numbered Reasons with Real Rupee Values */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider font-mono">Why the Agent Recommends This</h3>
            <ol className="space-y-2 text-xs font-mono">
              <li className="p-3 bg-slate-900/80 border border-slate-800 rounded flex items-start space-x-2">
                <span className="font-bold text-blue-400">1.</span>
                <span className="text-slate-300">
                  <strong className="text-slate-100">32.4% Annualized Return:</strong> Early payment discount of 2.5% saves ₹23,000 against a 6-day acceleration.
                </span>
              </li>
              <li className="p-3 bg-slate-900/80 border border-slate-800 rounded flex items-start space-x-2">
                <span className="font-bold text-blue-400">2.</span>
                <span className="text-slate-300">
                  <strong className="text-slate-100">Safety Floor Preserved:</strong> Post-payment liquidity (₹33.2L) exceeds policy threshold (₹15.0L) by ₹18.2L.
                </span>
              </li>
              <li className="p-3 bg-slate-900/80 border border-slate-800 rounded flex items-start space-x-2">
                <span className="font-bold text-blue-400">3.</span>
                <span className="text-slate-300">
                  <strong className="text-slate-100">Strategic Priority (5/5):</strong> Delaying payment threatens Q3 raw material allocation contract.
                </span>
              </li>
            </ol>
          </div>

          {/* 3. Alternatives Considered */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider font-mono">Alternatives Evaluated</h3>
            <div className="space-y-2 text-xs font-mono">
              <div className="p-2.5 bg-blue-950/40 border border-blue-800/60 rounded flex justify-between items-center">
                <div>
                  <span className="font-bold text-blue-400">Pay Now (Selected)</span>
                  <div className="text-[10px] text-slate-400">Captures discount, zero risk</div>
                </div>
                <span className="font-bold text-emerald-400">Score: 96/100</span>
              </div>
              <div className="p-2.5 bg-slate-900 border border-slate-800 rounded flex justify-between items-center opacity-70">
                <div>
                  <span className="text-slate-300">Pay at Maturity (Sept 5)</span>
                  <div className="text-[10px] text-slate-500">Forfeits ₹23,000 discount</div>
                </div>
                <span className="font-bold text-slate-400">Score: 61/100</span>
              </div>
              <div className="p-2.5 bg-slate-900 border border-slate-800 rounded flex justify-between items-center opacity-70">
                <div>
                  <span className="text-slate-300">Dynamic Bank Financing</span>
                  <div className="text-[10px] text-slate-500">Financing cost ₹4,100 reduces net savings</div>
                </div>
                <span className="font-bold text-slate-400">Score: 74/100</span>
              </div>
            </div>
          </div>

          {/* 4. What would change this decision */}
          <div className="space-y-2 bg-amber-950/30 border border-amber-800/50 p-3 rounded-lg text-xs font-mono">
            <div className="flex items-center text-amber-400 font-bold">
              <ShieldAlert className="w-4 h-4 mr-1.5" /> Sensitivity Triggers
            </div>
            <ul className="list-disc list-inside text-slate-300 space-y-1 text-[11px]">
              <li>If total available cash drops below ₹20.0L before Aug 30th</li>
              <li>If Flipkart receivable (₹18.0L) is delayed beyond 5 days</li>
            </ul>
          </div>

        </div>

        {/* 5. Deep-link to Scenario Simulator */}
        <div className="pt-4 border-t border-slate-800 space-y-2">
          <div className="text-xs text-slate-400">Test alternative scenarios:</div>
          <button
            onClick={() => {
              onClose();
              onNavigate('scenario-simulator');
            }}
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700 rounded text-xs font-mono font-semibold transition flex items-center justify-center space-x-2"
          >
            <span>Ask a "What-If" on this decision</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
