import React, { useState, useEffect } from 'react';
import { mockInvoices } from '../data/mockData';
import { formatINR, getActionColor } from '../utils/formatters';
import { Filter, ArrowUpDown, Info } from 'lucide-react';
import { fetchInvoicesData } from '../services/api';

interface InvoicesProps {
  onOpenDrawer: (invoiceId: string) => void;
}

export const Invoices: React.FC<InvoicesProps> = ({ onOpenDrawer }) => {
  const [filterAction, setFilterAction] = useState<string>('ALL');
  const [sortByScore, setSortByScore] = useState<boolean>(true);
  const [invoices, setInvoices] = useState<any[]>(mockInvoices);

  useEffect(() => {
    async function load() {
      const data = await fetchInvoicesData();
      if (data) {
        setInvoices(data);
      }
    }
    load();
  }, []);

  const normalizeScore = (rawScore: any) => {
    const num = Number(rawScore);
    if (isNaN(num)) return 85;
    if (num >= 1 && num <= 99) return Math.round(num);
    if (num > 99) return Math.min(98, Math.max(75, Math.round(num / 10)));
    const normalized = Math.round(50 + (num / 8.0));
    return Math.min(95, Math.max(5, normalized));
  };

  let displayedInvoices = invoices.map((inv: any) => ({
    ...inv,
    normalizedPriorityScore: normalizeScore(inv.priorityScore)
  }));

  if (filterAction !== 'ALL') {
    displayedInvoices = displayedInvoices.filter(i => i.aiAction === filterAction);
  }

  if (sortByScore) {
    displayedInvoices.sort((a, b) => b.normalizedPriorityScore - a.normalizedPriorityScore);
  }

  return (
    <div className="space-y-6 pb-12 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-sans">Invoice Intelligence</h1>
          <p className="text-xs text-slate-400 font-sans">AI Priority Scoring and Action Recommendations for Working Capital Optimization</p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-md">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="bg-transparent text-slate-200 outline-none cursor-pointer font-mono"
            >
              <option value="ALL">All Actions</option>
              <option value="Pay Now">Pay Now</option>
              <option value="Pay at Maturity">Pay at Maturity</option>
              <option value="Finance">Finance</option>
              <option value="Delay">Delay</option>
            </select>
          </div>

          <button
            onClick={() => setSortByScore(!sortByScore)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md border font-mono ${
              sortByScore ? 'bg-blue-950/60 text-blue-400 border-blue-800' : 'bg-slate-900 text-slate-400 border-slate-800'
            }`}
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
            <span>Sort: Priority Score</span>
          </button>
        </div>
      </div>

      <div className="bg-[#0F172A] border border-slate-800 rounded-lg overflow-hidden backdrop-blur-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-[11px] font-mono font-bold uppercase text-slate-400">
                <th className="py-3 px-4">Invoice ID</th>
                <th className="py-3 px-4">Supplier</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Due Date</th>
                <th className="py-3 px-4">Discount</th>
                <th className="py-3 px-4">Priority Score</th>
                <th className="py-3 px-4">AI Action</th>
                <th className="py-3 px-4 text-center">Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
              {displayedInvoices.map((inv: any) => (
                <tr 
                  key={inv.id} 
                  onClick={() => onOpenDrawer(inv.id)}
                  className="hover:bg-slate-800/40 transition cursor-pointer group"
                >
                  <td className="py-3 px-4 font-bold text-blue-400 group-hover:underline">{inv.id}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-200 font-sans">{inv.supplierName}</div>
                    <div className="text-[10px] text-slate-500">{inv.supplierCategory}</div>
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-slate-100">{formatINR(inv.amount)}</td>
                  <td className="py-3 px-4 text-slate-300">{inv.dueDate}</td>
                  <td className="py-3 px-4">
                    {inv.discountPct > 0 ? (
                      <span className="text-emerald-400 font-bold">{inv.discountPct}% ({inv.discountDeadline})</span>
                    ) : (
                      <span className="text-slate-500">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            inv.normalizedPriorityScore >= 80 ? 'bg-emerald-500' : inv.normalizedPriorityScore >= 50 ? 'bg-blue-500' : 'bg-amber-500'
                          }`}
                          style={{ width: `${inv.normalizedPriorityScore}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-200">{inv.normalizedPriorityScore}/100</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-1 rounded text-[11px] font-bold border ${getActionColor(inv.aiAction)}`}>
                      {inv.aiAction}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <button className="p-1 text-slate-500 hover:text-blue-400 transition">
                      <Info className="w-4 h-4" />
                    </button>
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
