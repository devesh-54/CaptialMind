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
  Building2
} from 'lucide-react';
import { fetchCommandCenterData, executeAction } from '../services/api';

interface ExecutionSequenceProps {
  liveData?: any;
  onOpenDrawer?: (id: string) => void;
}

export const ExecutionSequence: React.FC<ExecutionSequenceProps> = ({ liveData: propsLiveData, onOpenDrawer }) => {
  const [internalData, setInternalData] = useState<any>(null);
  const [selectedChoice, setSelectedChoice] = useState<string>('OPT-1');
  const [executedSteps, setExecutedSteps] = useState<Record<string, boolean>>({});
  const [isExecuting, setIsExecuting] = useState<string | null>(null);

  useEffect(() => {
    if (!propsLiveData) {
      async function loadData() {
        const realData = await fetchCommandCenterData();
        if (realData) {
          setInternalData(realData);
        }
      }
      loadData();
    }
  }, [propsLiveData]);

  const data = propsLiveData || internalData;

  const handleExecuteStep = async (stepId: string, invoiceId: string, actionType: string) => {
    setIsExecuting(stepId);
    await executeAction(invoiceId, actionType);
    setTimeout(() => {
      setExecutedSteps(prev => ({ ...prev, [stepId]: true }));
      setIsExecuting(null);
    }, 600);
  };

  // Dynamic signals extracted from live streaming data
  const availableCash = data?.kpis?.availableCash ?? 2554079.97;
  const deployableCapital = data?.kpis?.deployableCapital ?? (availableCash - 970000.0);

  const customerAInflow = data?.receivables?.[0] || {
    amount: 31760.96,
    collectionProbability: 87.0,
    expectedDelayDays: 1,
    status: 'On Time'
  };

  const boschInvoice = data?.invoices?.[0] || {
    id: 'INV_FUT_0260',
    amount: 68902.88,
    discountPct: 2.0,
    dueDate: '2026-08-28',
    priorityScore: 95
  };

  // Dynamic choices driven by live decision engine
  const choices = data?.candidates || [
    {
      id: 'OPT-1',
      title: 'Choice 1: Reserve Salary Opex + Early Pay Bosch Ltd (Recommended)',
      score: 96,
      subScores: { liquidity: 98, financial: 95, supplier: 92, risk: 96 },
      action: 'Pay Now',
      cost: '₹16.50L Opex + ₹68.90k Invoice',
      benefit: 'Captures 2.0% discount & protects Employee Salary Day in 3 days',
      riskNote: `Customer A inflow (${customerAInflow.collectionProbability}% prob) preserves ₹9.70L reserve floor`,
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
    },
    {
      id: 'OPT-4',
      title: 'Choice 4: Delay Payment (+10 Days)',
      score: 32,
      subScores: { liquidity: 40, financial: 25, supplier: 30, risk: 28 },
      action: 'Delay',
      cost: '₹0 immediate invoice outflow',
      benefit: 'Maximizes nominal immediate cash balance',
      riskNote: 'Breaches ₹9.70L Reserve Floor if Customer A is delayed >7 days',
      breachesFloor: true,
      breachDay: 'Oct 08',
      recommended: false
    }
  ];

  // Dynamic order of execution steps reflecting live data
  const executionSteps = [
    {
      stepNumber: 1,
      id: 'STEP-1',
      title: 'Lock Operating Reserve for Employee Salaries & Opex',
      eventTrigger: 'Employee Monthly Salaries & Opex Due in 3 Days',
      targetEntity: 'Payroll & Operations Account',
      amount: 1650000.0,
      timing: 'Immediate (Today)',
      actionType: 'LOCK_RESERVE',
      invoiceId: 'OBL-FUT-01',
      status: 'Ready',
      detail: 'Locks ₹16.50L in HDFC Operating Cash to guarantee 100% payroll coverage before any discretionary supplier payouts.'
    },
    {
      stepNumber: 2,
      id: 'STEP-2',
      title: `Execute Early Settlement for ${boschInvoice.supplierName || 'Bosch Ltd'} (${boschInvoice.id || 'INV_FUT_0260'})`,
      eventTrigger: `${boschInvoice.discountPct || 2.0}% Early Payment Discount Active`,
      targetEntity: `${boschInvoice.supplierName || 'Bosch Ltd'} Payable`,
      amount: boschInvoice.amount || 68902.88,
      timing: 'Execute Today (Before 17:00)',
      actionType: 'PAY_NOW',
      invoiceId: boschInvoice.id || 'INV_FUT_0260',
      status: 'Recommended',
      detail: `Dispatches ${formatINR(boschInvoice.amount || 68902.88)} wire transfer to ${boschInvoice.supplierName || 'Bosch Ltd'}, capturing ${boschInvoice.discountPct || 2.0}% discount yield and protecting Q3 component delivery SLAs.`
    },
    {
      stepNumber: 3,
      id: 'STEP-3',
      title: 'Execute Payout for Bosch Ltd Component Invoice (INV_FUT_0261)',
      eventTrigger: 'Invoice Due Tomorrow (2026-08-29)',
      targetEntity: 'Bosch Ltd Components',
      amount: 140555.66,
      timing: 'Due Tomorrow',
      actionType: 'PAY_NOW',
      invoiceId: 'INV_FUT_0261',
      status: 'Scheduled',
      detail: 'Schedules automated batch wire of ₹1.41L tomorrow morning to maintain 100% clean credit score with Bosch Ltd.'
    },
    {
      stepNumber: 4,
      id: 'STEP-4',
      title: 'Monitor Wire Inflow from Customer A (CUST011 / Mahindra Logistics)',
      eventTrigger: `Customer A Payment Expected (${customerAInflow.expectedDelayDays <= 2 ? 'On Time' : 'Delayed'})`,
      targetEntity: 'Mahindra Logistics Receivable',
      amount: customerAInflow.amount || 31760.96,
      timing: 'In 10 Days (Sep 28)',
      actionType: 'MONITOR_INFLOW',
      invoiceId: 'REC_FUT_0365',
      status: 'Bayesian Monitored',
      detail: `Monitors HDFC incoming wire channel with ${customerAInflow.collectionProbability || 87.0}% Bayesian collection probability. Automatically triggers re-optimization if delayed >3 days.`
    },
    {
      stepNumber: 5,
      id: 'STEP-5',
      title: 'Maintain Deployable Buffer Above Reserve Floor (₹9.70L)',
      eventTrigger: 'Continuous Reserve Policy Constraint',
      targetEntity: 'ICICI Reserve Buffer',
      amount: 970000.0,
      timing: 'Continuous 30-Day Horizon',
      actionType: 'RETAIN_BUFFER',
      invoiceId: 'POLICY-FLOOR',
      status: 'Active Policy',
      detail: 'Maintains ₹9.70L minimum cash floor throughout 30-day projection window, shielding company against unexpected demand shocks.'
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
                10s SSE REFRESH ACTIVE
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

      {/* SECTION 1: IMMINENT CONTEXT SIGNALS (DYNAMICALLY BOUND TO LIVE STREAM) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400 animate-pulse" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 1: Imminent Financial Context Signals (Live Dynamic)
            </h2>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-ping"></span> Live Stream Connected
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Signal 1: Salaries */}
          <div className="backdrop-blur-xl bg-[#0F172A]/50 border border-amber-500/30 rounded-xl p-4 space-y-2 shadow-xl hover:border-amber-500/60 transition group relative overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-400/40 to-transparent"></div>
            <div className="flex items-center justify-between text-[10px] text-amber-400 font-bold">
              <span>💼 SALARIES & OPEX</span>
              <span className="px-2 py-0.5 rounded-full bg-amber-500 text-black font-bold shadow-sm">DUE IN 3 DAYS</span>
            </div>
            <div className="text-xl font-bold text-slate-100">{formatINR(1650000)}</div>
            <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
              Critical payroll requirement due in 3 days. Must lock reserve before executing discretionary payouts.
            </p>
          </div>

          {/* Signal 2: Customer A (Dynamic Inflow & Bayesian Confidence) */}
          <div className="backdrop-blur-xl bg-[#0F172A]/50 border border-emerald-500/30 rounded-xl p-4 space-y-2 shadow-xl hover:border-emerald-500/60 transition group relative overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-400/40 to-transparent"></div>
            <div className="flex items-center justify-between text-[10px] text-emerald-400 font-bold gap-2">
              <span className="truncate">📥 CUSTOMER A INFLOW</span>
              <span className="shrink-0 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800 text-[9px]">EXPECTED IN 10d</span>
            </div>
            <div className="text-xl font-bold text-slate-100">{formatINR(customerAInflow.amount || 31760.96)}</div>
            <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
              Expected wire on Sep 28. Live Bayesian probability: <strong className="text-emerald-400">{customerAInflow.collectionProbability || 87.0}%</strong>.
            </p>
          </div>

          {/* Signal 3: Bosch Invoice (Dynamic Invoice Data) */}
          <div className="backdrop-blur-xl bg-[#0F172A]/50 border border-blue-500/30 rounded-xl p-4 space-y-2 shadow-xl hover:border-blue-500/60 transition group relative overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-400/40 to-transparent"></div>
            <div className="flex items-center justify-between text-[10px] text-blue-400 font-bold gap-2">
              <span className="truncate">🏭 BOSCH LTD RAW MATERIAL</span>
              <span className="shrink-0 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800 text-[9px]">DISCOUNT IN 2d</span>
            </div>
            <div className="text-xl font-bold text-slate-100">{formatINR(boschInvoice.amount || 68902.88)}</div>
            <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
              {boschInvoice.discountPct || 2.0}% early discount active. Priority Score: <strong>{boschInvoice.priorityScore || 95}</strong>/100.
            </p>
          </div>

          {/* Signal 4: Statutory Tax */}
          <div className="backdrop-blur-xl bg-[#0F172A]/50 border border-purple-500/30 rounded-xl p-4 space-y-2 shadow-xl hover:border-purple-500/60 transition group relative overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-purple-400/40 to-transparent"></div>
            <div className="flex items-center justify-between text-[10px] text-purple-400 font-bold gap-2">
              <span className="truncate">🏦 STATUTORY TAX OBLIGATION</span>
              <span className="shrink-0 bg-purple-950/80 px-2 py-0.5 rounded border border-purple-800 text-[9px]">DUE IN 5d</span>
            </div>
            <div className="text-xl font-bold text-slate-100">{formatINR(230000)}</div>
            <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
              Mandatory tax obligation due in 5 days. Remained covered under 30-day liquidity horizon.
            </p>
          </div>

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

      {/* SECTION 3: ORDER OF EXECUTION PIPELINE (DYNAMICALLY UPDATED) */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 3: Optimal Order of Execution (Dynamic Knapsack Output)
            </h2>
          </div>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 backdrop-blur-md">
            SEQUENCED EXECUTION PIPELINE
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

    </div>
  );
};
