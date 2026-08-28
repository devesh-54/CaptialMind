import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  CheckCircle2, 
  HelpCircle, 
  Sparkles,
  ArrowRight,
  Calendar,
  Layers,
  Info
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { mockActivityFeed, mockInvoices, mockOptionCandidates } from '../data/mockData';
import { PageId, OptionCandidate } from '../types/dashboard';
import { AlternativesPanel } from '../components/AlternativesPanel';
import { fetchCommandCenterData } from '../services/api';

interface CommandCenterProps {
  onOpenDrawer: (invoiceId: string) => void;
  onNavigate: (page: PageId) => void;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({ onOpenDrawer, onNavigate }) => {
  const [previewCandidateId, setPreviewCandidateId] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      const realData = await fetchCommandCenterData();
      if (realData) {
        setData(realData);
      }
    }
    loadData();
  }, []);

  const kpis = data?.kpis || {
    availableCash: 2554079.97,
    protectedCash: 970000.0,
    deployableCapital: 1584079.97,
    risk30d: 'LOW',
    wcEfficiency: 88,
    financingExposure: 1250000.0
  };

  const heroRec = data?.heroRecommendation || {
    title: 'Reserve ₹16.5L for Opex & Payroll + Pay ₹2.09L for Invoices INV_FUT_0260 & 0261 today',
    confidence: 96,
    breakdown: [
      { label: 'Operating Expense & Payroll (Due Today)', amount: 1650000.0 },
      { label: 'Bosch Ltd INV_FUT_0260 (Pay Now)', amount: 68902.88 },
      { label: 'Bosch Ltd INV_FUT_0261 (Pay Now)', amount: 140555.66 },
      { label: 'Retain Deployable Buffer', amount: 694621.43 }
    ],
    reasoning: 'Operating Expense & Payroll (₹16.50L) is due today and prioritized as CRITICAL from future_daily_consolidated.csv. Executing payments for open future invoices INV_FUT_0260 (₹68.9k) & INV_FUT_0261 (₹1.41L) today preserves Tier-1 supplier delivery SLAs before Customer CUST011 inflows ₹31.76k on Sep 28 (87% Bayesian probability).'
  };

  const candidates: OptionCandidate[] = data?.candidates || mockOptionCandidates;
  const forecast = data?.forecast || [
    { day: 'Aug 28', cash: 25.5, pessimistic: 24.0 },
    { day: 'Aug 29 (Opex)', cash: 9.0, pessimistic: 8.5 },
    { day: 'Sep 01', cash: 8.3, pessimistic: 7.8 },
    { day: 'Sep 05', cash: 8.0, pessimistic: 7.5 },
    { day: 'Sep 15 (REC_0365)', cash: 8.3, pessimistic: 7.8 },
    { day: 'Sep 28', cash: 25.8, pessimistic: 24.5 },
    { day: 'Oct 08', cash: 26.7, pessimistic: 25.0 },
    { day: 'Oct 18', cash: 28.0, pessimistic: 26.5 },
  ];
  
  const obligationsList = data?.obligations || [
    {
      id: 'OBL-FUT-01',
      supplierName: 'Operating Expense & Monthly Salaries',
      amount: 1650000.0,
      dueDate: '2026-08-28 (Today)',
      priority: 'CRITICAL',
      aiAction: 'Must Pay'
    },
    {
      id: 'OBL-FUT-02',
      supplierName: 'Invoice INV_FUT_0260 (Bosch Ltd)',
      amount: 68902.88,
      dueDate: 'Due 2026-08-28',
      priority: 'HIGH',
      aiAction: 'Pay Now'
    },
    {
      id: 'OBL-FUT-03',
      supplierName: 'Invoice INV_FUT_0261 (Bosch Ltd)',
      amount: 140555.66,
      dueDate: 'Due 2026-08-29',
      priority: 'HIGH',
      aiAction: 'Pay Now'
    },
    {
      id: 'OBL-FUT-04',
      supplierName: 'Invoice INV_FUT_0262 (JSW Steel)',
      amount: 21563.53,
      dueDate: 'Due 2026-08-31',
      priority: 'MEDIUM',
      aiAction: 'Pay at Maturity'
    }
  ];

  const activityList = data?.activityFeed || mockActivityFeed;
  const activeCandidate = candidates.find(c => c.id === previewCandidateId);

  const chartData = forecast.map((point: any, idx: number) => {
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
      
      {/* 1. DECLUTTERED KPI STRIP */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-5">
        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Available Cash</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">{formatINR(kpis.availableCash)}</div>
          <div className="text-[11px] text-emerald-400 font-mono mt-1">
            Opening: ₹42.04L
          </div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Protected Cash</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">{formatINR(kpis.protectedCash)}</div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">Policy Reserve Floor</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Deployable Capital</span>
          <div className="text-xl font-mono font-bold text-blue-400 mt-1">{formatINR(kpis.deployableCapital)}</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Opex & 3 Obligations</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">30-Day Risk</span>
          <div className="mt-1 flex items-center">
            <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              {kpis.risk30d}
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">Safety margin 101%</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">WC Efficiency</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">{kpis.wcEfficiency}/100</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Optimized Schedule</div>
        </div>

        <div className="bg-[#0F172A]/80 border border-slate-800/60 p-4 rounded-lg">
          <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider font-mono">Financing Exposure</span>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">{formatINR(kpis.financingExposure)}</div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Available Credit Line</div>
        </div>
      </div>

      {/* PROMINENT REAL-TIME BUSINESS CONTEXT & OBLIGATIONS BANNER */}
      <div className="bg-[#0F172A] border border-amber-500/40 rounded-lg p-4 space-y-3 shadow-lg">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-amber-400">
              Real-Time Treasury Context & Future Streaming Obligations
            </h3>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950 text-amber-300 border border-amber-800/60">
            PARSED FROM FUTURE STREAMING DATASET
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono text-xs">
          
          {/* Card 1: Operating Expense */}
          <div className="bg-amber-950/30 border border-amber-800/60 p-3 rounded-lg space-y-1">
            <div className="flex items-center justify-between text-[10px] text-amber-400 font-bold uppercase">
              <span>Operating Expense & Payroll</span>
              <span className="px-1.5 py-0.2 rounded bg-amber-500 text-black font-bold">DUE TODAY</span>
            </div>
            <div className="text-base font-bold text-slate-100">₹16.50L</div>
            <div className="text-[10px] text-slate-400">Critical Daily Opex Outflow</div>
          </div>

          {/* Card 2: Customer CUST011 Inflow */}
          <div className="bg-emerald-950/30 border border-emerald-800/60 p-3 rounded-lg space-y-1">
            <div className="flex items-center justify-between text-[10px] text-emerald-400 font-bold uppercase">
              <span>Customer CUST011 Inflow</span>
              <span>EXPECTED SEP 28</span>
            </div>
            <div className="text-base font-bold text-slate-100">₹31.76k</div>
            <div className="text-[10px] text-slate-400">87.0% Collection Confidence</div>
          </div>

          {/* Card 3: Invoice INV_FUT_0260 */}
          <div className="bg-blue-950/30 border border-blue-800/60 p-3 rounded-lg space-y-1">
            <div className="flex items-center justify-between text-[10px] text-blue-400 font-bold uppercase">
              <span>Invoice INV_FUT_0260</span>
              <span>DUE TODAY</span>
            </div>
            <div className="text-base font-bold text-slate-100">₹68.90k</div>
            <div className="text-[10px] text-emerald-400 font-bold">Bosch Ltd Tier-1 Payable</div>
          </div>

          {/* Card 4: Invoice INV_FUT_0261 */}
          <div className="bg-purple-950/30 border border-purple-800/60 p-3 rounded-lg space-y-1">
            <div className="flex items-center justify-between text-[10px] text-purple-400 font-bold uppercase">
              <span>Invoice INV_FUT_0261</span>
              <span>DUE AUG 29</span>
            </div>
            <div className="text-base font-bold text-slate-100">₹1.41L</div>
            <div className="text-[10px] text-slate-400">Bosch Ltd Component Invoice</div>
          </div>

        </div>
      </div>

      {/* 2. REFINED HERO CARD */}
      <div className="bg-[#0F172A] border-l-4 border-l-blue-500 border-y border-r border-slate-800 rounded-lg overflow-hidden shadow-xl">
        
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
            <span>{heroRec.confidence}% Confidence</span>
            <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
          </div>
        </div>

        <div className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          
          <div className="space-y-4 flex-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider flex items-center font-mono">
                <Sparkles className="w-3.5 h-3.5 mr-1.5" /> AI Priority Recommendation
              </span>
            </div>

            <h2 className="text-xl lg:text-2xl font-bold text-slate-100 tracking-tight leading-snug">
              {heroRec.title}
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800 font-mono text-xs">
              {heroRec.breakdown.map((item: any, i: number) => (
                <div key={i} className="flex justify-between items-center px-2.5 py-1.5 bg-slate-800/50 rounded">
                  <span className="text-slate-400 truncate mr-2">{item.label}</span>
                  <span className={`font-bold shrink-0 ${i === 0 ? 'text-amber-400' : i === 1 ? 'text-emerald-400' : 'text-blue-400'}`}>
                    {formatINR(item.amount)}
                  </span>
                </div>
              ))}
            </div>

            <p className="text-xs text-slate-300 leading-relaxed max-w-2xl font-sans">
              {heroRec.reasoning}
            </p>
          </div>

          <div className="flex flex-col justify-center space-y-3 border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-6 min-w-[220px]">
            <button 
              onClick={() => onOpenDrawer('INV_FUT_0260')}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-md font-semibold text-xs transition shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Approve Plan</span>
            </button>

            <button 
              onClick={() => onNavigate('scenario-simulator')}
              className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium border border-slate-700 transition"
            >
              Stress-Test in Simulator
            </button>

            <button 
              onClick={() => onOpenDrawer('INV_FUT_0260')}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium underline text-center"
            >
              Open Full Audit Drawer
            </button>
          </div>

        </div>
      </div>

      {/* 3. ALTERNATIVES & IMPACT PANEL */}
      <AlternativesPanel
        candidates={candidates}
        selectedCandidateId="OPT-1"
        previewCandidateId={previewCandidateId}
        onSelectPreview={(id) => setPreviewCandidateId(id)}
      />

      {/* 4. 30-DAY LIQUIDITY PROJECTION CHART */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5 space-y-4">
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-200 font-sans">
                30-Day Projected Liquidity Curve Across Alternatives
              </h3>

              <span className="px-2.5 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/80 text-[10px] font-mono font-bold flex items-center">
                <Info className="w-3 h-3 mr-1" /> All candidate decisions evaluated against this full 30-day forward horizon
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
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
              <span className="w-2.5 h-0.5 bg-red-500 mr-1.5"></span>Reserve Floor ₹9.70L
            </span>
          </div>
        </div>

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
              <ReferenceLine y={9.7} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Reserve Floor (₹9.70L)', fill: '#EF4444', fontSize: 10, position: 'insideBottomRight' }} />
              
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

      {/* 6. CAPITAL ALLOCATION WATERFALL */}
      <div className="bg-[#0F172A]/80 border border-slate-800/60 rounded-lg p-5">
        <div className="flex justify-between items-center mb-3 font-mono">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Capital Flow Breakdown</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950 text-purple-300 border border-purple-800/80 flex items-center">
              <Layers className="w-3 h-3 mr-1 text-purple-400" /> Globally optimal allocation (0/1 knapsack, 10 invoices evaluated)
            </span>
          </div>
          <span className="text-xs text-slate-500">Total Capital: {formatINR(kpis.availableCash)}</span>
        </div>
        <div className="w-full h-8 bg-slate-900 rounded-lg flex overflow-hidden p-1 gap-1 border border-slate-800">
          <div style={{ width: '37.9%' }} className="bg-slate-700 rounded text-[10px] font-mono text-slate-200 flex items-center justify-center font-bold">
            Reserve Floor ₹9.70L
          </div>
          <div style={{ width: '42.1%' }} className="bg-amber-600/80 rounded text-[10px] font-mono text-amber-100 flex items-center justify-center font-bold">
            Opex ₹16.50L
          </div>
          <div style={{ width: '12.0%' }} className="bg-emerald-600/80 rounded text-[10px] font-mono text-emerald-100 flex items-center justify-center font-bold">
            Invoices ₹2.09L
          </div>
          <div style={{ width: '8.0%' }} className="bg-blue-600/40 rounded text-[10px] font-mono text-blue-200 flex items-center justify-center font-bold">
            Buffer
          </div>
        </div>
      </div>

      {/* BOTTOM ROW: UPCOMING OBLIGATIONS + LIVE FEED */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
        <div className="bg-[#0F172A]/90 border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-sm font-bold text-slate-200">Upcoming Future Streaming Obligations</h3>
              <p className="text-[11px] text-slate-400">Parsed from future_daily_consolidated.csv</p>
            </div>
            <button onClick={() => onNavigate('invoices')} className="text-xs text-blue-400 hover:underline flex items-center font-mono">
              View all <ArrowRight className="w-3 h-3 ml-1" />
            </button>
          </div>
          <div className="divide-y divide-slate-800">
            {obligationsList.map((ob: any) => (
              <div key={ob.id} className="py-2.5 flex items-center justify-between text-xs font-mono">
                <div>
                  <div className="font-semibold text-slate-200 font-sans flex items-center space-x-1.5">
                    <span>{ob.supplierName}</span>
                    {ob.priority === 'CRITICAL' && (
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-950 text-amber-400 border border-amber-800">
                        CRITICAL
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-500">{ob.dueDate}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-100">{formatINR(ob.amount)}</div>
                  <span className={`px-1.5 py-0.5 text-[10px] rounded border ${
                    ob.aiAction === 'Must Pay' ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-emerald-950 text-emerald-400 border-emerald-800'
                  }`}>
                    {ob.aiAction}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#0F172A]/90 border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-200">Agent Activity Stream</h3>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse"></span> Live Stream
            </span>
          </div>
          <div className="space-y-3">
            {activityList.map((act: any) => (
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
