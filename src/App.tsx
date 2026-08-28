import React, { useState } from 'react';
import { PageId } from './types/dashboard';
import { TopBar } from './components/TopBar';
import { Navigation } from './components/Navigation';
import { ExplanationDrawer } from './components/ExplanationDrawer';

import { CommandCenter } from './pages/CommandCenter';
import { Invoices } from './pages/Invoices';
import { Receivables } from './pages/Receivables';
import { Suppliers } from './pages/Suppliers';
import { Financing } from './pages/Financing';
import { ScenarioSimulator } from './pages/ScenarioSimulator';
import { AgentActivity } from './pages/AgentActivity';
import { DecisionHistory } from './pages/DecisionHistory';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('command-center');
  const [drawerInvoiceId, setDrawerInvoiceId] = useState<string | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);

  const handleReoptimize = () => {
    setIsOptimizing(true);
    setTimeout(() => setIsOptimizing(false), 1200);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'command-center':
        return <CommandCenter onOpenDrawer={(id) => setDrawerInvoiceId(id)} onNavigate={(p) => setCurrentPage(p)} />;
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
      default:
        return <CommandCenter onOpenDrawer={(id) => setDrawerInvoiceId(id)} onNavigate={(p) => setCurrentPage(p)} />;
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
