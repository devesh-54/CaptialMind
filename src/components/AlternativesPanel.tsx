import React from 'react';
import { OptionCandidate } from '../types/dashboard';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';
import { CheckCircle2, ShieldAlert, ArrowUpRight, Scale } from 'lucide-react';

interface AlternativesPanelProps {
  candidates: OptionCandidate[];
  selectedCandidateId: string;
  previewCandidateId: string | null;
  onSelectPreview: (candidateId: string | null) => void;
}

export const AlternativesPanel: React.FC<AlternativesPanelProps> = ({
  candidates,
  selectedCandidateId,
  previewCandidateId,
  onSelectPreview,
}) => {
  const activeCandidate = candidates.find((c) => c.id === (previewCandidateId || selectedCandidateId)) || candidates[0];

  return (
    <div className="bg-[#0F172A] border-2 border-slate-700/80 rounded-lg p-5 space-y-4 shadow-xl">
      {/* Header & Section Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Scale className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Candidate Alternatives & 30-Day Impact Matrix
          </h3>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-950 text-blue-400 border border-blue-800">
            5 Evaluated
          </span>
        </div>

        {previewCandidateId && (
          <button
            onClick={() => onSelectPreview(null)}
            className="text-[11px] font-mono text-blue-400 hover:text-blue-300 font-semibold underline flex items-center"
          >
            ← Reset to Recommended Plan
          </button>
        )}
      </div>

      {/* Horizontal Option Candidate Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {candidates.map((cand) => {
          const isSelected = cand.id === selectedCandidateId;
          const isPreviewed = cand.id === previewCandidateId;
          const isHighlighted = isSelected || isPreviewed;

          return (
            <div
              key={cand.id}
              onClick={() => onSelectPreview(cand.id === selectedCandidateId ? null : cand.id)}
              className={`rounded-lg p-3 cursor-pointer transition-all duration-200 flex flex-col justify-between space-y-2 border ${
                isSelected
                  ? 'bg-blue-950/40 border-2 border-blue-500 shadow-md shadow-blue-500/10'
                  : isPreviewed
                  ? 'bg-purple-950/40 border-2 border-purple-500'
                  : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              {/* Top Title & Score */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold text-slate-200 truncate">{cand.action}</span>
                  {isSelected && (
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-blue-500 text-white flex items-center">
                      <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" /> Selected
                    </span>
                  )}
                </div>

                {/* Score bar */}
                <div className="flex items-center space-x-1.5 font-mono text-[10px]">
                  <span className="text-slate-400">Score</span>
                  <div className="flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        cand.score >= 90
                          ? 'bg-emerald-500'
                          : cand.score >= 70
                          ? 'bg-blue-500'
                          : cand.score >= 50
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${cand.score}%` }}
                    ></div>
                  </div>
                  <span className="font-bold text-slate-200">{cand.score}</span>
                </div>
              </div>

              {/* Cost / Benefit */}
              <p className="text-[10px] text-slate-300 font-mono leading-tight min-h-[24px]">
                {cand.costBenefit}
              </p>

              {/* Mini Sparkline Chart (60x24) */}
              <div className="h-8 w-full bg-slate-950/60 rounded p-1 border border-slate-800/80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={cand.sparklineData} margin={{ top: 2, right: 2, left: 2, bottom: 2 }}>
                    <Area
                      type="monotone"
                      dataKey="cash"
                      stroke={cand.breachesFloor ? '#EF4444' : isSelected ? '#3B82F6' : '#A855F7'}
                      strokeWidth={1.5}
                      fill={cand.breachesFloor ? 'rgba(239, 68, 68, 0.15)' : 'rgba(59, 130, 246, 0.15)'}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Risk Note */}
              <div
                className={`text-[9px] font-mono flex items-center space-x-1 ${
                  cand.breachesFloor ? 'text-red-400 font-bold' : 'text-slate-400'
                }`}
              >
                {cand.breachesFloor && <ShieldAlert className="w-3 h-3 text-red-400 shrink-0" />}
                <span className="truncate" title={cand.riskNote}>
                  {cand.riskNote}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Synthesis Rationale Line */}
      <div className="bg-slate-900/90 border border-slate-800 rounded p-3 text-xs text-slate-300 font-sans leading-relaxed">
        <strong className="text-blue-400 font-mono font-bold uppercase tracking-wide mr-1.5">
          AI Trade-Off Synthesis:
        </strong>
        Pay Now scores highest (96/100) because it captures ₹33,440 in early settlement discounts while keeping the 30-day reserve floor breach risk at zero; Bank Credit Line (74/100) preserves cash today but incurs ₹18,000 in interest costs for no net liquidity benefit; Delay Payment (32/100) breaches the ₹15.0L policy reserve floor on Day 18.
      </div>
    </div>
  );
};
