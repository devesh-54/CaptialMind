import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  Database, 
  Radio, 
  RefreshCw, 
  FileSpreadsheet, 
  Play, 
  CheckCircle2, 
  Clock, 
  Zap,
  Code2,
  Server
} from 'lucide-react';
import { fetchCommandCenterData, triggerSimulatedEvent, subscribeToSSEStream } from '../services/api';

export const DataStreamInspector: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'live-stream' | 'historical-data'>('live-stream');
  const [streamStatus, setStreamStatus] = useState<string>('Connected to SSE Stream');
  const [lastHeartbeat, setLastHeartbeat] = useState<string>('Just now');
  const [streamLogs, setStreamLogs] = useState<any[]>([]);
  const [commandCenterData, setCommandCenterData] = useState<any>(null);
  const [selectedCsv, setSelectedCsv] = useState<string>('invoices');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  useEffect(() => {
    async function loadData() {
      const data = await fetchCommandCenterData();
      if (data) {
        setCommandCenterData(data);
      }
    }
    loadData();

    // Subscribe to real-time Server-Sent Events stream from http://localhost:8000/api/stream
    const unsubscribe = subscribeToSSEStream((eventData) => {
      const timestamp = new Date().toLocaleTimeString();
      setLastHeartbeat(timestamp);

      if (eventData.event === 'CONNECTED') {
        setStreamStatus('ACTIVE SSE CHANNEL');
      } else if (eventData.event === 'HEARTBEAT') {
        setStreamStatus(`LIVE PULSE (${eventData.data.timestamp})`);
      } else if (eventData.event === 'REALTIME_UPDATE') {
        setStreamStatus(`EVENT RECEIVED (${eventData.data.timestamp})`);
      }

      setStreamLogs((prev) => [
        {
          id: Math.random().toString(36).substring(7),
          timestamp: timestamp,
          event: eventData.event,
          payload: eventData.data
        },
        ...prev.slice(0, 49) // Keep last 50 logs
      ]);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const handleTriggerSimulatedEvent = async (type: string, desc: string, delay = 0, outflow = 0) => {
    setIsSimulating(true);
    await triggerSimulatedEvent(type, desc, delay, outflow);
    setTimeout(() => setIsSimulating(false), 800);
  };

  const invoices = commandCenterData?.invoices || [];
  const receivables = commandCenterData?.receivables || [];
  const suppliers = commandCenterData?.suppliers || [];
  const obligations = commandCenterData?.obligations || [];

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold text-slate-100">Data Ingestion & Event Stream Inspector</h1>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Real-time monitoring of historical dataset ingestion (`historical_data_cashpilot`) and FastAPI SSE stream payloads (`http://localhost:8000/api/stream`).
          </p>
        </div>

        {/* STATUS BADGE */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center space-x-2">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="text-slate-300">Channel:</span>
            <span className="font-bold text-emerald-400">{streamStatus}</span>
          </div>

          <button
            onClick={async () => {
              const data = await fetchCommandCenterData();
              if (data) setCommandCenterData(data);
            }}
            className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-400 hover:text-white transition"
            title="Refetch backend REST state"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* TOP NAVIGATION TABS */}
      <div className="flex space-x-2 border-b border-slate-800 text-xs">
        <button
          onClick={() => setActiveSubTab('live-stream')}
          className={`pb-2 px-4 font-bold transition border-b-2 flex items-center space-x-2 ${
            activeSubTab === 'live-stream' 
              ? 'border-blue-500 text-blue-400' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Radio className="w-3.5 h-3.5" />
          <span>Real-Time SSE Event Stream ({streamLogs.length} Events)</span>
        </button>

        <button
          onClick={() => setActiveSubTab('historical-data')}
          className={`pb-2 px-4 font-bold transition border-b-2 flex items-center space-x-2 ${
            activeSubTab === 'historical-data' 
              ? 'border-blue-500 text-blue-400' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileSpreadsheet className="w-3.5 h-3.5" />
          <span>Ingested Historical Dataset Records</span>
        </button>
      </div>

      {/* TAB 1: LIVE SSE STREAM LOGS */}
      {activeSubTab === 'live-stream' && (
        <div className="space-y-6">
          
          {/* SIMULATION TRIGGER CONTROLS */}
          <div className="bg-[#0F172A] border border-blue-500/40 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-blue-400" />
                <h3 className="text-xs font-bold uppercase text-slate-200">Inject Real-Time Demo Event Stream</h3>
              </div>
              <span className="text-[10px] text-slate-400">Triggers immediate SSE broadcast over FastAPI</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                disabled={isSimulating}
                onClick={() => handleTriggerSimulatedEvent('FORECAST', 'Customer A (Mahindra) payment delayed by 10 days', 10, 0)}
                className="py-2.5 px-3 bg-slate-900 hover:bg-slate-800 border border-amber-500/40 text-amber-400 hover:text-amber-300 rounded text-xs text-left transition flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">⚠️ Customer A Delay (+10d)</div>
                  <div className="text-[10px] text-slate-400">Triggers Cash Flow Re-Forecast</div>
                </div>
                <Play className="w-3.5 h-3.5 shrink-0 ml-2" />
              </button>

              <button
                disabled={isSimulating}
                onClick={() => handleTriggerSimulatedEvent('DECIDE', 'Unexpected plant equipment outflow ₹6.0L', 0, 6)}
                className="py-2.5 px-3 bg-slate-900 hover:bg-slate-800 border border-red-500/40 text-red-400 hover:text-red-300 rounded text-xs text-left transition flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">🚨 Outflow Outbreak (₹6.0L)</div>
                  <div className="text-[10px] text-slate-400">Triggers Re-Allocation Engine</div>
                </div>
                <Play className="w-3.5 h-3.5 shrink-0 ml-2" />
              </button>

              <button
                disabled={isSimulating}
                onClick={() => handleTriggerSimulatedEvent('OBSERVE', 'Bank Treasury Cash Sync Confirmed: ₹47.27Cr', 0, 0)}
                className="py-2.5 px-3 bg-slate-900 hover:bg-slate-800 border border-emerald-500/40 text-emerald-400 hover:text-emerald-300 rounded text-xs text-left transition flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">✅ Treasury Cash Sync</div>
                  <div className="text-[10px] text-slate-400">Pushes HDFC Balance Pulse</div>
                </div>
                <Play className="w-3.5 h-3.5 shrink-0 ml-2" />
              </button>
            </div>
          </div>

          {/* STREAM LOG TABLE */}
          <div className="bg-[#0F172A] border border-slate-800 rounded-lg overflow-hidden">
            <div className="bg-slate-900/80 px-4 py-2.5 border-b border-slate-800 flex justify-between items-center text-xs">
              <span className="font-bold text-slate-300 uppercase">Live Server-Sent Events (SSE) Stream Payload Inspector</span>
              <span className="text-[10px] text-slate-500">Endpoint: http://localhost:8000/api/stream</span>
            </div>

            <div className="divide-y divide-slate-800/80 max-h-[500px] overflow-y-auto">
              {streamLogs.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  <Clock className="w-6 h-6 mx-auto mb-2 opacity-50" />
                  Listening to `/api/stream` SSE stream... Heartbeats and events will appear here in real time.
                </div>
              ) : (
                streamLogs.map((log) => (
                  <div key={log.id} className="p-3 text-xs space-y-1.5 hover:bg-slate-900/40 transition">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          log.event === 'CONNECTED' ? 'bg-blue-950 text-blue-400 border-blue-800' :
                          log.event === 'REALTIME_UPDATE' ? 'bg-emerald-950 text-emerald-400 border-emerald-800 animate-pulse' :
                          'bg-slate-800 text-slate-400 border-slate-700'
                        }`}>
                          {log.event}
                        </span>
                        <span className="text-slate-400">{log.timestamp}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">JSON Payload</span>
                    </div>

                    <pre className="bg-slate-950 p-2.5 rounded border border-slate-900 text-[11px] text-slate-300 overflow-x-auto">
                      {JSON.stringify(log.payload, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      )}

      {/* TAB 2: INGESTED HISTORICAL CSV DATASET */}
      {activeSubTab === 'historical-data' && (
        <div className="space-y-6">
          
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400 font-bold uppercase">Select Dataset File:</span>
            {['invoices', 'obligations', 'receivables', 'suppliers'].map((csvKey) => (
              <button
                key={csvKey}
                onClick={() => setSelectedCsv(csvKey)}
                className={`px-3 py-1.5 rounded-md border font-bold capitalize transition ${
                  selectedCsv === csvKey 
                    ? 'bg-blue-950 text-blue-400 border-blue-800' 
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                {csvKey}.csv
              </button>
            ))}
          </div>

          <div className="bg-[#0F172A] border border-slate-800 rounded-lg overflow-hidden">
            <div className="bg-slate-900/80 px-4 py-2.5 border-b border-slate-800 flex justify-between items-center text-xs">
              <span className="font-bold text-slate-300 uppercase">
                Parsed Dataset: `historical_data_cashpilot/data/historical/{selectedCsv}.csv`
              </span>
              <span className="text-[10px] text-emerald-400 font-bold">PARSED BY FASTAPI BACKEND</span>
            </div>

            <div className="overflow-x-auto">
              {selectedCsv === 'invoices' && (
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-900/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
                      <th className="py-2.5 px-4">Invoice ID</th>
                      <th className="py-2.5 px-4">Supplier</th>
                      <th className="py-2.5 px-4 text-right">Amount</th>
                      <th className="py-2.5 px-4">Due Date</th>
                      <th className="py-2.5 px-4">Discount</th>
                      <th className="py-2.5 px-4">Priority</th>
                      <th className="py-2.5 px-4">AI Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {invoices.map((inv: any) => (
                      <tr key={inv.id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 px-4 font-bold text-blue-400">{inv.id}</td>
                        <td className="py-2.5 px-4 text-slate-200 font-semibold">{inv.supplierName}</td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-100">{formatINR(inv.amount)}</td>
                        <td className="py-2.5 px-4 text-slate-400">{inv.dueDate}</td>
                        <td className="py-2.5 px-4 text-emerald-400 font-bold">{inv.discountPct}%</td>
                        <td className="py-2.5 px-4 text-slate-200 font-bold">{inv.priorityScore}/100</td>
                        <td className="py-2.5 px-4 font-bold text-blue-400">{inv.aiAction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedCsv === 'obligations' && (
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-900/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
                      <th className="py-2.5 px-4">Obligation ID</th>
                      <th className="py-2.5 px-4">Description / Supplier</th>
                      <th className="py-2.5 px-4 text-right">Amount</th>
                      <th className="py-2.5 px-4">Due Date</th>
                      <th className="py-2.5 px-4">Priority</th>
                      <th className="py-2.5 px-4">AI Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {obligations.map((ob: any) => (
                      <tr key={ob.id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 px-4 font-bold text-blue-400">{ob.id}</td>
                        <td className="py-2.5 px-4 text-slate-200 font-semibold">{ob.supplierName}</td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-100">{formatINR(ob.amount)}</td>
                        <td className="py-2.5 px-4 text-amber-400 font-bold">{ob.dueDate}</td>
                        <td className="py-2.5 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            ob.priority === 'CRITICAL' ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-slate-800 text-slate-300 border-slate-700'
                          }`}>
                            {ob.priority}
                          </span>
                        </td>
                        <td className="py-2.5 px-4 font-bold text-emerald-400">{ob.aiAction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedCsv === 'receivables' && (
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-900/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
                      <th className="py-2.5 px-4">Receivable ID</th>
                      <th className="py-2.5 px-4">Customer Name</th>
                      <th className="py-2.5 px-4 text-right">Amount</th>
                      <th className="py-2.5 px-4">Expected Date</th>
                      <th className="py-2.5 px-4">Confidence</th>
                      <th className="py-2.5 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {receivables.map((rec: any) => (
                      <tr key={rec.id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 px-4 font-bold text-blue-400">{rec.id}</td>
                        <td className="py-2.5 px-4 text-slate-200 font-semibold">{rec.customerName}</td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-100">{formatINR(rec.amount)}</td>
                        <td className="py-2.5 px-4 text-slate-400">{rec.expectedDate}</td>
                        <td className="py-2.5 px-4 text-emerald-400 font-bold">{rec.collectionProbability}%</td>
                        <td className="py-2.5 px-4 font-bold text-slate-200">{rec.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedCsv === 'suppliers' && (
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-900/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
                      <th className="py-2.5 px-4">Supplier ID</th>
                      <th className="py-2.5 px-4">Supplier Name</th>
                      <th className="py-2.5 px-4">Category</th>
                      <th className="py-2.5 px-4">Strategic Rating</th>
                      <th className="py-2.5 px-4">Liquidity Risk</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {suppliers.map((sup: any) => (
                      <tr key={sup.id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 px-4 font-bold text-blue-400">{sup.id}</td>
                        <td className="py-2.5 px-4 text-slate-200 font-semibold">{sup.name}</td>
                        <td className="py-2.5 px-4 text-slate-400">{sup.category}</td>
                        <td className="py-2.5 px-4 text-blue-400 font-bold">{sup.strategicImportance}/5</td>
                        <td className="py-2.5 px-4 font-bold text-emerald-400">{sup.liquidityRisk}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

        </div>
      )}
    </div>
  );
};
