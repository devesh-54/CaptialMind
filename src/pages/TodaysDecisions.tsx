import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  Play, 
  CheckCircle2, 
  Lock, 
  Sparkles, 
  Clock, 
  ArrowUpRight, 
  ShieldCheck,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { fetchCommandCenterData, triggerSimulatedEvent } from '../services/api';

export const TodaysDecisions: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [executedItems, setExecutedItems] = useState<Record<string, boolean>>({});
  const [executingId, setExecutingId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const real = await fetchCommandCenterData();
      if (real) {
        setData(real);
      }
    }
    load();
  }, []);

  // Filter only items scheduled for TODAY
  const rawInvoices = data?.invoices || [
    {
      id: 'INV00002',
      supplierName: 'Valeo India Pvt Ltd',
      supplierCategory: 'Lighting Systems & Sensor Assemblies',
      amount: 22721445.28,
      discountPct: 2.0,
      dueDate: '2026-01-04',
      dueToday: true,
      aiAction: 'PAY_NOW',
      priorityScore: 95,
      reason: 'Capture 2.0% early discount yield (+₹4,54,428 saved today). Highest priority OEM allocation.'
    },
    {
      id: 'INV_TML_270',
      supplierName: 'Bosch Ltd (Powertrain Electronics)',
      supplierCategory: 'Fuel Injection & Engine ECU Systems',
      amount: 181400.00,
      discountPct: 1.5,
      dueDate: '2026-09-05',
      dueToday: true,
      aiAction: 'PAY_NOW',
      priorityScore: 91,
      reason: 'Execute early wire before 17:00 cutoff to maintain Critical Tier-1 supplier SLA.'
    }
  ];

  const todayObligation = {
    id: 'OBL-TML-01',
    supplierName: 'Plant Operating Expense & Assembly Payroll',
    supplierCategory: 'Tata Motors Assembly Worker Payroll Due in 3 Days',
    amount: 1650000.00,
    discountPct: 0,
    dueDate: '2026-08-31',
    dueToday: true,
    aiAction: 'LOCK_RESERVE',
    priorityScore: 99,
    reason: 'Lock ₹16.50L operating cash in HDFC Treasury to guarantee 100% assembly worker payroll coverage.'
  };

  const todayItems = [
    ...rawInvoices.filter((inv: any) => inv.aiAction === 'Pay Now' || inv.aiAction === 'PAY_NOW' || inv.dueToday).slice(0, 2),
    todayObligation
  ];

  const handleExecute = async (item: any) => {
    setExecutingId(item.id);
    await triggerSimulatedEvent('PAYMENT_SCHEDULED', `Today payout executed for ${item.supplierName}`, 0, item.amount);
    setTimeout(() => {
      setExecutedItems(prev => ({ ...prev, [item.id]: true }));
      setExecutingId(null);
    }, 700);
  };

  const totalPayoutToday = todayItems.reduce((acc, item) => acc + item.amount, 0);

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-16 font-mono text-slate-100 selection:bg-blue-600 selection:text-white">
      
      {/* MINIMAL HEADER */}
      <div className="bg-[#0F172A]/80 border border-white/10 rounded-2xl p-6 shadow-2xl backdrop-blur-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-sans text-blue-400 font-bold mb-1">
            <Calendar className="w-3.5 h-3.5" />
            <span>AUG 29, 2026 — TODAY'S DECISION QUEUE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 font-sans tracking-tight">
            Today's Payout Decisions
          </h1>
          <p className="text-xs text-slate-400 font-sans">
            Minimal executive queue of actions scheduled for immediate execution today.
          </p>
        </div>

        <div className="bg-slate-950/80 border border-slate-800 px-4 py-2.5 rounded-xl shrink-0 text-right">
          <div className="text-[10px] uppercase text-slate-500 font-bold">Total Cash Allocated Today</div>
          <div className="text-xl font-bold text-emerald-400 mt-0.5">{formatINR(totalPayoutToday)}</div>
        </div>
      </div>

      {/* VERTICALLY STACKED MINIMAL DECISION CARDS */}
      <div className="space-y-4">
        {todayItems.map((item: any, index: number) => {
          const isExecuted = executedItems[item.id];
          const isExecuting = executingId === item.id;
          const isLock = item.aiAction === 'LOCK_RESERVE';

          return (
            <div 
              key={item.id}
              className={`bg-[#0F172A]/70 border rounded-2xl p-6 transition-all duration-300 shadow-xl backdrop-blur-xl relative overflow-hidden space-y-4 ${
                isExecuted 
                  ? 'border-emerald-500/50 bg-emerald-950/10' 
                  : isLock
                  ? 'border-amber-500/40 bg-amber-950/10'
                  : 'border-blue-500/40 hover:border-blue-500/70'
              }`}
            >
              <div className={`absolute inset-x-0 top-0 h-1 ${
                isExecuted ? 'bg-emerald-500' : isLock ? 'bg-amber-500' : 'bg-blue-500'
              }`}></div>

              {/* CARD TOP ROW */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-3">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-500 font-mono">#0{index + 1}</span>
                    <span className="text-base font-bold text-slate-100 font-sans">{item.supplierName}</span>
                  </div>
                  <p className="text-xs text-slate-400 font-sans">{item.supplierCategory}</p>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    isExecuted
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : isLock
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-blue-950 text-blue-300 border border-blue-800'
                  }`}>
                    {isExecuted ? 'EXECUTED TODAY' : isLock ? 'LOCK RESERVE' : 'PAY TODAY'}
                  </span>
                  {item.discountPct > 0 && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {item.discountPct}% DISCOUNT
                    </span>
                  )}
                </div>
              </div>

              {/* AMOUNT & REASONING ROW */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                
                <div className="md:col-span-4 bg-slate-950/80 p-4 rounded-xl border border-white/5 font-mono">
                  <div className="text-[10px] text-slate-500 uppercase font-bold">Amount to Process</div>
                  <div className="text-2xl font-bold text-slate-100 mt-1">{formatINR(item.amount)}</div>
                </div>

                <div className="md:col-span-8 space-y-1 font-sans text-xs">
                  <div className="text-slate-400 font-bold flex items-center">
                    <Sparkles className="w-3.5 h-3.5 text-blue-400 mr-1" /> AI Decision Rationale
                  </div>
                  <p className="text-slate-200 leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-white/5">
                    {item.reason || item.action_reason || 'Allocated by 0/1 Knapsack DP solver for optimal capital efficiency.'}
                  </p>
                </div>

              </div>

              {/* BOTTOM ACTION BAR */}
              <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs font-sans">
                <div className="text-slate-400 font-mono text-[11px] flex items-center">
                  <Clock className="w-3.5 h-3.5 text-slate-500 mr-1" /> Target Execution: <strong>Today (Before 17:00)</strong>
                </div>

                <button
                  disabled={isExecuted || isExecuting}
                  onClick={() => handleExecute(item)}
                  className={`py-2.5 px-6 rounded-xl font-bold transition-all duration-300 shadow-xl flex items-center space-x-2 ${
                    isExecuted
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40 cursor-default'
                      : isExecuting
                      ? 'bg-slate-800 text-slate-400 cursor-wait'
                      : isLock
                      ? 'bg-amber-600 hover:bg-amber-500 text-black shadow-amber-600/20 hover:scale-105 active:scale-95'
                      : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/30 hover:scale-105 active:scale-95'
                  }`}
                >
                  {isExecuting ? (
                    <span>Processing Wire...</span>
                  ) : isExecuted ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>{isLock ? 'Reserve Locked' : 'Wire Dispatched'}</span>
                    </>
                  ) : isLock ? (
                    <>
                      <Lock className="w-4 h-4" />
                      <span>Lock Reserve Now</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-current" />
                      <span>Execute Wire Transfer</span>
                    </>
                  )}
                </button>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
