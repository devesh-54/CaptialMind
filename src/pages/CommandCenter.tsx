import React from 'react';
import { formatINR } from '../utils/formatters';
import { 
  CheckCircle2, 
  HelpCircle, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { mockActivityFeed, mockInvoices } from '../data/mockData';
import { PageId } from '../types/dashboard';

interface CommandCenterProps {
  onOpenDrawer: (invoiceId: string) => void;
  onNavigate: (page: PageId) => void;
}

const forecastData = [
  { day: 'Aug 28', cash: 48.2, floor: 15.0, pessimistic: 48.2 },
  { day: 'Aug 30', cash: 38.8, floor: 15.0, pessimistic: 35.2 },
  { day: 'Sep 02', cash: 42.1, floor: 15.0, pessimistic: 33.0 },
  { day: 'Sep 05', cash: 36.5, floor: 15.0, pessimistic: 24.5 },
  { day: 'Sep 08', cash: 29.4, floor: 15.0, pessimistic: 16.1 },
  { day: 'Sep 12', cash: 34.0, floor: 15.0, pessimistic: 18.2 },
  { day: 'Sep 18', cash: 41.5, floor: 15.0, pessimistic: 28.0 },
  { day: 'Sep 25', cash: 52.0, floor: 15.0, pessimistic: 39.5 },
];

export const CommandCenter: React.FC<CommandCenterProps> = ({ onOpenDrawer, onNavigate }) => {
  return (
    <div className="space-y-6 pb-12">
      
      {/* 4.1 KPI STRIP (6 Cards in single row) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-[#0F172A] border border-slate-800 p-3.5 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Available Cash</span>
          <div className="text-lg font-mono font-bold text-slate-100 mt-1">₹48.2L</div>
          <div className="text-[11px] text-emerald-400 font-mono mt-1">
            ↑ ₹3.5L vs last week
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-800 p-3.5 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Protected Cash</span>
          <div className="text-lg font-mono font-bold text-slate-100 mt-1">₹15.0L</div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">Policy Floor Level</div>
        </div>

        <div className="bg-[#0F172A] border border-slate-800 p-3.5 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Deployable Capital</span>
          <div className="text-lg font-mono font-bold text-blue-400 mt-1">₹33.2L</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">3 obligations queued</div>
        </div>

        <div className="bg-[#0F172A] border border-slate-800 p-3.5 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">30-Day Risk</span>
          <div className="mt-1 flex items-center">
            <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              LOW
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">Safety margin 121%</div>
        </div>

        <div className="bg-[#0F172A] border border-slate-800 p-3.5 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">WC Efficiency</span>
          <div className="text-lg font-mono font-bold text-slate-100 mt-1">88/100</div>
          <div className="text-[11px] text-emerald-400 font-mono mt-1">Top 10% Industry</div>
        </div>

        <div className="bg-[#0F172A] border border-slate-800 p-3.5 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Financing Exposure</span>
          <div className="text-lg font-mono font-bold text-slate-100 mt-1">₹12.5L</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">2 active credit lines</div>
        </div>
      </div>

      {/* 4.2 AI RECOMMENDATION HERO CARD */}
      <div className="bg-[#0F172A] border-l-4 border-l-blue-500 border-y border-r border-slate-800 rounded-lg p-6 relative overflow-hidden shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          
          <div className="space-y-3 flex-1">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider flex items-center space-x-1 font-mono">
                <Sparkles className="w-3.5 h-3.5 mr-1" /> AI Decision Recommendation
              </span>
              <div className="flex items-center text-xs text-slate-400 font-mono" title="Model certainty based on 90-day cash flow stability">
                <span>94% Confidence</span>
                <HelpCircle className="w-3.5 h-3.5 ml-1 text-slate-500" />
              </div>
            </div>

            <h2 className="text-2xl font-bold text-slate-100 tracking-tight">
              Allocate <span className="font-mono text-blue-400">₹18.4L</span> today to capture <span className="font-mono text-emerald-400">₹33,440</span> early discounts
            </h2>

            {/* Allocation breakdown */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800 font-mono text-xs">
              <div className="flex justify-between items-center px-2 py-1 bg-slate-800/50 rounded">
                <span className="text-slate-400">Tata Steel (Pay Now)</span>
                <span className="text-emerald-400 font-bold">₹9.2L</span>
              </div>
              <div className="flex justify-between items-center px-2 py-1 bg-slate-800/50 rounded">
                <span className="text-slate-400">Apex Logistics (Pay Now)</span>
                <span className="text-emerald-400 font-bold">₹5.8L</span>
              </div>
              <div className="flex justify-between items-center px-2 py-1 bg-slate-800/50 rounded">
                <span className="text-slate-400">Retain Safety Buffer</span>
                <span className="text-blue-400 font-bold">₹3.4L</span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Executing these payments today captures a 2.5% discount on Tata Steel (annualized return 32.4%) and protects Q3 freight dispatch with Apex Logistics, while preserving ₹33.2L deployable cash—well above your ₹15.0L policy reserve floor.
            </p>
          </div>

          {/* Actions & Lifecycle */}
          <div className="flex flex-col justify-between space-y-4 border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-6">
            
            <div className="space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">Status Lifecycle</div>
              <div className="flex items-center space-x-1.5 text-xs font-mono">
                <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">Recommended</span>
                <span className="text-slate-600">→</span>
                <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60 font-semibold">Pending Approval</span>
                <span className="text-slate-600">→</span>
                <span className="text-slate-600">Executed</span>
              </div>
            </div>

            <div className="space-y-2">
              <button 
                onClick={() => onOpenDrawer('INV-2026-081')}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-md font-semibold text-xs transition shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve Plan (₹18.4L)</span>
              </button>

              <div className="flex space-x-2">
                <button 
                  onClick={() => onNavigate('scenario-simulator')}
                  className="flex-1 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium border border-slate-700 transition"
                >
                  Simulate Alternatives
                </button>
                <button 
                  onClick={() => onOpenDrawer('INV-2026-081')}
                  className="py-2 px-3 text-xs text-blue-400 hover:text-blue-300 font-medium underline"
                >
                  Why this decision?
                </button>
              </div>
            </div>

          </div>

        </div>
      </div>

      {/* 4.3 CAPITAL ALLOCATION WATERFALL */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5">
        <div className="flex justify-between items-center mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Capital Flow Waterfall</span>
          <span className="text-xs font-mono text-slate-500">Total Capital: ₹48.2L</span>
        </div>
        <div className="w-full h-8 bg-slate-900 rounded-lg flex overflow-hidden p-1 gap-1 border border-slate-800">
          <div style={{ width: '31.1%' }} className="bg-slate-700 rounded text-[10px] font-mono text-slate-200 flex items-center justify-center font-bold" title="Reserved Floor ₹15L">
            Reserve ₹15.0L
          </div>
          <div style={{ width: '38.1%' }} className="bg-emerald-600/80 rounded text-[10px] font-mono text-emerald-100 flex items-center justify-center font-bold" title="Recommended Payments ₹18.4L">
            Deploy ₹18.4L
          </div>
          <div style={{ width: '30.8%' }} className="bg-blue-600/40 rounded text-[10px] font-mono text-blue-200 flex items-center justify-center font-bold" title="Remaining Liquidity ₹14.8L">
            Buffer ₹14.8L
          </div>
        </div>
      </div>

      {/* 4.4 30-DAY CASH FORECAST CHART */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-200">30-Day Liquidity Projection</h3>
            <p className="text-xs text-slate-400">Comparing expected cash position vs pessimistic receivable delay scenario</p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="flex items-center text-blue-400"><span className="w-2.5 h-2.5 bg-blue-500 rounded-full mr-1.5"></span>Expected</span>
            <span className="flex items-center text-amber-400"><span className="w-2.5 h-2.5 bg-amber-500 rounded-full mr-1.5"></span>Pessimistic</span>
            <span className="flex items-center text-red-400"><span className="w-2.5 h-0.5 bg-red-500 mr-1.5"></span>Floor ₹15L</span>
          </div>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecastData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${v}L`} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#090D16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px', color: '#F8FAFC' }}
                formatter={(value: any) => [`₹${value}L`, 'Cash Balance']}
              />
              <ReferenceLine y={15.0} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Policy Reserve Floor (₹15.0L)', fill: '#EF4444', fontSize: 10, position: 'insideBottomRight' }} />
              <Area type="monotone" dataKey="cash" stroke="#3B82F6" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCash)" />
              <Area type="monotone" dataKey="pessimistic" stroke="#F59E0B" strokeWidth={1.5} strokeDasharray="4 4" fill="transparent" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4.5 BOTTOM ROW: OBLIGATIONS + LIVE FEED */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Upcoming Obligations */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-200">Upcoming Obligations (Next 5)</h3>
            <button onClick={() => onNavigate('invoices')} className="text-xs text-blue-400 hover:underline flex items-center font-mono">
              View all <ArrowRight className="w-3 h-3 ml-1" />
            </button>
          </div>
          <div className="divide-y divide-slate-800">
            {mockInvoices.slice(0, 4).map((inv) => (
              <div key={inv.id} className="py-2.5 flex items-center justify-between text-xs font-mono">
                <div>
                  <div className="font-semibold text-slate-200">{inv.supplierName}</div>
                  <div className="text-[11px] text-slate-500">Due {inv.dueDate}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-100">{formatINR(inv.amount)}</div>
                  <span className={`px-1.5 py-0.5 text-[10px] rounded border ${inv.aiAction === 'Pay Now' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                    {inv.aiAction}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Activity Feed */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-200">Agent Activity Stream</h3>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse"></span> Live Sync
            </span>
          </div>
          <div className="space-y-3">
            {mockActivityFeed.map((act) => (
              <div key={act.id} className="flex space-x-3 text-xs">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-950 text-blue-400 border border-blue-800/60 h-fit">
                  {act.stage}
                </span>
                <div className="flex-1">
                  <div className="flex justify-between">
                    <span className="font-semibold text-slate-200">{act.title}</span>
                    <span className="text-[10px] font-mono text-slate-500">{act.timestamp}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">{act.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
