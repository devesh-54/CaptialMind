import React from 'react';
import { X, ArrowRight, ShieldAlert, Scale } from 'lucide-react';
import { PageId } from '../types/dashboard';
import { mockOptionCandidates } from '../data/mockData';

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
                Decision Audit & Reasoning Engine
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
            <div className="text-[10px] uppercase font-bold text-slate-500 font-mono">Selected AI Action</div>
            <div className="text-base font-bold text-emerald-400 font-mono">
              Pay Now (₹9,20,000)
            </div>
            <p className="text-xs text-slate-300 font-sans">
              Captures ₹23,000 discount before deadline (Aug 30, 2026). 32.4% annualized yield.
            </p>
          </div>

          {/* 2. Candidate Evaluation Scores (Spec §3 & §5 reuse) */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Scale className="w-4 h-4 text-blue-400" />
              <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider font-mono">
                Evaluated Candidates & Scores
              </h3>
            </div>
            <div className="space-y-2 text-xs font-mono">
              {mockOptionCandidates.map((cand) => (
                <div
                  key={cand.id}
                  className={`p-3 rounded border flex justify-between items-center ${
                    cand.selected
                      ? 'bg-blue-950/40 border-blue-800 text-blue-300 font-bold'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-200">{cand.action}</span>
                      {cand.selected && (
                        <span className="px-1.5 py-0.2 rounded text-[9px] bg-blue-500 text-white">SELECTED</span>
                      )}
                    </div>
                    <div className="text-[10px] text-slate-400 font-sans">{cand.costBenefit}</div>
                  </div>
                  <div className="text-right">
                    <span className={`font-bold ${cand.score >= 90 ? 'text-emerald-400' : 'text-slate-300'}`}>
                      Score: {cand.score}/100
                    </span>
                    <div className="text-[9px] text-slate-500">{cand.riskNote}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. Numbered Reasons with Real Rupee Values */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider font-mono">Decision Rationale</h3>
            <ol className="space-y-2 text-xs font-mono">
              <li className="p-3 bg-slate-900/80 border border-slate-800 rounded flex items-start space-x-2">
                <span className="font-bold text-blue-400">1.</span>
                <span className="text-slate-300 font-sans">
                  <strong className="text-slate-100 font-mono">32.4% Annualized Return:</strong> Early payment discount of 2.5% saves ₹23,000 against a 6-day acceleration.
                </span>
              </li>
              <li className="p-3 bg-slate-900/80 border border-slate-800 rounded flex items-start space-x-2">
                <span className="font-bold text-blue-400">2.</span>
                <span className="text-slate-300 font-sans">
                  <strong className="text-slate-100 font-mono">Safety Floor Preserved:</strong> Post-payment liquidity (₹33.2L) exceeds policy threshold (₹15.0L) by ₹18.2L.
                </span>
              </li>
              <li className="p-3 bg-slate-900/80 border border-slate-800 rounded flex items-start space-x-2">
                <span className="font-bold text-blue-400">3.</span>
                <span className="text-slate-300 font-sans">
                  <strong className="text-slate-100 font-mono">Strategic Priority (5/5):</strong> Delaying payment threatens Q3 raw material allocation contract.
                </span>
              </li>
            </ol>
          </div>

          {/* 4. Trade-off Synthesis */}
          <div className="space-y-2 bg-amber-950/30 border border-amber-800/50 p-3.5 rounded-lg text-xs font-mono">
            <div className="flex items-center text-amber-400 font-bold">
              <ShieldAlert className="w-4 h-4 mr-1.5" /> Trade-Off & Sensitivity Triggers
            </div>
            <p className="text-slate-300 text-[11px] font-sans leading-relaxed">
              Bank Finance option (Score 74) was rejected because ₹18,000 in interest costs exceeds the liquidity value since cash floor is not breached under Pay Now.
            </p>
          </div>

        </div>

        {/* 5. Deep-link to Scenario Simulator */}
        <div className="pt-4 border-t border-slate-800 space-y-2">
          <button
            onClick={() => {
              onClose();
              onNavigate('scenario-simulator');
            }}
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700 rounded text-xs font-mono font-semibold transition flex items-center justify-center space-x-2"
          >
            <span>Stress-Test this Decision in What-If Simulator</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
