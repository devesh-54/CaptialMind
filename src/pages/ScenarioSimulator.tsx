import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { Sliders, RefreshCw, Sparkles } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { runWhatIfSimulation } from '../services/api';

export const ScenarioSimulator: React.FC = () => {
  const [delayDays, setDelayDays] = useState<number>(5);
  const [cashDropLakhs, setCashDropLakhs] = useState<number>(6);
  const [simulationResult, setSimulationResult] = useState<any>(null);

  const baselineData = [
    { day: 'Aug 28', cash: 48.2 },
    { day: 'Aug 30', cash: 38.8 },
    { day: 'Sep 02', cash: 42.1 },
    { day: 'Sep 05', cash: 36.5 },
    { day: 'Sep 08', cash: 29.4 },
    { day: 'Sep 15', cash: 41.5 },
    { day: 'Sep 25', cash: 52.0 },
  ];

  useEffect(() => {
    async function runSim() {
      const res = await runWhatIfSimulation(delayDays, cashDropLakhs);
      if (res) {
        setSimulationResult(res);
      }
    }
    runSim();
  }, [delayDays, cashDropLakhs]);

  const simulatedData = simulationResult?.simulatedForecast || baselineData.map((item, idx) => {
    let newCash = item.cash;
    if (idx >= 1) newCash -= cashDropLakhs * 0.7;
    if (idx >= 3) newCash -= delayDays * 0.4;
    return {
      day: item.day,
      cash: Math.max(8.0, Number(newCash.toFixed(1)))
    };
  });

  const minSimulatedCash = simulationResult?.minCashLakhs ?? Math.min(...simulatedData.map((d: any) => d.cash));
  const breachesFloor = simulationResult?.breachesFloor ?? (minSimulatedCash < 15.0);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-100">What-If Scenario Simulator</h1>
        <p className="text-xs text-slate-400">Stress-Test Treasury Decisions Against Supply Chain & Receivable Delays</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div className="lg:col-span-4 bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Sliders className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-slate-200 font-mono uppercase">Stress Controls</h2>
          </div>

          <div className="space-y-2 font-mono">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Flipkart Receivable Delay</span>
              <span className="font-bold text-amber-400">+{delayDays} Days</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="15" 
              value={delayDays}
              onChange={(e) => setDelayDays(Number(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0 days</span>
              <span>15 days</span>
            </div>
          </div>

          <div className="space-y-2 font-mono">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Unexpected Outflow</span>
              <span className="font-bold text-red-400">₹{cashDropLakhs}L</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="15" 
              value={cashDropLakhs}
              onChange={(e) => setCashDropLakhs(Number(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>₹0L</span>
              <span>₹15L</span>
            </div>
          </div>

          <div className="space-y-1 font-mono text-xs">
            <label className="text-slate-400 text-[11px]">Select Target Invoice / Supplier</label>
            <select className="w-full bg-slate-900 border border-slate-800 rounded p-2 text-slate-200 outline-none">
              <option>INV-2026-081 (Tata Steel - ₹9.2L)</option>
              <option>INV-2026-084 (Apex Logistics - ₹5.8L)</option>
              <option>INV-2026-092 (Zenith Packaging - ₹12.5L)</option>
            </select>
          </div>

          <button
            onClick={() => {
              setDelayDays(0);
              setCashDropLakhs(0);
            }}
            className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-slate-400 rounded text-xs font-mono border border-slate-800 transition flex items-center justify-center space-x-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset to Baseline</span>
          </button>
        </div>

        <div className="lg:col-span-8 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#0F172A] border border-slate-800 p-4 rounded-lg">
              <span className="text-[10px] font-mono font-bold uppercase text-slate-500">Baseline Lowest Cash</span>
              <div className="text-xl font-mono font-bold text-slate-200 mt-1">₹29.4L</div>
              <div className="text-[11px] font-mono text-emerald-400 mt-0.5">Above ₹15.0L Floor</div>
            </div>

            <div className={`bg-[#0F172A] border p-4 rounded-lg transition-all duration-300 ${
              breachesFloor ? 'border-red-500/80 bg-red-950/20' : 'border-amber-500/80 bg-amber-950/20'
            }`}>
              <span className="text-[10px] font-mono font-bold uppercase text-slate-400">Simulated Lowest Cash</span>
              <div className={`text-xl font-mono font-bold mt-1 ${breachesFloor ? 'text-red-400 animate-pulse' : 'text-amber-400'}`}>
                ₹{minSimulatedCash.toFixed(1)}L
              </div>
              <div className={`text-[11px] font-mono mt-0.5 ${breachesFloor ? 'text-red-400 font-bold' : 'text-amber-400'}`}>
                {breachesFloor ? '⚠️ BREACHES ₹15.0L FLOOR' : 'Caution Margin Tight'}
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-3">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="font-bold text-slate-200 font-sans">Simulated Cash Path Comparison</span>
              <div className="flex items-center space-x-3">
                <span className="text-slate-400 flex items-center"><span className="w-2 h-2 rounded-full bg-slate-500 mr-1"></span>Baseline</span>
                <span className="text-blue-400 flex items-center"><span className="w-2 h-2 rounded-full bg-blue-500 mr-1"></span>Simulated</span>
              </div>
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={simulatedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSim" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={breachesFloor ? "#EF4444" : "#3B82F6"} stopOpacity={0.4}/>
                      <stop offset="95%" stopColor={breachesFloor ? "#EF4444" : "#3B82F6"} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${v}L`} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#090D16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px', color: '#F8FAFC' }}
                  />
                  <ReferenceLine y={15.0} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Reserve Floor (₹15.0L)', fill: '#EF4444', fontSize: 10 }} />
                  <Area type="monotone" dataKey="cash" stroke={breachesFloor ? "#EF4444" : "#3B82F6"} strokeWidth={2.5} fillOpacity={1} fill="url(#colorSim)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-[#0F172A] border-l-4 border-l-purple-500 border-y border-r border-slate-800 rounded-lg p-4 space-y-2">
            <div className="flex items-center space-x-2 text-xs font-mono font-bold text-purple-400">
              <Sparkles className="w-4 h-4" />
              <span>AI Decision Adaptation Rationale</span>
            </div>
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {simulationResult?.explanation || (
                breachesFloor ? 
                `Action Shifted: Because simulated cash drops to ₹${minSimulatedCash.toFixed(1)}L (breaching reserve floor), CashPilot automatically shifts Zenith Packaging from Pay Now to Bank Credit Line.` :
                `Strategy Intact: Current stress parameters (+${delayDays}d delay, ₹${cashDropLakhs}L outflow) keep minimum liquidity at ₹${minSimulatedCash.toFixed(1)}L, safely above floor.`
              )}
            </p>
          </div>

        </div>

      </div>
    </div>
  );
};
