import React, { useState, useEffect } from 'react';
import { mockDecisionHistory } from '../data/mockData';
import { formatINR } from '../utils/formatters';
import { Link2, ShieldCheck, Clock, CheckCircle } from 'lucide-react';
import { fetchDecisionHistoryData } from '../services/api';

interface DecisionHistoryProps {
  onOpenDrawer: (id: string) => void;
}

export const DecisionHistory: React.FC<DecisionHistoryProps> = ({ onOpenDrawer }) => {
  const [decisions, setDecisions] = useState<any[]>(mockDecisionHistory);

  useEffect(() => {
    async function load() {
      const data = await fetchDecisionHistoryData();
      if (data) {
        setDecisions(data);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6 pb-12 font-mono">
      <div>
        <h1 className="text-xl font-bold text-slate-100 font-sans">Autonomous Decision History Log</h1>
        <p className="text-xs text-slate-400">Complete Audit Trail of Working Capital Allocation & Superseded Version Linkage</p>
      </div>

      <div className="bg-[#0F172A] border border-slate-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-[11px] font-bold uppercase text-slate-400">
                <th className="py-3 px-4">Decision ID</th>
                <th className="py-3 px-4">Timestamp & Trigger</th>
                <th className="py-3 px-4">Recommended Decision</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Audit Linkage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {decisions.map((dec) => (
                <tr key={dec.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-4 font-bold text-blue-400">{dec.id}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-slate-200 font-sans">{dec.triggerEvent}</div>
                    <div className="text-[10px] text-slate-500">{dec.timestamp}</div>
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-200">{dec.decision}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{formatINR(dec.amount)}</td>
                  <td className="py-3.5 px-4 font-bold text-emerald-400">{dec.confidence}%</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      dec.status === 'Pending Approval' ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-emerald-950 text-emerald-400 border-emerald-800'
                    }`}>
                      {dec.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    {dec.supersededBy ? (
                      <span className="text-slate-500 text-[10px] flex items-center">
                        <Link2 className="w-3 h-3 mr-1 text-slate-500" />
                        Superseded by <strong className="text-slate-300 ml-1">{dec.supersededBy}</strong>
                      </span>
                    ) : (
                      <button
                        onClick={() => onOpenDrawer('INV00002')}
                        className="text-blue-400 hover:text-blue-300 underline font-bold text-[11px] flex items-center"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 mr-1" /> View Full Rationale
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
