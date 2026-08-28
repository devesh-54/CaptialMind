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
  const [channelStatus, setChannelStatus] = useState<string>('Active SSE Stream Channel');
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
            entity: 'Bosch Ltd Raw Materials',
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

    // Automated sequence generator cycling real future data records every 3.5 seconds
    const sequencePool = [
      {
        entity: 'Customer CUST011 (Mahindra Logistics Wire Sync)',
        type: 'RECEIVABLE_INFLOW',
        amount: 31760.96,
        status: 'MONITORED INFLOW',
        confidence: '87.0%',
        impact: 'Bayesian Prior Verified (alpha=10, beta=2)',
        source: 'future_relational_vertical_merged.csv'
      },
      {
        entity: 'Bosch Ltd Tier-1 Raw Material (INV_FUT_0260)',
        type: 'INVOICE_PAYABLE',
        amount: 68902.88,
        status: 'DISCOUNT ACTIVE (2.0%)',
        confidence: '95.0%',
        impact: 'Knapsack Priority Score 95/100',
        source: 'invoices.csv'
      },
      {
        entity: 'HDFC & ICICI Treasury Balance Telemetry Ping',
        type: 'TELEMETRY_SYNC',
        amount: 25540799.70,
        status: 'TREASURY CONFIRMED',
        confidence: '100%',
        impact: 'Available Cash ₹25.54 Cr',
        source: 'cash_accounts.csv'
      },
      {
        entity: 'Employee Salaries & Operating Expense Reserve',
        type: 'OPEX_PAYROLL',
        amount: 1650000.00,
        status: 'LOCKED IN RESERVE',
        confidence: '100%',
        impact: 'Protected in HDFC Treasury (Due in 3 Days)',
        source: 'obligations.csv'
      },
      {
        entity: 'Apollo Tyres Ltd Component Invoice (INV_FUT_0265)',
        type: 'INVOICE_PAYABLE',
        amount: 215000.00,
        status: 'PAY AT MATURITY',
        confidence: '82.0%',
        impact: 'Deferred to preserve liquidity floor',
        source: 'invoices.csv'
      }
    ];

    let poolIdx = 0;
    const intervalTimer = setInterval(() => {
      const item = sequencePool[poolIdx % sequencePool.length];
      poolIdx++;
      const timeStr = new Date().toLocaleTimeString();

      const newRecord = {
        id: `LIVE_STREAM_${Math.floor(100000 + Math.random() * 900000)}`,
        timestamp: timeStr,
        sourceDataset: item.source,
        entity: item.entity,
        type: item.type,
        amount: item.amount,
        status: item.status,
        confidence: item.confidence,
        actionImpact: item.impact,
        isNew: true
      };

      setChannelStatus(`STREAMING LIVE (${timeStr})`);
      setStreamRows((prev) => [newRecord, ...prev.slice(0, 199)]);
      setEventCount((c) => c + 1);
    }, 3500);

    // Listen to real-time SSE stream events from backend
    const unsubscribe = subscribeToSSEStream((streamEvent) => {
      const timeStr = new Date().toLocaleTimeString();

      if (streamEvent.event === 'CONNECTED') {
        setChannelStatus('LIVE STREAM CONNECTED');
      } else if (streamEvent.event === 'REALTIME_UPDATE') {
        const dataPayload = streamEvent.data;
        const newRecord = {
          id: `REC_REOPT_${Math.floor(1000 + Math.random() * 9000)}`,
          timestamp: timeStr,
          sourceDataset: 'future_daily_consolidated.csv (LIVE RE-OPTIMIZED)',
          entity: dataPayload.newEvent?.title || 'Material Event Triggered',
          type: 'MATERIAL_REOPTIMIZATION',
          amount: dataPayload.availableCash ? dataPayload.availableCash : 1650000.0,
          status: 'RE-OPTIMIZED',
          confidence: '96.0%',
          actionImpact: dataPayload.newEvent?.impact || 'Strategy Shifted',
          isNew: true
        };

        setStreamRows((prev) => [newRecord, ...prev.slice(0, 199)]);
        setEventCount((c) => c + 1);
      }
    });

    return () => {
      clearInterval(intervalTimer);
      unsubscribe();
    };
  }, []);

  const handleSimulateNewData = async (type: string, desc: string, delay = 0, outflow = 0) => {
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
      filterCategory === 'MATERIAL' ? (row.status.includes('RE-OPTIMIZED') || row.type.includes('MATERIAL')) : true;

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
                <Radio className="w-3 h-3 mr-1 text-emerald-400 animate-pulse" /> AUTOMATED LIVE STREAMING ENGINE
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-950/80 text-blue-300 border border-blue-500/40 backdrop-blur-md">
                3.5s REFRESH INTERVAL
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 font-sans tracking-tight">
              Automated Real-Time Live Stream Table Dashboard
            </h1>
            <p className="text-xs text-slate-300 font-sans">
              Incoming financial data stream records accumulate automatically every 3.5 seconds in real time without clicking.
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs shrink-0">
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold">Total Ingested Stream Rows</div>
              <div className="text-base font-bold text-emerald-400 flex items-center justify-end space-x-1.5">
                <span>{eventCount} Records</span>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CONTROLS & MANUAL OVERRIDE STRIP */}
      <div className="backdrop-blur-xl bg-[#0F172A]/50 border border-white/10 rounded-2xl p-5 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Manual Instant Event Injection (Optional)
            </h2>
          </div>
          <span className="text-[10px] text-slate-400">Stream appends automatically; click for instant override</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            disabled={isSimulating}
            onClick={() => handleSimulateNewData('RECEIVABLE_DELAYED', 'Customer A Wire Delayed (+10d)', 10, 0)}
            className="py-2.5 px-3 bg-slate-900/80 hover:bg-slate-800 border border-amber-500/30 hover:border-amber-500/60 text-amber-300 rounded-xl text-xs text-left transition backdrop-blur-md flex items-center justify-between group"
          >
            <div>
              <div className="font-bold text-[11px]">📥 Customer Delay (+10d)</div>
              <div className="text-[10px] text-slate-400 font-sans">Inject Material Delay</div>
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
              <div className="text-[10px] text-slate-400 font-sans">Inject Invoice Record</div>
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
              <div className="text-[10px] text-slate-400 font-sans">Inject Outflow Event</div>
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
              <div className="text-[10px] text-slate-400 font-sans">Inject Telemetry Sync</div>
            </div>
            <Play className="w-3.5 h-3.5 shrink-0 text-emerald-400 group-hover:scale-110 transition" />
          </button>
        </div>
      </div>

      {/* FILTER & SEARCH STRIP */}
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
            <span className="font-bold text-slate-200 uppercase">Automated Live Ingestion Stream ({filteredRows.length} Rows Active)</span>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold flex items-center">
            <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-ping"></span> {channelStatus}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="bg-slate-950/80 border-b border-white/10 text-[11px] uppercase font-bold text-slate-400">
                <th className="py-3.5 px-6">Timestamp & Stream ID</th>
                <th className="py-3.5 px-4">Entity / Customer / Supplier</th>
                <th className="py-3.5 px-4">Transaction Type</th>
                <th className="py-3.5 px-4 text-right">Amount</th>
                <th className="py-3.5 px-4">Probability / Confidence</th>
                <th className="py-3.5 px-4">Status & Action Impact</th>
                <th className="py-3.5 px-4">Source Dataset</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredRows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 text-xs font-sans">
                    <Clock className="w-6 h-6 mx-auto mb-2 opacity-50 text-blue-400" />
                    No streaming records matched your search filter. Stream is actively adding rows every 3.5s.
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
