import React from 'react';
import { mockDecisionHistory } from '../data/mockData';
import { formatINR } from '../utils/formatters';
import { Link2, ShieldCheck, Clock, CheckCircle } from 'lucide-react';

interface DecisionHistoryProps {
  onOpenDrawer: (id: string) => void;
}

export const DecisionHistory: React.FC<DecisionHistoryProps> = ({ onOpenDrawer }) => {
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Autonomous Decision History Log</h1>
        <p className="text-xs text-slate-400">Complete Audit Trail of Working Capital Allocation & Superseded Version Linkage</p>
      </div>

      <div className="bg-[#0F172A] border border-slate-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-[11px] font-mono font-bold uppercase text-slate-400">
                <th className="py-3 px-4">Decision ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Trigger Event</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
              {mockDecisionHistory.map((dec) => (
                <tr 
                  key={dec.id} 
                  onClick={() => onOpenDrawer('INV-2026-081')}
                  className="hover:bg-slate-800/40 transition cursor-pointer group"
                >
                  <td className="py-3 px-4 font-bold text-blue-400 group-hover:underline">
                    <div className="flex items-center space-x-1.5">
                      <span>{dec.id}</span>
                      {dec.version && <span className="text-[10px] text-slate-500 font-normal">({dec.version})</span>}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{dec.timestamp}</td>
                  <td className="py-3 px-4 text-slate-300 font-sans">{dec.triggerEvent}</td>
                  <td className="py-3 px-4 font-bold text-slate-100 font-sans">
                    <div className="flex items-center space-x-2">
                      {dec.supersededBy && (
                        <span title={`Superseded by ${dec.supersededBy}`}>
                          <Link2 className="w-3.5 h-3.5 text-amber-400" />
                        </span>
                      )}
                      <span>{dec.decision}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-slate-100">{formatINR(dec.amount)}</td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">{dec.confidence}%</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      dec.status === 'Executed' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' :
                      dec.status === 'Pending Approval' ? 'bg-amber-950 text-amber-400 border-amber-800' :
                      'bg-slate-800 text-slate-400 border-slate-700'
                    }`}>
                      {dec.status}
                    </span>
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
