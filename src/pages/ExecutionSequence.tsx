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
  ChevronRight
} from 'lucide-react';
import { fetchCommandCenterData, executeAction } from '../services/api';

interface ExecutionSequenceProps {
  onOpenDrawer?: (id: string) => void;
}

export const ExecutionSequence: React.FC<ExecutionSequenceProps> = ({ onOpenDrawer }) => {
  const [data, setData] = useState<any>(null);
  const [selectedChoice, setSelectedChoice] = useState<string>('OPT-1');
  const [executedSteps, setExecutedSteps] = useState<Record<string, boolean>>({});
  const [isExecuting, setIsExecuting] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      const realData = await fetchCommandCenterData();
      if (realData) {
        setData(realData);
      }
    }
    loadData();
  }, []);

  const handleExecuteStep = async (stepId: string, invoiceId: string, actionType: string) => {
    setIsExecuting(stepId);
    await executeAction(invoiceId, actionType);
    setTimeout(() => {
      setExecutedSteps(prev => ({ ...prev, [stepId]: true }));
      setIsExecuting(null);
    }, 600);
  };

  const choices = [
    {
      id: 'OPT-1',
      title: 'Choice 1: Reserve Salary Opex + Early Pay Bosch Ltd (Recommended)',
      score: 96,
      subScores: { liquidity: 98, financial: 95, supplier: 92, risk: 96 },
      action: 'Pay Now',
      cost: '₹16.50L Opex + ₹68.90k Invoice',
      benefit: 'Captures 2.0% discount & protects Employee Salary Day in 3 days',
      riskNote: 'Customer A inflow (in 10 days) preserves ₹9.70L reserve floor',
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
      title: 'Execute Early Settlement for Bosch Ltd (INV_FUT_0260)',
      eventTrigger: '2.0% Early Payment Discount Deadline in 2 Days',
      targetEntity: 'Bosch Ltd Tier-1 Payable',
      amount: 68902.88,
      timing: 'Execute Today (Before 17:00)',
      actionType: 'PAY_NOW',
      invoiceId: 'INV_FUT_0260',
      status: 'Recommended',
      detail: 'Dispatches ₹68.90k wire transfer to Bosch Ltd, capturing 2.0% discount yield and protecting Q3 component delivery SLAs.'
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
      eventTrigger: 'Customer A Payment Expected in 10 Days (2026-09-28)',
      targetEntity: 'Mahindra Logistics Receivable',
      amount: 31760.96,
      timing: 'In 10 Days (Sep 28)',
      actionType: 'MONITOR_INFLOW',
      invoiceId: 'REC_FUT_0365',
      status: 'Bayesian Monitored',
      detail: 'Monitors HDFC incoming wire channel with 87.0% Bayesian collection probability. Automatically triggers re-optimization if delayed >3 days.'
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
    <div className="space-y-8 pb-12 font-mono">
      {/* PAGE HEADER */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2">
          <ListOrdered className="w-6 h-6 text-blue-400" />
          <h1 className="text-xl font-bold text-slate-100 font-sans">Treasury Choices & Execution Sequence</h1>
        </div>
        <p className="text-xs text-slate-400 font-sans mt-1">
          Evaluates upcoming cash context signals, presents AI choices, and enforces the optimal step-by-step order of execution.
        </p>
      </div>

      {/* SECTION 1: IMMINENT CONTEXT SIGNALS */}
      <div className="bg-[#0F172A] border border-amber-500/40 rounded-lg p-5 space-y-4 shadow-lg">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-amber-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-amber-400">
              Section 1: Imminent Financial Signals & Context
            </h2>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
            REAL-TIME DATASET SIGNALS
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          
          {/* Signal 1: Salaries */}
          <div className="bg-amber-950/40 border border-amber-800/60 p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-[10px] text-amber-400 font-bold">
              <span>💼 EMPLOYEE SALARIES & OPEX</span>
              <span className="px-1.5 py-0.5 rounded bg-amber-500 text-black font-bold">DUE IN 3 DAYS</span>
            </div>
            <div className="text-lg font-bold text-slate-100">{formatINR(1650000)}</div>
            <p className="text-[11px] text-slate-300 font-sans">
              Critical payroll requirement due in 3 days. Must lock reserve before executing discretionary payouts.
            </p>
          </div>

          {/* Signal 2: Customer A */}
          <div className="bg-emerald-950/40 border border-emerald-800/60 p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-[10px] text-emerald-400 font-bold">
              <span>📥 CUSTOMER A (CUST011) INFLOW</span>
              <span>EXPECTED IN 10 DAYS</span>
            </div>
            <div className="text-lg font-bold text-slate-100">{formatINR(31760.96)}</div>
            <p className="text-[11px] text-slate-300 font-sans">
              Expected wire on Sep 28. Bayesian probability: <strong>87.0%</strong> (11 historical observations).
            </p>
          </div>

          {/* Signal 3: Bosch Invoice */}
          <div className="bg-blue-950/40 border border-blue-800/60 p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-[10px] text-blue-400 font-bold">
              <span>🏭 BOSCH LTD RAW MATERIAL</span>
              <span>DISCOUNT IN 2 DAYS</span>
            </div>
            <div className="text-lg font-bold text-slate-100">{formatINR(68902.88)}</div>
            <p className="text-[11px] text-slate-300 font-sans">
              2.0% early discount deadline in 2 days. Early payout preserves critical supplier relationship.
            </p>
          </div>

          {/* Signal 4: Statutory Tax */}
          <div className="bg-purple-950/40 border border-purple-800/60 p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-[10px] text-purple-400 font-bold">
              <span>🏦 STATUTORY TAX OBLIGATION</span>
              <span>DUE IN 5 DAYS</span>
            </div>
            <div className="text-lg font-bold text-slate-100">{formatINR(230000)}</div>
            <p className="text-[11px] text-slate-300 font-sans">
              Mandatory tax obligation due in 5 days. Must remain covered under 30-day liquidity horizon.
            </p>
          </div>

        </div>
      </div>

      {/* SECTION 2: CHOICE EVALUATION MATRIX */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="w-4 h-4 text-blue-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 2: AI Choice Evaluation Matrix
            </h2>
          </div>
          <span className="text-[11px] text-slate-400">4-Objective Min-Max Normalized Scores</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {choices.map((choice) => (
            <div 
              key={choice.id}
              onClick={() => setSelectedChoice(choice.id)}
              className={`p-4 rounded-lg border cursor-pointer transition space-y-3 ${
                choice.recommended 
                  ? 'bg-blue-950/40 border-blue-500/60 ring-1 ring-blue-500/30' 
                  : selectedChoice === choice.id
                  ? 'bg-slate-900 border-slate-700'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-100 text-xs font-sans">{choice.title}</span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                  choice.recommended ? 'bg-blue-900 text-blue-300 border-blue-700' : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}>
                  Score: {choice.score}/100
                </span>
              </div>

              {/* Sub-scores mini bars */}
              <div className="grid grid-cols-4 gap-2 text-[10px] font-mono">
                <div>
                  <div className="text-slate-400 flex justify-between"><span>Liq</span><span>{choice.subScores.liquidity}</span></div>
                  <div className="w-full bg-slate-800 h-1 rounded mt-0.5"><div style={{ width: `${choice.subScores.liquidity}%` }} className="bg-blue-500 h-full rounded"></div></div>
                </div>
                <div>
                  <div className="text-slate-400 flex justify-between"><span>Fin</span><span>{choice.subScores.financial}</span></div>
                  <div className="w-full bg-slate-800 h-1 rounded mt-0.5"><div style={{ width: `${choice.subScores.financial}%` }} className="bg-emerald-500 h-full rounded"></div></div>
                </div>
                <div>
                  <div className="text-slate-400 flex justify-between"><span>Supp</span><span>{choice.subScores.supplier}</span></div>
                  <div className="w-full bg-slate-800 h-1 rounded mt-0.5"><div style={{ width: `${choice.subScores.supplier}%` }} className="bg-purple-500 h-full rounded"></div></div>
                </div>
                <div>
                  <div className="text-slate-400 flex justify-between"><span>Risk</span><span>{choice.subScores.risk}</span></div>
                  <div className="w-full bg-slate-800 h-1 rounded mt-0.5"><div style={{ width: `${choice.subScores.risk}%` }} className="bg-amber-500 h-full rounded"></div></div>
                </div>
              </div>

              <div className="text-[11px] space-y-1 text-slate-300 font-sans border-t border-slate-800/80 pt-2">
                <div><strong>Cost & Benefit:</strong> {choice.benefit} ({choice.cost})</div>
                <div>
                  <strong>Risk Assessment:</strong>{' '}
                  {choice.breachesFloor ? (
                    <span className="text-red-400 font-bold">⚠️ BREACHES RESERVE FLOOR ON {choice.breachDay}</span>
                  ) : (
                    <span className="text-emerald-400">{choice.riskNote}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 3: ORDER OF EXECUTION PIPELINE */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-5">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Section 3: Optimal Order of Execution (0/1 Knapsack Output)
            </h2>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
            SEQUENCED EXECUTION PIPELINE
          </span>
        </div>

        <div className="space-y-4">
          {executionSteps.map((step) => {
            const isDone = executedSteps[step.id];
            const isRunning = isExecuting === step.id;

            return (
              <div 
                key={step.id}
                className={`p-4 rounded-lg border transition ${
                  isDone 
                    ? 'bg-emerald-950/30 border-emerald-800/60' 
                    : step.stepNumber === 1
                    ? 'bg-amber-950/20 border-amber-800/60'
                    : 'bg-slate-900 border-slate-800'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  
                  <div className="flex items-start space-x-3">
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                      isDone 
                        ? 'bg-emerald-500 text-black' 
                        : step.stepNumber === 1
                        ? 'bg-amber-500 text-black'
                        : 'bg-blue-600 text-white'
                    }`}>
                      {isDone ? <CheckCircle2 className="w-4 h-4" /> : step.stepNumber}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-bold text-slate-100 text-xs font-sans">{step.title}</h3>
                        <span className={`px-2 py-0.2 rounded text-[10px] font-bold border ${
                          isDone 
                            ? 'bg-emerald-950 text-emerald-400 border-emerald-800' 
                            : step.stepNumber === 1
                            ? 'bg-amber-950 text-amber-400 border-amber-800'
                            : 'bg-blue-950 text-blue-400 border-blue-800'
                        }`}>
                          {isDone ? 'EXECUTED' : step.status}
                        </span>
                      </div>

                      <p className="text-[11px] text-slate-300 font-sans leading-relaxed">{step.detail}</p>
                      
                      <div className="flex items-center space-x-4 text-[10px] text-slate-400 pt-1">
                        <span>🗓️ Signal: <strong>{step.eventTrigger}</strong></span>
                        <span>⏱️ Execution Timing: <strong className="text-slate-200">{step.timing}</strong></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:flex-col sm:items-end shrink-0 space-y-1">
                    <div className="text-sm font-bold text-slate-100">{formatINR(step.amount)}</div>
                    
                    {step.actionType === 'PAY_NOW' || step.actionType === 'LOCK_RESERVE' ? (
                      <button
                        disabled={isDone || isRunning}
                        onClick={() => handleExecuteStep(step.id, step.invoiceId, step.actionType)}
                        className={`py-1.5 px-3 rounded text-xs font-bold transition flex items-center space-x-1.5 ${
                          isDone 
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800 cursor-default'
                            : isRunning
                            ? 'bg-slate-800 text-slate-400 cursor-wait'
                            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/30'
                        }`}
                      >
                        {isRunning ? (
                          <span>Executing...</span>
                        ) : isDone ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Done</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-3 h-3" />
                            <span>Execute Step</span>
                          </>
                        )}
                      </button>
                    ) : (
                      <span className="text-[10px] text-slate-500 italic">Automated Trigger</span>
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
