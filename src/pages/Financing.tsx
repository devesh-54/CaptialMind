import React from 'react';
import { formatINR } from '../utils/formatters';
import { CheckCircle2, ShieldCheck, Landmark, Clock, ArrowRight } from 'lucide-react';

export const Financing: React.FC = () => {
  const options = [
    {
      id: 'FIN-01',
      title: 'Internal Cash Deployment',
      recommended: true,
      impact: '₹18.4L Immediate Outflow',
      cost: '₹0 (Zero Financing Interest)',
      verdict: 'RECOMMENDED: Captures ₹33,440 discount while preserving ₹15L safety reserve floor.',
      apr: '0.0%',
      availability: 'Instant (HDFC Treasury)'
    },
    {
      id: 'FIN-02',
      title: 'Dynamic Bank Credit Line',
      recommended: false,
      impact: '₹0 Outflow Today (₹12.5L Line Drawn)',
      cost: '₹4,100 Interest Cost (8.5% APR)',
      verdict: 'ALTERNATIVE: Preserves cash if Flipkart receivable is delayed >5 days.',
      apr: '8.5% p.a.',
      availability: 'Pre-Approved (ICICI Bank)'
    },
    {
      id: 'FIN-03',
      title: 'Supplier Reverse Factoring',
      recommended: false,
      impact: '₹9.2L Paid by Factoring Partner',
      cost: '₹7,800 Processing & Yield Fee',
      verdict: 'SUB-OPTIMAL: Higher fee reduces net discount yield from 2.5% to 1.6%.',
      apr: '11.2% p.a.',
      availability: 'Active (KredX Platform)'
    }
  ];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Financing Option Evaluator</h1>
        <p className="text-xs text-slate-400">Comparing Internal Liquidity vs External Credit Lines for Working Capital Optimization</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {options.map((opt) => (
          <div 
            key={opt.id}
            className={`rounded-lg p-6 space-y-4 relative flex flex-col justify-between transition ${
              opt.recommended 
                ? 'bg-[#0F172A] border-2 border-blue-500 shadow-xl shadow-blue-500/10' 
                : 'bg-[#0F172A] border border-slate-800 opacity-90'
            }`}
          >
            {opt.recommended && (
              <span className="absolute -top-3 left-4 px-2.5 py-0.5 rounded bg-blue-600 text-white font-mono text-[10px] font-bold uppercase tracking-wider flex items-center shadow">
                <CheckCircle2 className="w-3 h-3 mr-1" /> AI Recommended Choice
              </span>
            )}

            <div className="space-y-3 pt-2">
              <h3 className="font-bold text-slate-100 text-base">{opt.title}</h3>

              <div className="space-y-2 font-mono text-xs">
                <div className="p-2.5 bg-slate-900/80 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Immediate Cash Impact</div>
                  <div className="font-bold text-slate-200 mt-0.5">{opt.impact}</div>
                </div>

                <div className="p-2.5 bg-slate-900/80 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Financing Cost</div>
                  <div className={`font-bold mt-0.5 ${opt.recommended ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {opt.cost}
                  </div>
                </div>

                <div className="flex justify-between text-[11px] text-slate-400 pt-1">
                  <span>APR Rate: <strong className="text-slate-200">{opt.apr}</strong></span>
                  <span>Access: <strong className="text-slate-200">{opt.availability}</strong></span>
                </div>
              </div>

              <p className="text-xs text-slate-300 bg-slate-900/40 p-3 rounded border border-slate-800/60 leading-relaxed font-sans">
                {opt.verdict}
              </p>
            </div>

            <button 
              className={`w-full py-2 px-3 rounded text-xs font-mono font-semibold transition flex items-center justify-center space-x-1 ${
                opt.recommended 
                  ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20' 
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
              }`}
            >
              <span>{opt.recommended ? 'Selected Strategy' : 'Evaluate Alternative'}</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </button>

          </div>
        ))}
      </div>
    </div>
  );
};
