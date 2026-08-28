import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { Sliders, RefreshCw, Sparkles, AlertTriangle, ShieldCheck, TrendingDown } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { runWhatIfSimulation } from '../services/api';

export const ScenarioSimulator: React.FC = () => {
  const [delayDays, setDelayDays] = useState<number>(5);
  const [cashDropLakhs, setCashDropLakhs] = useState<number>(6);
  const [simulationResult, setSimulationResult] = useState<any>(null);

  const baselineData = [
    { day: 'Aug 28', cash: 45.0 },
    { day: 'Aug 30', cash: 28.5 },
    { day: 'Sep 02', cash: 27.8 },
    { day: 'Sep 05', cash: 27.0 },
    { day: 'Sep 15', cash: 27.5 },
    { day: 'Sep 28', cash: 30.8 },
    { day: 'Oct 08', cash: 31.7 },
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
    if (idx >= 1) newCash -= (cashDropLakhs / 100.0) * 0.7;
    if (idx >= 3) newCash -= delayDays * 0.4;
    return {
      day: item.day,
      cash: Math.max(12.0, Number(newCash.toFixed(2)))
    };
  });

  const minSimulatedCash = simulationResult?.minCashLakhs ? (simulationResult.minCashLakhs / 100.0) : Math.min(...simulatedData.map((d: any) => d.cash));
  const breachesFloor = simulationResult?.breachesFloor ?? (minSimulatedCash < 15.50);

  return (
    <div className="space-y-6 pb-12 font-mono">
      <div>
        <h1 className="text-xl font-bold text-slate-100 font-sans">What-If Stress Test Scenario Simulator</h1>
        <p className="text-xs text-slate-400">Simulate Fleet Receivable Delays & Plant Outflow Spikes Against Tata Motors ₹15.50 Cr Reserve Policy</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* CONTROLS SIDEBAR */}
        <div className="lg:col-span-4 bg-[#0F172A]/80 border border-slate-800 rounded-xl p-5 space-y-6 backdrop-blur-xl shadow-xl">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Sliders className="w-4 h-4 text-blue-400" />
            <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-sans">Interactive Stress Controls</h2>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-sans">
              <span className="text-slate-300 font-bold">VRL Logistics Fleet Wire Delay</span>
              <span className="font-bold text-amber-400 font-mono">+{delayDays} Days</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="15" 
              value={delayDays}
              onChange={(e) => setDelayDays(Number(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0 days (On Time)</span>
              <span>15 days delay</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-sans">
              <span className="text-slate-300 font-bold">Unexpected Plant Opex Outflow</span>
              <span className="font-bold text-red-400 font-mono">₹{cashDropLakhs} Lakhs</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="15" 
              value={cashDropLakhs}
              onChange={(e) => setCashDropLakhs(Number(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>₹0L</span>
              <span>₹15L</span>
            </div>
          </div>

          <div className="space-y-1 text-xs font-sans">
            <label className="text-slate-400 text-[11px] font-bold">Target Supplier / Payables Pool</label>
            <select className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 outline-none font-mono text-xs">
              <option>INV00002 (Valeo India Pvt Ltd - ₹2.27 Cr)</option>
              <option>INV_TML_270 (Bosch Ltd Powertrain - ₹1.81L)</option>
              <option>INV00024 (JSW Steel Auto Grade - ₹9.20L)</option>
            </select>
          </div>

          <button
            onClick={() => {
              setDelayDays(0);
              setCashDropLakhs(0);
            }}
            className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-mono border border-slate-800 transition flex items-center justify-center space-x-2 shadow"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset to Baseline</span>
          </button>
        </div>

        {/* SIMULATION VISUALS */}
        <div className="lg:col-span-8 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#0F172A]/80 border border-slate-800 p-4 rounded-xl backdrop-blur-xl">
              <span className="text-[10px] font-mono font-bold uppercase text-slate-400">Baseline Lowest Cash</span>
              <div className="text-xl font-mono font-bold text-slate-100 mt-1">₹27.00 Cr</div>
              <div className="text-[11px] font-sans text-emerald-400 mt-0.5 font-bold">Above ₹15.50 Cr Reserve Floor</div>
            </div>

            <div className={`border p-4 rounded-xl backdrop-blur-xl transition-all duration-300 ${
              breachesFloor ? 'border-red-500/80 bg-red-950/20' : 'border-amber-500/80 bg-amber-950/20'
            }`}>
              <span className="text-[10px] font-mono font-bold uppercase text-slate-400">Simulated Lowest Cash</span>
              <div className={`text-xl font-mono font-bold mt-1 ${breachesFloor ? 'text-red-400 animate-pulse' : 'text-amber-400'}`}>
                ₹{minSimulatedCash.toFixed(2)} Cr
              </div>
              <div className={`text-[11px] font-sans mt-0.5 font-bold ${breachesFloor ? 'text-red-400' : 'text-amber-400'}`}>
                {breachesFloor ? '⚠️ BREACHES ₹15.50 Cr RESERVE FLOOR' : 'Caution Margin Tight'}
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A]/80 border border-slate-800 rounded-xl p-5 space-y-3 backdrop-blur-xl shadow-xl">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="font-bold text-slate-200 font-sans">Simulated Cash Path Comparison</span>
              <div className="flex items-center space-x-3 text-[11px]">
                <span className="text-slate-400 flex items-center"><span className="w-2 h-2 rounded-full bg-slate-500 mr-1"></span>Baseline</span>
                <span className="text-blue-400 flex items-center"><span className="w-2 h-2 rounded-full bg-blue-500 mr-1"></span>Simulated</span>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={simulatedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSim" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={breachesFloor ? "#EF4444" : "#3B82F6"} stopOpacity={0.4}/>
                      <stop offset="95%" stopColor={breachesFloor ? "#EF4444" : "#3B82F6"} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${v}Cr`} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#090D16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px', color: '#F8FAFC' }}
                  />
                  <ReferenceLine y={15.50} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Reserve Floor Policy (₹15.50 Cr)', fill: '#EF4444', fontSize: 10 }} />
                  <Area type="monotone" dataKey="cash" stroke={breachesFloor ? "#EF4444" : "#3B82F6"} strokeWidth={2.5} fillOpacity={1} fill="url(#colorSim)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-[#0F172A]/80 border-l-4 border-l-purple-500 border-y border-r border-slate-800 rounded-xl p-4 space-y-2 backdrop-blur-xl">
            <div className="flex items-center space-x-2 text-xs font-mono font-bold text-purple-400">
              <Sparkles className="w-4 h-4" />
              <span className="font-sans">AI Decision Adaptation Rationale</span>
            </div>
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {simulationResult?.explanation || (
                breachesFloor ? 
                `Action Shifted: Because simulated cash drops to ₹${minSimulatedCash.toFixed(2)} Cr (breaching ₹15.50 Cr reserve floor policy), CashPilot automatically shifts Valeo India invoice from Pay Now to Bank Credit Line.` :
                `Strategy Intact: Current stress parameters (+${delayDays}d delay, ₹${cashDropLakhs}L outflow) keep minimum cash at ₹${minSimulatedCash.toFixed(2)} Cr, safely above policy floor.`
              )}
            </p>
          </div>

        </div>

      </div>
    </div>
  );
};
