import React, { useState, useEffect } from 'react';
import { mockReceivables } from '../data/mockData';
import { formatINR } from '../utils/formatters';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { fetchReceivablesData } from '../services/api';

export const Receivables: React.FC = () => {
  const [receivables, setReceivables] = useState<any[]>(mockReceivables);

  useEffect(() => {
    async function load() {
      const data = await fetchReceivablesData();
      if (data) {
        setReceivables(data);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Receivables & Cash Inflow Risk</h1>
        <p className="text-xs text-slate-400">Making Collection Uncertainty Concrete & Visible for Treasury Planning</p>
      </div>

      <div className="bg-[#0F172A] border border-slate-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-[11px] font-mono font-bold uppercase text-slate-400">
                <th className="py-3 px-4">Receivable ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Expected Date</th>
                <th className="py-3 px-4">Collection Probability</th>
                <th className="py-3 px-4">Expected Delay</th>
                <th className="py-3 px-4">Inflow Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
              {receivables.map((rec) => (
                <tr key={rec.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-4 font-bold text-blue-400">{rec.id}</td>
                  <td className="py-3 px-4 font-semibold text-slate-200 font-sans">{rec.customerName}</td>
                  <td className="py-3 px-4 text-right font-bold text-slate-100">{formatINR(rec.amount)}</td>
                  <td className="py-3 px-4 text-slate-300">{rec.expectedDate}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            rec.collectionProbability >= 90 ? 'bg-emerald-500' : rec.collectionProbability >= 75 ? 'bg-amber-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${rec.collectionProbability}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-200">{rec.collectionProbability}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    {rec.expectedDelayDays > 0 ? (
                      <span className="text-amber-400 font-bold">+{rec.expectedDelayDays} days</span>
                    ) : (
                      <span className="text-emerald-400">On Schedule</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border flex items-center w-fit space-x-1 ${
                      rec.status === 'On Time' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' :
                      rec.status === 'Slight Delay' ? 'bg-amber-950 text-amber-400 border-amber-800' :
                      'bg-red-950 text-red-400 border-red-800'
                    }`}>
                      {rec.status === 'On Time' && <CheckCircle className="w-3 h-3 mr-1" />}
                      {rec.status === 'Slight Delay' && <Clock className="w-3 h-3 mr-1" />}
                      {rec.status === 'At Risk' && <AlertCircle className="w-3 h-3 mr-1" />}
                      <span>{rec.status}</span>
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
