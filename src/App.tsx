import React, { useState, useEffect } from 'react';
import { PageId } from './types/dashboard';
import { TopBar } from './components/TopBar';
import { Navigation } from './components/Navigation';
import { ExplanationDrawer } from './components/ExplanationDrawer';
import { subscribeToSSEStream, triggerSimulatedEvent, fetchCommandCenterData } from './services/api';

import { CommandCenter } from './pages/CommandCenter';
import { TodaysDecisions } from './pages/TodaysDecisions';
import { Invoices } from './pages/Invoices';
import { Receivables } from './pages/Receivables';
import { Suppliers } from './pages/Suppliers';
import { Financing } from './pages/Financing';
import { ScenarioSimulator } from './pages/ScenarioSimulator';
import { AgentActivity } from './pages/AgentActivity';
import { DecisionHistory } from './pages/DecisionHistory';
import { DataStreamInspector } from './pages/DataStreamInspector';
import { ExecutionSequence } from './pages/ExecutionSequence';
import { LiveStreamTable } from './pages/LiveStreamTable';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('command-center');
  const [drawerInvoiceId, setDrawerInvoiceId] = useState<string | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [liveStreamStatus, setLiveStreamStatus] = useState<string>('Connecting...');
  
  const [liveData, setLiveData] = useState<any>(null);

  useEffect(() => {
    async function loadInitial() {
      const data = await fetchCommandCenterData();
      if (data) {
        setLiveData(data);
      }
    }
    loadInitial();

    const unsubscribe = subscribeToSSEStream((streamEvent) => {
      if (streamEvent.event === 'REALTIME_UPDATE') {
        const payload = streamEvent.data;
        setLiveData((prev: any) => ({
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
      case 'todays-decisions':
        return <TodaysDecisions />;
      case 'live-stream-table':
        return <LiveStreamTable />;
      case 'execution-sequence':
        return <ExecutionSequence liveData={liveData} onOpenDrawer={(id) => setDrawerInvoiceId(id)} />;
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
      <TopBar onReoptimize={handleReoptimize} isOptimizing={isOptimizing} />

      <div className="flex-1 flex overflow-hidden">
        <Navigation currentPage={currentPage} onSelectPage={(page) => setCurrentPage(page)} />

        <main className="flex-1 p-6 overflow-y-auto max-w-7xl">
          {renderPage()}
        </main>
      </div>

      <ExplanationDrawer 
        invoiceId={drawerInvoiceId} 
        onClose={() => setDrawerInvoiceId(null)} 
        onNavigate={(p) => setCurrentPage(p)}
      />
    </div>
  );
}

export default App;
