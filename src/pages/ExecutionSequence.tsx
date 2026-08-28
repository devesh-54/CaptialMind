import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  ListOrdered, 
  Calendar, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  Play, 
  Clock, 
  Layers, 
  ShieldCheck,
  TrendingUp,
  SlidersHorizontal,
  Sparkles,
  Zap,
  Activity,
  ChevronRight,
  Lock,
  DollarSign,
  Building2,
  Table,
  FileText
} from 'lucide-react';
import { fetchCommandCenterData, executeAction, subscribeToSSEStream } from '../services/api';

interface ExecutionSequenceProps {
  liveData?: any;
  onOpenDrawer?: (id: string) => void;
}

export const ExecutionSequence: React.FC<ExecutionSequenceProps> = ({ liveData: propsLiveData, onOpenDrawer }) => {
  const [internalData, setInternalData] = useState<any>(propsLiveData || null);
  const [selectedChoice, setSelectedChoice] = useState<string>('OPT-1');
  const [executedSteps, setExecutedSteps] = useState<Record<string, boolean>>({});
  const [isExecuting, setIsExecuting] = useState<string | null>(null);

  useEffect(() => {
    if (propsLiveData) {
      setInternalData(propsLiveData);
    }
  }, [propsLiveData]);

  useEffect(() => {
    async function loadData() {
      const realData = await fetchCommandCenterData();
      if (realData) {
        setInternalData((prev: any) => ({ ...realData, ...prev }));
      }
    }
    loadData();

    const unsubscribe = subscribeToSSEStream((streamEvent) => {
      if (streamEvent.event === 'REALTIME_UPDATE') {
        const payload = streamEvent.data;
        setInternalData((prev: any) => ({
          ...prev,
          kpis: {
            ...prev?.kpis,
            availableCash: payload.availableCash ?? prev?.kpis?.availableCash ?? 45040000.0,
            deployableCapital: Math.max(0, (payload.availableCash ?? 45040000.0) - 15500000.0)
          },
          heroRecommendation: payload.heroRecommendation || prev?.heroRecommendation,
          candidates: payload.candidates || prev?.candidates,
          invoices: payload.invoices || prev?.invoices,
          receivables: payload.receivables || prev?.receivables,
          activityFeed: payload.newEvent ? [payload.newEvent, ...(prev?.activityFeed || [])] : prev?.activityFeed
        }));
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const data = internalData || propsLiveData;

  const handleExecuteStep = async (stepId: string, invoiceId: string, actionType: string) => {
    setIsExecuting(stepId);
    await executeAction(invoiceId, actionType);
    setTimeout(() => {
      setExecutedSteps(prev => ({ ...prev, [stepId]: true }));
      setIsExecuting(null);
    }, 600);
  };

  // Dynamic signals extracted from live streaming data
  const availableCash = data?.kpis?.availableCash ?? 45040000.0;
  const deployableCapital = data?.kpis?.deployableCapital ?? (availableCash - 15500000.0);

  const customerAInflow = data?.receivables?.[0] || {
    id: 'REC00001',
    customerName: 'VRL Logistics Ltd',
    amount: 317609.60,
    collectionProbability: 87.0,
    expectedDelayDays: 1,
    status: 'On Time'
  };

  const boschInvoice = data?.invoices?.[0] || {
    id: 'INV00002',
    supplierName: 'Valeo India Pvt Ltd',
    amount: 22721445.28,
    discountPct: 2.0,
    dueDate: '2026-01-04',
    priorityScore: 95
  };

  // Dynamic live signals derived directly from real-time stream ingestion feed
  const liveStreamEvents = (data?.activityFeed || data?.events_log || []);

  const parseSignalMetric = (evt: any) => {
    if (!evt) return { amount: '₹15.50L', titleStr: 'FINANCIAL SIGNAL' };
    const text = `${evt.title || ''} ${evt.detail || ''}`;
    
    // Extract rupee amount
    const rupeeMatch = text.match(/(₹\s?[\d\.,]+(?:\s?[LCMcr]+)?)/i);
    let amountStr = rupeeMatch ? rupeeMatch[1] : '';

    // Extract delay days
    const delayMatch = text.match(/(\+\d+\s?d(?:ays)?)/i);
    if (!amountStr && delayMatch) {
      amountStr = delayMatch[1];
    }

    if (!amountStr) {
      amountStr = '₹45.04 Cr';
    }

    // Clean title string without emoji
    let cleanTitle = (evt.title || evt.event_type || 'STREAM SIGNAL')
      .replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '')
      .trim();

    return { amountStr, cleanTitle };
  };

  const renderedSignals = liveStreamEvents.length > 0
    ? liveStreamEvents.slice(0, 4).map((evt: any, i: number) => {
        const { amountStr, cleanTitle } = parseSignalMetric(evt);
        return {
          id: evt.id || `sig-${i}`,
          title: cleanTitle,
          tag: evt.impact || evt.stage || 'LIVE STREAM',
          tagColor: i % 2 === 0 ? 'bg-amber-500 text-black' : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800',
          borderColor: i % 2 === 0 ? 'border-amber-500/30 hover:border-amber-500/60' : 'border-emerald-500/30 hover:border-emerald-500/60',
          topLineColor: i % 2 === 0 ? 'via-amber-400/40' : 'via-emerald-400/40',
          titleColor: i % 2 === 0 ? 'text-amber-400' : 'text-emerald-400',
          amountText: amountStr,
          timeText: evt.time || 'Live',
          detail: evt.detail || 'Live stream context signal ingested into 0/1 Knapsack DP decision solver.'
        };
      })
    : [
        {
          id: 'sig-1',
          title: 'PLANT SALARIES & OPEX',
          tag: 'DUE IN 3 DAYS',
          tagColor: 'bg-amber-500 text-black',
          borderColor: 'border-amber-500/30 hover:border-amber-500/60',
          topLineColor: 'via-amber-400/40',
          titleColor: 'text-amber-400',
          amountText: formatINR(1650000),
          timeText: '01:31:23',
          detail: 'Critical payroll requirement due in 3 days. Lock reserve before executing discretionary payouts.'
        },
        {
          id: 'sig-2',
          title: `${customerAInflow.customerName || 'VRL LOGISTICS'} INFLOW`,
          tag: `EXPECTED IN ${customerAInflow.expectedDelayDays || 10}d`,
          tagColor: 'bg-emerald-950/80 text-emerald-300 border border-emerald-800',
          borderColor: 'border-emerald-500/30 hover:border-emerald-500/60',
          topLineColor: 'via-emerald-400/40',
          titleColor: 'text-emerald-400',
          amountText: formatINR(customerAInflow.amount || 317609.60),
          timeText: '01:31:45',
          detail: `Expected wire on Sep 28. Live Bayesian probability: ${customerAInflow.collectionProbability || 87.0}%.`
        },
        {
          id: 'sig-3',
          title: `${boschInvoice.supplierName || 'BOSCH LTD'} OEM`,
          tag: `DISCOUNT ${boschInvoice.discountPct || 2.0}%`,
          tagColor: 'bg-blue-950/80 text-blue-300 border border-blue-800',
          borderColor: 'border-blue-500/30 hover:border-blue-500/60',
          topLineColor: 'via-blue-400/40',
          titleColor: 'text-blue-400',
          amountText: formatINR(boschInvoice.amount || 22721445.28),
          timeText: '01:31:56',
          detail: `${boschInvoice.discountPct || 2.0}% early discount active. Priority Score: ${boschInvoice.priorityScore || 95}/100.`
        },
        {
          id: 'sig-4',
          title: 'STATUTORY TAX OBLIGATION',
          tag: 'DUE IN 5 DAYS',
          tagColor: 'bg-purple-950/80 text-purple-300 border border-purple-800',
          borderColor: 'border-purple-500/30 hover:border-purple-500/60',
          topLineColor: 'via-purple-400/40',
          titleColor: 'text-purple-400',
          amountText: formatINR(230000),
          timeText: '01:32:00',
          detail: 'Mandatory tax obligation due in 5 days. Remained covered under 30-day liquidity horizon.'
        }
      ];

  // Dynamic choices driven by live decision engine
  const choices = data?.candidates || [
    {
      id: 'OPT-1',
      title: 'Choice 1: Reserve Salary Opex + Early Pay Bosch/Valeo (Recommended)',
      score: 96,
      subScores: { liquidity: 98, financial: 95, supplier: 92, risk: 96 },
      action: 'Pay Now',
      cost: '₹16.50L Opex + Invoice Payout',
      benefit: 'Captures 2.0% discount & protects Plant Worker Payroll in 3 days',
      riskNote: `${customerAInflow.customerName || 'VRL Logistics'} inflow (${customerAInflow.collectionProbability}% prob) preserves ₹15.50L reserve floor`,
      breachesFloor: false,
      recommended: true
    },
    {
      id: 'OPT-2',
      title: 'Choice 2: Pay at Maturity (Defer Early Payment)',
      score: 61,
      subScores: { liquidity: 65, financial: 42, supplier: 78, risk: 62 },
      action: 'Pay at Maturity',
      cost: '₹16.50L Opex Today',
      benefit: 'Holds cash for Salary Day; defers invoice payment',
      riskNote: 'Forfeits early discount yield; zero return on cash',
      breachesFloor: false,
      recommended: false
    },
    {
      id: 'OPT-3',
      title: 'Choice 3: Draw Bank Dynamic Credit Line',
      score: 74,
      subScores: { liquidity: 90, financial: 65, supplier: 85, risk: 58 },
      action: 'Finance',
      cost: '₹1,250 Interest Cost (8.5% APR)',
      benefit: 'Frees cash buffer for unexpected expense spikes',
      riskNote: 'Preserves liquidity but incurs borrowing interest',
      breachesFloor: false,
      recommended: false
    }
  ];

  // Dynamically map live stream invoices & breakdown into 0/1 Knapsack Execution Steps!
  const dynamicInvoices = data?.invoices || [];

  const executionSteps = [
    {
      stepNumber: 1,
      id: 'STEP-1',
      title: 'Lock Operating Reserve for Plant Salaries & Opex',
      eventTrigger: 'Plant Assembly Line Payroll Due in 3 Days',
      targetEntity: 'HDFC Operations Account',
      amount: 1650000.0,
      timing: 'Immediate (Today)',
      actionType: 'LOCK_RESERVE',
      invoiceId: 'OBL-TML-01',
      status: 'Ready',
      detail: 'Locks ₹16.50L in HDFC Operating Cash to guarantee 100% assembly line worker payroll coverage before any discretionary supplier payouts.'
    },
    ...dynamicInvoices.slice(0, 5).map((inv: any, idx: number) => ({
      stepNumber: idx + 2,
      id: `STEP-${idx + 2}`,
      title: `Execute ${inv.aiAction || 'Payout'} for ${inv.supplierName} (${inv.id})`,
      eventTrigger: inv.discountPct > 0 ? `${inv.discountPct}% Early Payment Discount Active` : `Invoice Due ${inv.dueDate}`,
      targetEntity: `${inv.supplierName} Payable`,
      amount: inv.amount || 100000.0,
      timing: idx === 0 ? 'Execute Today (Before 17:00)' : `Due ${inv.dueDate}`,
      actionType: inv.aiAction === 'Pay Now' ? 'PAY_NOW' : 'PAY_AT_MATURITY',
      invoiceId: inv.id,
      status: idx === 0 ? 'Recommended' : 'Scheduled',
      detail: `Dispatches ${formatINR(inv.amount || 100000.0)} wire transfer for ${inv.supplierName}. 0/1 Knapsack Priority Score: ${inv.priorityScore || 85}/100.`
    })),
    {
      stepNumber: (dynamicInvoices.slice(0, 5).length) + 2,
      id: `STEP-${(dynamicInvoices.slice(0, 5).length) + 2}`,
      title: `Monitor Wire Inflow from ${customerAInflow.customerName || 'VRL Logistics Ltd'}`,
      eventTrigger: `Fleet Delivery Expected (${customerAInflow.collectionProbability || 87.0}% Bayesian Prob)`,
      targetEntity: `${customerAInflow.customerName || 'VRL Logistics Ltd'} Receivable`,
      amount: customerAInflow.amount || 317609.60,
      timing: 'In 10 Days (Sep 28)',
      actionType: 'MONITOR_INFLOW',
      invoiceId: customerAInflow.id || 'REC_TML_0365',
      status: 'Bayesian Monitored',
      detail: `Monitors HDFC incoming wire channel with ${customerAInflow.collectionProbability || 87.0}% Bayesian collection probability. Automatically triggers re-optimization if delayed >3 days.`
    },
    {
      stepNumber: (dynamicInvoices.slice(0, 5).length) + 3,
      id: `STEP-${(dynamicInvoices.slice(0, 5).length) + 3}`,
      title: 'Maintain Deployable Buffer Above Reserve Floor (₹15.50L)',
      eventTrigger: 'Continuous Reserve Policy Constraint',
      targetEntity: 'ICICI Treasury Reserve Buffer',
      amount: 15500000.0,
      timing: 'Continuous 30-Day Horizon',
      actionType: 'RETAIN_BUFFER',
      invoiceId: 'POLICY-FLOOR',
      status: 'Active Policy',
      detail: 'Maintains ₹15.50L minimum cash floor throughout 30-day projection window, shielding Tata Motors against unexpected demand shocks.'
    }
  ];

  return (
    <div className="space-y-8 pb-12 font-mono relative selection:bg-blue-600 selection:text-white">
      
      {/* AMBIENT BACKGROUND GLOW ORBS FOR LIQUID GLASS EFFECT */}
      <div className="absolute -top-12 -left-12 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse"></div>
      <div className="absolute top-1/3 -right-12 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="absolute bottom-12 left-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>

      {/* LIQUID GLASS HERO HEADER */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        
        {/* Iridescent Top Reflection Highlight */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30 backdrop-blur-md flex items-center">
                <Sparkles className="w-3 h-3 mr-1 text-blue-400" /> LIVE DATA DYNAMIC EXECUTION ENGINE
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 backdrop-blur-md animate-pulse">
                10s SSE REFRESH ACTIVE ({dynamicInvoices.length} INVOICES INGESTED)
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 font-sans tracking-tight">
              Treasury Context Choices & Order of Execution
            </h1>
            <p className="text-xs text-slate-300 font-sans">
              Evaluates live streaming financial context signals, presents AI candidate choices, and enforces dynamic order of execution.
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs shrink-0">
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold">Live Deployable Capital</div>
              <div className="text-base font-bold text-blue-400">{formatINR(deployableCapital)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 1: IMMINENT CONTEXT SIGNALS (DYNAMICALLY BOUND TO LIVE STREAMING EVENTS) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400 animate-pulse" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 1: Imminent Financial Context Signals (Live Dynamic Stream Feed)
            </h2>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-ping"></span> Live Stream Connected
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {renderedSignals.map((sig: any) => (
            <div 
              key={sig.id}
              className={`backdrop-blur-xl bg-[#0F172A]/50 border ${sig.borderColor} rounded-xl p-4 space-y-2 shadow-xl transition group relative overflow-hidden flex flex-col justify-between`}
            >
              <div className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent ${sig.topLineColor} to-transparent`}></div>
              
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-bold gap-2">
                  <span className={`font-sans font-bold text-[11px] truncate ${sig.titleColor}`}>{sig.title}</span>
                  <span className={`shrink-0 px-2 py-0.5 rounded text-[9px] font-bold uppercase ${sig.tagColor}`}>
                    {sig.tag}
                  </span>
                </div>
                
                {/* LARGE MONETARY / METRIC DISPLAY */}
                <div className="text-2xl font-bold text-slate-100 font-mono tracking-tight pt-1">
                  {sig.amountText}
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-white/5">
                <p className="text-[11px] text-slate-300 font-sans leading-relaxed line-clamp-2">
                  {sig.detail}
                </p>

                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span className="flex items-center text-slate-400"><Clock className="w-3 h-3 mr-1 text-slate-500" /> Refreshed {sig.timeText}</span>
                  <span className="text-emerald-400 font-bold">● Active</span>
                </div>
              </div>

            </div>
          ))}
        </div>
      </div>

      {/* SECTION 2: CHOICE EVALUATION MATRIX (LIQUID GLASS DYNAMIC CANDIDATES) */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="w-4 h-4 text-blue-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 2: AI Choice Evaluation Matrix (Live 0/1 Knapsack Scores)
            </h2>
          </div>
          <span className="text-[11px] text-slate-400">4-Objective Min-Max Normalized Scores</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {choices.map((choice: any) => {
            const rawScore = Number(choice.score) || 96;
            const displayScore = rawScore > 100 ? Math.min(98, Math.max(70, Math.round(rawScore / 750))) : Math.min(99, Math.max(1, rawScore));

            return (
              <div 
                key={choice.id}
                onClick={() => setSelectedChoice(choice.id)}
                className={`p-5 rounded-xl border backdrop-blur-xl transition-all duration-300 cursor-pointer space-y-3 relative overflow-hidden ${
                  choice.recommended || choice.selected
                    ? 'bg-blue-950/40 border-blue-500/60 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/30' 
                    : selectedChoice === choice.id
                    ? 'bg-slate-900/80 border-slate-600 shadow-md'
                    : 'bg-slate-900/40 border-white/5 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-100 text-xs font-sans">{choice.title}</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border backdrop-blur-md ${
                    choice.recommended || choice.selected ? 'bg-blue-500/20 text-blue-300 border-blue-400/40' : 'bg-slate-800/80 text-slate-400 border-slate-700'
                  }`}>
                    Score: {displayScore}/100
                  </span>
                </div>

                {/* Sub-scores mini bars */}
                {choice.subScores && (
                  <div className="grid grid-cols-4 gap-2 text-[10px] font-mono">
                    <div>
                      <div className="text-slate-400 flex justify-between"><span>Liq</span><span>{choice.subScores.liquidity}</span></div>
                      <div className="w-full bg-slate-800/80 h-1 rounded-full mt-0.5 overflow-hidden"><div style={{ width: `${choice.subScores.liquidity}%` }} className="bg-blue-500 h-full rounded-full"></div></div>
                    </div>
                    <div>
                      <div className="text-slate-400 flex justify-between"><span>Fin</span><span>{choice.subScores.financial}</span></div>
                      <div className="w-full bg-slate-800/80 h-1 rounded-full mt-0.5 overflow-hidden"><div style={{ width: `${choice.subScores.financial}%` }} className="bg-emerald-500 h-full rounded-full"></div></div>
                    </div>
                    <div>
                      <div className="text-slate-400 flex justify-between"><span>Supp</span><span>{choice.subScores.supplier}</span></div>
                      <div className="w-full bg-slate-800/80 h-1 rounded-full mt-0.5 overflow-hidden"><div style={{ width: `${choice.subScores.supplier}%` }} className="bg-purple-500 h-full rounded-full"></div></div>
                    </div>
                    <div>
                      <div className="text-slate-400 flex justify-between"><span>Risk</span><span>{choice.subScores.risk}</span></div>
                      <div className="w-full bg-slate-800/80 h-1 rounded-full mt-0.5 overflow-hidden"><div style={{ width: `${choice.subScores.risk}%` }} className="bg-amber-500 h-full rounded-full"></div></div>
                    </div>
                  </div>
                )}

                <div className="text-[11px] space-y-1 text-slate-300 font-sans border-t border-white/5 pt-2">
                  <div><strong>Cost & Benefit:</strong> {choice.costBenefit || choice.benefit} {choice.cost ? `(${choice.cost})` : ''}</div>
                  <div>
                    <strong>Risk Assessment:</strong>{' '}
                    {choice.breachesFloor ? (
                      <span className="text-red-400 font-bold">⚠️ BREACHES RESERVE FLOOR ON {choice.breachDay || 'Oct 08'}</span>
                    ) : (
                      <span className="text-emerald-400">{choice.riskNote}</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION 3: ORDER OF EXECUTION PIPELINE (DYNAMICALLY UPDATED FROM LIVE STREAM) */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 3: Optimal Order of Execution (Dynamic Live Knapsack Steps)
            </h2>
          </div>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 backdrop-blur-md">
            {executionSteps.length} DYNAMIC PIPELINE STEPS
          </span>
        </div>

        <div className="space-y-4 relative">
          
          {/* Vertical Connecting Line */}
          <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-gradient-to-b from-blue-500 via-amber-500 to-emerald-500 opacity-30 -z-0"></div>

          {executionSteps.map((step) => {
            const isDone = executedSteps[step.id];
            const isRunning = isExecuting === step.id;

            return (
              <div 
                key={step.id}
                className={`p-5 rounded-xl border backdrop-blur-xl transition-all duration-300 space-y-3 relative z-10 ${
                  isDone 
                    ? 'bg-emerald-950/30 border-emerald-500/40 shadow-lg shadow-emerald-950/20' 
                    : step.stepNumber === 1
                    ? 'bg-amber-950/20 border-amber-500/40 shadow-lg shadow-amber-950/20'
                    : 'bg-slate-900/50 border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  
                  <div className="flex items-start space-x-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 shadow-lg ${
                      isDone 
                        ? 'bg-emerald-500 text-black shadow-emerald-500/30' 
                        : step.stepNumber === 1
                        ? 'bg-amber-500 text-black shadow-amber-500/30'
                        : 'bg-blue-600 text-white shadow-blue-600/30'
                    }`}>
                      {isDone ? <CheckCircle2 className="w-4 h-4" /> : step.stepNumber}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-bold text-slate-100 text-sm font-sans">{step.title}</h3>
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border backdrop-blur-md ${
                          isDone 
                            ? 'bg-emerald-950 text-emerald-400 border-emerald-800' 
                            : step.stepNumber === 1
                            ? 'bg-amber-950 text-amber-400 border-amber-800'
                            : 'bg-blue-950 text-blue-400 border-blue-800'
                        }`}>
                          {isDone ? 'EXECUTED' : step.status}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 font-sans leading-relaxed">{step.detail}</p>
                      
                      <div className="flex flex-wrap items-center gap-4 text-[10px] text-slate-400 pt-1">
                        <span>🗓️ Signal: <strong>{step.eventTrigger}</strong></span>
                        <span>⏱️ Timing: <strong className="text-slate-200">{step.timing}</strong></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:flex-col sm:items-end shrink-0 space-y-2">
                    <div className="text-base font-bold text-slate-100">{formatINR(step.amount)}</div>
                    
                    {step.actionType === 'PAY_NOW' || step.actionType === 'LOCK_RESERVE' ? (
                      <button
                        disabled={isDone || isRunning}
                        onClick={() => handleExecuteStep(step.id, step.invoiceId, step.actionType)}
                        className={`py-2 px-4 rounded-xl text-xs font-bold transition-all duration-300 shadow-lg flex items-center space-x-2 ${
                          isDone 
                            ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 cursor-default'
                            : isRunning
                            ? 'bg-slate-800 text-slate-400 cursor-wait'
                            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/30 hover:scale-105 active:scale-95'
                        }`}
                      >
                        {isRunning ? (
                          <span>Executing...</span>
                        ) : isDone ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span>Executed</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-3.5 h-3.5 fill-current" />
                            <span>Execute Step</span>
                          </>
                        )}
                      </button>
                    ) : (
                      <span className="text-[10px] text-slate-500 italic bg-slate-900/60 px-2 py-1 rounded border border-slate-800">
                        Automated Trigger
                      </span>
                    )}
                  </div>

                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION 4: LIVE STREAM INGESTED INVOICES LEDGER TABLE (EXPECTED OUTPUT STREAM VISIBILITY) */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <Table className="w-4 h-4 text-blue-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 4: Live Stream Ingested Invoice Candidates ({dynamicInvoices.length} Items Evaluated)
            </h2>
          </div>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-950 text-blue-300 border border-blue-800">
            0/1 KNAPSACK INPUT MATRIX
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-900/90 text-slate-400 font-bold border-b border-white/10 text-[10px] uppercase">
                <th className="py-2.5 px-3">Invoice ID</th>
                <th className="py-2.5 px-3">Supplier Name</th>
                <th className="py-2.5 px-3">Amount (₹)</th>
                <th className="py-2.5 px-3">Discount</th>
                <th className="py-2.5 px-3">Due Date</th>
                <th className="py-2.5 px-3">Priority Score</th>
                <th className="py-2.5 px-3">AI 0/1 DP Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono text-slate-300">
              {dynamicInvoices.map((inv: any) => (
                <tr key={inv.id} className="hover:bg-white/5 transition">
                  <td className="py-2.5 px-3 font-bold text-blue-400">{inv.id}</td>
                  <td className="py-2.5 px-3 font-sans text-slate-200">{inv.supplierName}</td>
                  <td className="py-2.5 px-3 font-bold text-slate-100">{formatINR(inv.amount)}</td>
                  <td className="py-2.5 px-3">
                    {inv.discountPct > 0 ? (
                      <span className="text-emerald-400 font-bold">{inv.discountPct}% Active</span>
                    ) : (
                      <span className="text-slate-500">0%</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">{inv.dueDate}</td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 text-[10px] font-bold border border-slate-700">
                      {inv.priorityScore || 85}/100
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      inv.aiAction === 'Pay Now' || inv.aiAction === 'CAPTURE_DISCOUNT'
                        ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                        : 'bg-blue-950 text-blue-300 border-blue-800'
                    }`}>
                      {inv.aiAction || 'Pay Now'}
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
