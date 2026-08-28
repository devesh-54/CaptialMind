import React, { useState, useEffect } from 'react';
import { PageId } from './types/dashboard';
import { TopBar } from './components/TopBar';
import { Navigation } from './components/Navigation';
import { ExplanationDrawer } from './components/ExplanationDrawer';
import { subscribeToSSEStream, triggerSimulatedEvent, fetchCommandCenterData } from './services/api';

import { CommandCenter } from './pages/CommandCenter';
import { Invoices } from './pages/Invoices';
import { Receivables } from './pages/Receivables';
import { Suppliers } from './pages/Suppliers';
import { Financing } from './pages/Financing';
import { ScenarioSimulator } from './pages/ScenarioSimulator';
import { AgentActivity } from './pages/AgentActivity';
import { DecisionHistory } from './pages/DecisionHistory';
import { DataStreamInspector } from './pages/DataStreamInspector';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('command-center');
  const [drawerInvoiceId, setDrawerInvoiceId] = useState<string | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [liveStreamStatus, setLiveStreamStatus] = useState<string>('Connecting...');
  
  // Real-time live streaming state passed dynamically to all views
  const [liveData, setLiveData] = useState<any>(null);

  useEffect(() => {
    // Initial fetch from backend REST API
    async function loadInitial() {
      const data = await fetchCommandCenterData();
      if (data) {
        setLiveData(data);
      }
    }
    loadInitial();

    // Persistent SSE stream listener for real-time live updates
    const unsubscribe = subscribeToSSEStream((streamEvent) => {
      if (streamEvent.event === 'CONNECTED') {
        setLiveStreamStatus('LIVE SSE CONNECTED');
      } else if (streamEvent.event === 'HEARTBEAT') {
        setLiveStreamStatus(`LIVE • ${streamEvent.data.timestamp}`);
      } else if (streamEvent.event === 'REALTIME_UPDATE') {
        setLiveStreamStatus(`RE-OPTIMIZED • ${streamEvent.data.timestamp}`);
        const payload = streamEvent.data;
        setLiveData((prev: any) => ({
          ...prev,
          kpis: {
            ...prev?.kpis,
            availableCash: payload.availableCash ?? prev?.kpis?.availableCash ?? 2554079.97,
            deployableCapital: (payload.availableCash ? payload.availableCash - 970000.0 : prev?.kpis?.deployableCapital)
          },
          heroRecommendation: payload.heroRecommendation || prev?.heroRecommendation,
          candidates: payload.candidates || prev?.candidates,
          forecast: payload.forecast || prev?.forecast,
          receivables: payload.receivables || prev?.receivables,
          activityFeed: payload.newEvent ? [payload.newEvent, ...(prev?.activityFeed || [])] : prev?.activityFeed
        }));
      } else if (streamEvent.event === 'TELEMETRY_PING') {
        setLiveStreamStatus(`TELEMETRY PING • ${streamEvent.data.timestamp}`);
        if (streamEvent.data?.availableCash) {
          setLiveData((prev: any) => ({
            ...prev,
            kpis: {
              ...prev?.kpis,
              availableCash: streamEvent.data.availableCash,
              deployableCapital: Math.max(0, streamEvent.data.availableCash - 970000.0)
            }
          }));
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const handleReoptimize = async () => {
    setIsOptimizing(true);
    await triggerSimulatedEvent(
      'DECIDE',
      'Manual Re-Optimization Triggered',
      0,
      0
    );
    setTimeout(() => setIsOptimizing(false), 1000);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'command-center':
        return <CommandCenter liveData={liveData} onOpenDrawer={(id) => setDrawerInvoiceId(id)} onNavigate={(p) => setCurrentPage(p)} />;
      case 'invoices':
        return <Invoices onOpenDrawer={(id) => setDrawerInvoiceId(id)} />;
      case 'receivables':
        return <Receivables />;
      case 'suppliers':
        return <Suppliers />;
      case 'financing':
        return <Financing />;
      case 'scenario-simulator':
        return <ScenarioSimulator />;
      case 'agent-activity':
        return <AgentActivity />;
      case 'decision-history':
        return <DecisionHistory onOpenDrawer={(id) => setDrawerInvoiceId(id)} />;
      case 'data-stream':
        return <DataStreamInspector />;
      default:
        return <CommandCenter liveData={liveData} onOpenDrawer={(id) => setDrawerInvoiceId(id)} onNavigate={(p) => setCurrentPage(p)} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 font-sans flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Top Header Bar */}
      <TopBar onReoptimize={handleReoptimize} isOptimizing={isOptimizing} />

      {/* Main Content Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <Navigation currentPage={currentPage} onSelectPage={(page) => setCurrentPage(page)} />

        {/* Dynamic Page Content */}
        <main className="flex-1 p-6 overflow-y-auto max-w-7xl">
          {renderPage()}
        </main>
      </div>

      {/* Global Audit & Explanation Drawer */}
      <ExplanationDrawer 
        invoiceId={drawerInvoiceId} 
        onClose={() => setDrawerInvoiceId(null)} 
        onNavigate={(p) => setCurrentPage(p)}
      />
    </div>
  );
}

export default App;
