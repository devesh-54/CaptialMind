import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  Table, 
  Radio, 
  RefreshCw, 
  PlusCircle, 
  Search, 
  Filter, 
  Zap, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  ArrowDownLeft, 
  FileText, 
  Building2, 
  ShieldAlert,
  Play
} from 'lucide-react';
import { subscribeToSSEStream, triggerSimulatedEvent, fetchCommandCenterData } from '../services/api';

export const LiveStreamTable: React.FC = () => {
  const [streamRows, setStreamRows] = useState<any[]>([]);
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [channelStatus, setChannelStatus] = useState<string>('Active SSE Channel');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [eventCount, setEventCount] = useState<number>(0);

  useEffect(() => {
    // Populate initial dataset rows from backend
    async function loadInitial() {
      const data = await fetchCommandCenterData();
      if (data && data.invoices) {
        const initialRows = [
          {
            id: 'REC_FUT_0365',
            timestamp: new Date().toLocaleTimeString(),
            sourceDataset: 'future_daily_consolidated.csv',
            entity: 'Customer CUST011 (Mahindra Logistics)',
            type: 'RECEIVABLE_INFLOW',
            amount: 31760.96,
            status: 'EXPECTED SEP 28',
            confidence: '87.0%',
            actionImpact: 'Expected Inflow',
            isNew: false
          },
          {
            id: 'INV_FUT_0260',
            timestamp: new Date().toLocaleTimeString(),
            sourceDataset: 'invoices.csv',
            entity: 'Bosch Ltd',
            type: 'INVOICE_PAYABLE',
            amount: 68902.88,
            status: 'PAY NOW (DUE TODAY)',
            confidence: '95.0%',
            actionImpact: 'Captures 2.0% Discount',
            isNew: false
          },
          {
            id: 'INV_FUT_0261',
            timestamp: new Date().toLocaleTimeString(),
            sourceDataset: 'invoices.csv',
            entity: 'Bosch Ltd Components',
            type: 'INVOICE_PAYABLE',
            amount: 140555.66,
            status: 'PAY NOW (DUE TOMORROW)',
            confidence: '89.0%',
            actionImpact: 'Protects Delivery SLA',
            isNew: false
          },
          {
            id: 'OBL_FUT_001',
            timestamp: new Date().toLocaleTimeString(),
            sourceDataset: 'future_daily_consolidated.csv',
            entity: 'Operating Expense & Monthly Salaries',
            type: 'OPEX_PAYROLL',
            amount: 1650000.00,
            status: 'CRITICAL (DUE TODAY)',
            confidence: '100%',
            actionImpact: 'Locked in Reserve',
            isNew: false
          }
        ];
        setStreamRows(initialRows);
        setEventCount(initialRows.length);
      }
    }
    loadInitial();

    // Listen to real-time SSE event stream & append new incoming records continuously
    const unsubscribe = subscribeToSSEStream((streamEvent) => {
      const timeStr = new Date().toLocaleTimeString();

      if (streamEvent.event === 'CONNECTED') {
        setChannelStatus('LIVE STREAM CONNECTED');
      } else if (streamEvent.event === 'HEARTBEAT') {
        setChannelStatus(`LIVE PULSE (${streamEvent.data.timestamp})`);
      } else if (streamEvent.event === 'REALTIME_UPDATE' || streamEvent.event === 'TELEMETRY_PING') {
        setChannelStatus(`STREAMING LIVE (${timeStr})`);

        const dataPayload = streamEvent.data;
        const newRecord = {
          id: `REC_LIVE_${Math.floor(1000 + Math.random() * 9000)}`,
          timestamp: timeStr,
          sourceDataset: 'future_daily_consolidated.csv (LIVE STREAM)',
          entity: dataPayload.newEvent?.title || `Live Telemetry Date ${dataPayload.sequenceDate || '2026-08-28'}`,
          type: streamEvent.event === 'REALTIME_UPDATE' ? 'MATERIAL_REOPTIMIZATION' : 'TELEMETRY_PING',
          amount: dataPayload.availableCash ? dataPayload.availableCash / 10.0 : 1650000.0,
          status: streamEvent.event === 'REALTIME_UPDATE' ? 'RE-OPTIMIZED' : 'MONITORED',
          confidence: streamEvent.event === 'REALTIME_UPDATE' ? '96.0%' : '100%',
          actionImpact: dataPayload.newEvent?.impact || 'Stream Ingested',
          isNew: true
        };

        setStreamRows((prev) => [newRecord, ...prev.slice(0, 99)]);
        setEventCount((c) => c + 1);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const handleSimulateNewData = async (type: str, desc: str, delay = 0, outflow = 0) => {
    setIsSimulating(true);
    await triggerSimulatedEvent(type, desc, delay, outflow);
    setTimeout(() => setIsSimulating(false), 800);
  };

  const filteredRows = streamRows.filter((row) => {
    const matchesFilter = 
      filterCategory === 'ALL' ? true :
      filterCategory === 'INVOICES' ? row.type.includes('INVOICE') :
      filterCategory === 'RECEIVABLES' ? row.type.includes('RECEIVABLE') :
      filterCategory === 'PAYROLL' ? row.type.includes('OPEX') :
      filterCategory === 'MATERIAL' ? row.status.includes('RE-OPTIMIZED') : true;

    const matchesSearch = 
      row.entity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.type.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  return (
    <div className="space-y-8 pb-12 font-mono relative selection:bg-blue-600 selection:text-white">
      
      {/* AMBIENT BACKGROUND GLOW ORBS */}
      <div className="absolute -top-12 -left-12 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse"></div>
      <div className="absolute top-1/3 -right-12 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>

      {/* LIQUID GLASS HERO HEADER */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 backdrop-blur-md flex items-center">
                <Radio className="w-3 h-3 mr-1 text-emerald-400 animate-pulse" /> LIVE STREAMING TABLE DASHBOARD
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-950/80 text-blue-300 border border-blue-500/40 backdrop-blur-md">
                CONTINUOUS INGESTION
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 font-sans tracking-tight">
              Real-Time Data Ingestion Table Dashboard
            </h1>
            <p className="text-xs text-slate-300 font-sans">
              Displays live telemetry & financial dataset records arriving over SSE stream. New records accumulate continuously.
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs shrink-0">
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold">Total Ingested Events</div>
              <div className="text-base font-bold text-emerald-400 flex items-center justify-end space-x-1">
                <span>{eventCount} Records</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CONTROLS & LIVE SIMULATION ACTION STRIP */}
      <div className="backdrop-blur-xl bg-[#0F172A]/50 border border-white/10 rounded-2xl p-5 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Trigger New Live Data Stream Event
            </h2>
          </div>
          <span className="text-[10px] text-slate-400">Appends new records directly into the table</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            disabled={isSimulating}
            onClick={() => handleSimulateNewData('RECEIVABLE_DELAYED', 'Customer A Wire Delayed (+10d)', 10, 0)}
            className="py-2.5 px-3 bg-slate-900/80 hover:bg-slate-800 border border-amber-500/30 hover:border-amber-500/60 text-amber-300 rounded-xl text-xs text-left transition backdrop-blur-md flex items-center justify-between group"
          >
            <div>
              <div className="font-bold text-[11px]">📥 Customer Delay (+10d)</div>
              <div className="text-[10px] text-slate-400">Appends Material Event</div>
            </div>
            <Play className="w-3.5 h-3.5 shrink-0 text-amber-400 group-hover:scale-110 transition" />
          </button>

          <button
            disabled={isSimulating}
            onClick={() => handleSimulateNewData('NEW_INVOICE', 'Bosch Ltd Tier-1 Invoice INV_FUT_0270 Created (₹81.4k)', 0, 0)}
            className="py-2.5 px-3 bg-slate-900/80 hover:bg-slate-800 border border-blue-500/30 hover:border-blue-500/60 text-blue-300 rounded-xl text-xs text-left transition backdrop-blur-md flex items-center justify-between group"
          >
            <div>
              <div className="font-bold text-[11px]">🏭 New Invoice (Bosch Ltd)</div>
              <div className="text-[10px] text-slate-400">Appends Invoice Record</div>
            </div>
            <Play className="w-3.5 h-3.5 shrink-0 text-blue-400 group-hover:scale-110 transition" />
          </button>

          <button
            disabled={isSimulating}
            onClick={() => handleSimulateNewData('DECIDE', 'Unexpected Machine Expense Outflow ₹6.0L', 0, 6)}
            className="py-2.5 px-3 bg-slate-900/80 hover:bg-slate-800 border border-red-500/30 hover:border-red-500/60 text-red-300 rounded-xl text-xs text-left transition backdrop-blur-md flex items-center justify-between group"
          >
            <div>
              <div className="font-bold text-[11px]">⚡ Emergency Outflow (₹6.0L)</div>
              <div className="text-[10px] text-slate-400">Appends Opex Event</div>
            </div>
            <Play className="w-3.5 h-3.5 shrink-0 text-red-400 group-hover:scale-110 transition" />
          </button>

          <button
            disabled={isSimulating}
            onClick={() => handleSimulateNewData('OBSERVE', 'HDFC Bank Telemetry Balance Sync Ping', 0, 0.5)}
            className="py-2.5 px-3 bg-slate-900/80 hover:bg-slate-800 border border-emerald-500/30 hover:border-emerald-500/60 text-emerald-300 rounded-xl text-xs text-left transition backdrop-blur-md flex items-center justify-between group"
          >
            <div>
              <div className="font-bold text-[11px]">📡 Telemetry Bank Ping</div>
              <div className="text-[10px] text-slate-400">Appends Monitored Ping</div>
            </div>
            <Play className="w-3.5 h-3.5 shrink-0 text-emerald-400 group-hover:scale-110 transition" />
          </button>
        </div>
      </div>

      {/* FILTER & SEARCH BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        
        {/* Category Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {['ALL', 'INVOICES', 'RECEIVABLES', 'PAYROLL', 'MATERIAL'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-3 py-1.5 rounded-xl font-bold transition backdrop-blur-md border ${
                filterCategory === cat
                  ? 'bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-600/30'
                  : 'bg-slate-900/60 text-slate-400 border-white/5 hover:text-slate-200 hover:border-white/20'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative min-w-[240px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search live records..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition backdrop-blur-md"
          />
        </div>
      </div>

      {/* LIQUID GLASS LIVE DATA TABLE */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
        <div className="bg-slate-900/80 px-6 py-3 border-b border-white/10 flex justify-between items-center text-xs font-mono">
          <div className="flex items-center space-x-2">
            <Table className="w-4 h-4 text-blue-400" />
            <span className="font-bold text-slate-200 uppercase">Live Stream Data Ingestion Table ({filteredRows.length} Rows Shown)</span>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse"></span> {channelStatus}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="bg-slate-950/80 border-b border-white/10 text-[11px] uppercase font-bold text-slate-400">
                <th className="py-3.5 px-6">Timestamp & ID</th>
                <th className="py-3.5 px-4">Entity / Customer / Supplier</th>
                <th className="py-3.5 px-4">Transaction Type</th>
                <th className="py-3.5 px-4 text-right">Amount</th>
                <th className="py-3.5 px-4">Probability / Confidence</th>
                <th className="py-3.5 px-4">Status & Impact</th>
                <th className="py-3.5 px-4">Source Dataset</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredRows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 text-xs font-sans">
                    <Clock className="w-6 h-6 mx-auto mb-2 opacity-50 text-blue-400" />
                    No streaming records matched your filter. Incoming live stream events will accumulate here automatically.
                  </td>
                </tr>
              ) : (
                filteredRows.map((row) => (
                  <tr 
                    key={row.id}
                    className={`transition-all duration-500 hover:bg-slate-800/40 ${
                      row.isNew ? 'bg-blue-500/10 animate-pulse border-l-4 border-l-blue-500' : ''
                    }`}
                  >
                    <td className="py-4 px-6">
                      <div className="font-bold text-blue-400">{row.id}</div>
                      <div className="text-[10px] text-slate-400">{row.timestamp}</div>
                    </td>

                    <td className="py-4 px-4 font-semibold text-slate-100 font-sans">
                      {row.entity}
                    </td>

                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border backdrop-blur-md ${
                        row.type.includes('MATERIAL') ? 'bg-amber-950/80 text-amber-300 border-amber-500/40' :
                        row.type.includes('INVOICE') ? 'bg-blue-950/80 text-blue-300 border-blue-500/40' :
                        row.type.includes('RECEIVABLE') ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40' :
                        'bg-slate-800/80 text-slate-300 border-slate-700'
                      }`}>
                        {row.type}
                      </span>
                    </td>

                    <td className="py-4 px-4 text-right font-bold text-slate-100">
                      {formatINR(row.amount)}
                    </td>

                    <td className="py-4 px-4 font-bold text-emerald-400">
                      {row.confidence}
                    </td>

                    <td className="py-4 px-4">
                      <div className="font-bold text-slate-200">{row.status}</div>
                      <div className="text-[10px] text-slate-400 font-sans">{row.actionImpact}</div>
                    </td>

                    <td className="py-4 px-4 text-[10px] text-slate-400">
                      {row.sourceDataset}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
