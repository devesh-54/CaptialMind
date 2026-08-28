import React, { useState } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  CheckCircle2, 
  HelpCircle, 
  Sparkles,
  ArrowRight,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine, LineChart, Line } from 'recharts';
import { mockActivityFeed, mockInvoices, mockOptionCandidates } from '../data/mockData';
import { PageId, OptionCandidate } from '../types/dashboard';
import { AlternativesPanel } from '../components/AlternativesPanel';

interface CommandCenterProps {
  onOpenDrawer: (invoiceId: string) => void;
  onNavigate: (page: PageId) => void;
}

const baselineForecastData = [
  { day: 'Aug 28', cash: 48.2, pessimistic: 48.2 },
  { day: 'Aug 30', cash: 38.8, pessimistic: 35.2 },
  { day: 'Sep 02', cash: 42.1, pessimistic: 33.0 },
  { day: 'Sep 05', cash: 36.5, pessimistic: 24.5 },
  { day: 'Sep 08', cash: 29.4, pessimistic: 16.1 },
  { day: 'Sep 12', cash: 34.0, pessimistic: 18.2 },
  { day: 'Sep 18', cash: 41.5, pessimistic: 28.0 },
  { day: 'Sep 25', cash: 52.0, pessimistic: 39.5 },
];

export const CommandCenter: React.FC<CommandCenterProps> = ({ onOpenDrawer, onNavigate }) => {
  const [previewCandidateId, setPreviewCandidateId] = useState<string | null>(null);

  const activeCandidate = mockOptionCandidates.find(c => c.id === previewCandidateId);

  // Combine baseline chart with preview candidate overlay if selected
  const chartData = baselineForecastData.map((point, idx) => {
    let previewCash = point.cash;
    if (activeCandidate && activeCandidate.sparklineData[idx]) {
      previewCash = activeCandidate.sparklineData[idx].cash;
    }
    return {
      ...point,
      previewCash: activeCandidate ? previewCash : undefined,
    };
  });

  return (
    <div className="space-y-8 pb-12">
      
      {/* 2. DECLUTTERED KPI STRIP (~20px gap) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-5">
        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Available Cash</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">₹48.2L</div>
          <div className="text-[11px] text-emerald-400 font-mono mt-1">
            ↑ ₹3.5L vs last week
          </div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Protected Cash</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">₹15.0L</div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">Policy Reserve Floor</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Deployable Capital</span>
          <div className="text-xl font-mono font-bold text-blue-400 mt-1">₹33.2L</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">3 obligations queued</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">30-Day Risk</span>
          <div className="mt-1 flex items-center">
            <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              LOW
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">Safety margin 121%</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">WC Efficiency</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">88/100</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Optimized Schedule</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Financing Exposure</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">₹12.5L</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Available Credit Line</div>
        </div>
      </div>

      {/* 2. REFINED HERO CARD (Dedicated status lifecycle strip + Breathing room) */}
      <div className="bg-[#0F172A] border-l-4 border-l-blue-500 border-y border-r border-slate-800 rounded-lg overflow-hidden shadow-xl">
        
        {/* Top Status Lifecycle Strip */}
        <div className="bg-slate-900/90 px-6 py-2 border-b border-slate-800 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center space-x-2">
            <span className="text-slate-400 uppercase text-[10px] font-bold">Decision Lifecycle:</span>
            <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 font-semibold">Recommended</span>
            <span className="text-slate-600">→</span>
            <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60 font-semibold">Pending Approval</span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-600">Executed</span>
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-slate-400" title="Model certainty based on 90-day cash flow stability">
            <span>94% Confidence</span>
            <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
          </div>
        </div>

        {/* Hero Content Body */}
        <div className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          
          <div className="space-y-4 flex-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider flex items-center font-mono">
                <Sparkles className="w-3.5 h-3.5 mr-1.5" /> AI Priority Recommendation
              </span>
            </div>

            <h2 className="text-2xl lg:text-3xl font-bold text-slate-100 tracking-tight">
              Allocate <span className="font-mono text-blue-400">₹18.4L</span> today to capture <span className="font-mono text-emerald-400">₹33,440</span> early discounts
            </h2>

            {/* Pill breakdown */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800 font-mono text-xs">
              <div className="flex justify-between items-center px-2.5 py-1.5 bg-slate-800/50 rounded">
                <span className="text-slate-400">Tata Steel (Pay Now)</span>
                <span className="text-emerald-400 font-bold">₹9.2L</span>
              </div>
              <div className="flex justify-between items-center px-2.5 py-1.5 bg-slate-800/50 rounded">
                <span className="text-slate-400">Apex Logistics (Pay Now)</span>
                <span className="text-emerald-400 font-bold">₹5.8L</span>
              </div>
              <div className="flex justify-between items-center px-2.5 py-1.5 bg-slate-800/50 rounded">
                <span className="text-slate-400">Retain Safety Buffer</span>
                <span className="text-blue-400 font-bold">₹3.4L</span>
              </div>
            </div>

            {/* Reasoning paragraph (capped width) */}
            <p className="text-xs text-slate-300 leading-relaxed max-w-2xl font-sans">
              Executing these payments today captures a 2.5% discount on Tata Steel (annualized return 32.4%) and protects Q3 freight dispatch with Apex Logistics, while preserving ₹33.2L deployable cash—well above your ₹15.0L policy reserve floor.
            </p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col justify-center space-y-3 border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-6 min-w-[220px]">
            <button 
              onClick={() => onOpenDrawer('INV-2026-081')}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-md font-semibold text-xs transition shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Approve Plan (₹18.4L)</span>
            </button>

            <button 
              onClick={() => onNavigate('scenario-simulator')}
              className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium border border-slate-700 transition"
            >
              Stress-Test in Simulator
            </button>

            <button 
              onClick={() => onOpenDrawer('INV-2026-081')}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium underline text-center"
            >
              Open Full Audit Drawer
            </button>
          </div>

        </div>
      </div>

      {/* 3. NEW COMPONENT: ALTERNATIVES & IMPACT PANEL */}
      <AlternativesPanel
        candidates={mockOptionCandidates}
        selectedCandidateId="OPT-1"
        previewCandidateId={previewCandidateId}
        onSelectPreview={(id) => setPreviewCandidateId(id)}
      />

      {/* 4. UPGRADED 30-DAY LIQUIDITY PROJECTION CHART (With candidate comparison overlay) */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5 space-y-4">
        
        {/* Chart Header & Comparison Legend */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-slate-200 font-sans">
              30-Day Projected Liquidity Curve Across Alternatives
            </h3>
            <p className="text-xs text-slate-400">
              Comparing baseline cash path against pessimistic receivable delays & candidate previews
            </p>
          </div>

          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="flex items-center text-blue-400">
              <span className="w-2.5 h-2.5 bg-blue-500 rounded-full mr-1.5"></span>Selected Plan
            </span>
            <span className="flex items-center text-amber-400">
              <span className="w-2.5 h-2.5 bg-amber-500 rounded-full mr-1.5"></span>Pessimistic
            </span>
            {activeCandidate && (
              <span className="flex items-center text-purple-400 font-bold">
                <span className="w-2.5 h-2.5 bg-purple-500 rounded-full mr-1.5 animate-pulse"></span>
                Preview: {activeCandidate.action}
              </span>
            )}
            <span className="flex items-center text-red-400">
              <span className="w-2.5 h-0.5 bg-red-500 mr-1.5"></span>Reserve Floor ₹15L
            </span>
          </div>
        </div>

        {/* Active Candidate Preview Banner */}
        {activeCandidate && (
          <div className="bg-purple-950/40 border border-purple-800/60 p-2.5 rounded text-xs font-mono text-purple-300 flex justify-between items-center">
            <span>
              <strong>Previewing Candidate:</strong> {activeCandidate.title} — {activeCandidate.costBenefit}
              {activeCandidate.breachesFloor && (
                <span className="text-red-400 font-bold ml-2">⚠️ BREACHES RESERVE FLOOR ON {activeCandidate.breachDay}</span>
              )}
            </span>
            <button
              onClick={() => setPreviewCandidateId(null)}
              className="text-purple-400 hover:text-white underline text-[11px]"
            >
              Clear Preview
            </button>
          </div>
        )}

        {/* Chart */}
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${v}L`} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#090D16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px', color: '#F8FAFC' }}
                formatter={(value: any, name: any) => [
                  `₹${value}L`, 
                  name === 'cash' ? 'Selected Plan' : name === 'previewCash' ? `Preview (${activeCandidate?.action})` : 'Pessimistic Scenario'
                ]}
              />
              <ReferenceLine y={15.0} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Reserve Floor (₹15.0L)', fill: '#EF4444', fontSize: 10, position: 'insideBottomRight' }} />
              
              <Area type="monotone" dataKey="cash" stroke="#3B82F6" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCash)" />
              <Area type="monotone" dataKey="pessimistic" stroke="#F59E0B" strokeWidth={1.5} strokeDasharray="4 4" fill="transparent" />

              {activeCandidate && (
                <Area 
                  type="monotone" 
                  dataKey="previewCash" 
                  stroke={activeCandidate.breachesFloor ? "#EF4444" : "#A855F7"} 
                  strokeWidth={2.5} 
                  strokeDasharray="5 5" 
                  fill="transparent" 
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 6. CAPITAL ALLOCATION WATERFALL (Demoted location) */}
      <div className="bg-[#0F172A]/80 border border-slate-800/60 rounded-lg p-5">
        <div className="flex justify-between items-center mb-3 font-mono">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Capital Flow Breakdown</span>
          <span className="text-xs text-slate-500">Total Capital: ₹48.2L</span>
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

      {/* BOTTOM ROW: OBLIGATIONS + LIVE FEED */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
        
        {/* Upcoming Obligations */}
        <div className="bg-[#0F172A]/90 border border-slate-800 rounded-lg p-5 space-y-3">
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
                  <div className="font-semibold text-slate-200 font-sans">{inv.supplierName}</div>
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
        <div className="bg-[#0F172A]/90 border border-slate-800 rounded-lg p-5 space-y-3">
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
                  <div className="flex justify-between font-mono">
                    <span className="font-semibold text-slate-200 font-sans">{act.title}</span>
                    <span className="text-[10px] text-slate-500">{act.timestamp}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5 font-sans">{act.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
