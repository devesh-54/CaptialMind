import React, { useState, useEffect } from 'react';
import { formatINR } from '../utils/formatters';
import { 
  Building2, 
  Search, 
  Filter, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Play, 
  Sparkles, 
  ArrowUpRight, 
  TrendingUp, 
  Clock, 
  DollarSign, 
  Plus, 
  Zap,
  Info,
  Check
} from 'lucide-react';
import { fetchSuppliersData, executeAction, triggerSimulatedEvent } from '../services/api';

export const Suppliers: React.FC = () => {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [executingSupplierId, setExecutingSupplierId] = useState<string | null>(null);
  const [executedSuppliers, setExecutedSuppliers] = useState<Record<string, boolean>>({});
  const [selectedSupplierDetail, setSelectedSupplierDetail] = useState<any | null>(null);

  useEffect(() => {
    async function load() {
      const data = await fetchSuppliersData();
      if (data && data.length > 0) {
        setSuppliers(data);
      } else {
        // High quality fallback data for Tata Motors Tier-1 Automotive OEMs
        setSuppliers([
          {
            id: 'SUP010',
            name: 'Valeo India Pvt Ltd',
            category: 'Lighting Systems & Sensor Assemblies',
            strategicImportance: 5,
            liquidityRisk: 'LOW',
            isCritical: true,
            outstandingAmount: 22721445.28,
            onTimePaymentPct: 98.4,
            capturedDiscountTotal: 454428.90,
            paymentTerms: '2/10 Net-30',
            aiStatus: 'EARLY DISCOUNT CAPTURED',
            contactPerson: 'Arun Kumar (Key Account Director)'
          },
          {
            id: 'SUP003',
            name: 'Bosch Ltd',
            category: 'Powertrain Electronics & Fuel Injection',
            strategicImportance: 5,
            liquidityRisk: 'LOW',
            isCritical: true,
            outstandingAmount: 181400.00,
            onTimePaymentPct: 99.2,
            capturedDiscountTotal: 3628.00,
            paymentTerms: '1.5/10 Net-30',
            aiStatus: 'PAYMENT SCHEDULED',
            contactPerson: 'Deepak Sharma (Automotive Sales)'
          },
          {
            id: 'SUP001',
            name: 'Tata Steel Ltd',
            category: 'Auto Grade Sheet Metal & Structural Steel',
            strategicImportance: 5,
            liquidityRisk: 'LOW',
            isCritical: true,
            outstandingAmount: 920000.00,
            onTimePaymentPct: 97.8,
            capturedDiscountTotal: 18400.00,
            paymentTerms: 'Net-30',
            aiStatus: 'OPTIMAL ALLOCATION',
            contactPerson: 'Rajesh Mehta (Commercial Accounts)'
          },
          {
            id: 'SUP008',
            name: 'Bharat Forge Ltd',
            category: 'Forged Engine Crankshafts & Chassis Axles',
            strategicImportance: 4,
            liquidityRisk: 'MEDIUM',
            isCritical: false,
            outstandingAmount: 1450000.00,
            onTimePaymentPct: 91.5,
            capturedDiscountTotal: 0.00,
            paymentTerms: 'Net-45',
            aiStatus: 'PAY AT MATURITY',
            contactPerson: 'Vikram Kalyani (Supply Chain Lead)'
          },
          {
            id: 'SUP002',
            name: 'JSW Steel Ltd',
            category: 'Hot Rolled Chassis Frame Metal',
            strategicImportance: 4,
            liquidityRisk: 'LOW',
            isCritical: true,
            outstandingAmount: 680000.00,
            onTimePaymentPct: 96.0,
            capturedDiscountTotal: 13600.00,
            paymentTerms: 'Net-30',
            aiStatus: 'PAYMENT SCHEDULED',
            contactPerson: 'Sunil Jindal (Corporate Accounts)'
          },
          {
            id: 'SUP012',
            name: 'Apollo Tyres Ltd',
            category: 'Commercial Vehicle Heavy Fleet Radial Tires',
            strategicImportance: 3,
            liquidityRisk: 'LOW',
            isCritical: false,
            outstandingAmount: 420000.00,
            onTimePaymentPct: 94.2,
            capturedDiscountTotal: 8400.00,
            paymentTerms: 'Net-30',
            aiStatus: 'OPTIMAL ALLOCATION',
            contactPerson: 'Priya Nair (Fleet Supplies)'
          }
        ]);
      }
    }
    load();
  }, []);

  const handleExecuteEarlyPayment = async (sup: any) => {
    setExecutingSupplierId(sup.id);
    await triggerSimulatedEvent('PAYMENT_SCHEDULED', `Early settlement wire dispatched to ${sup.name}`, 0, sup.outstandingAmount);
    setTimeout(() => {
      setExecutedSuppliers(prev => ({ ...prev, [sup.id]: true }));
      setExecutingSupplierId(null);
    }, 700);
  };

  const filteredSuppliers = suppliers.filter(sup => {
    const matchesSearch = sup.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          sup.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          sup.id.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (riskFilter === 'CRITICAL') return matchesSearch && sup.isCritical;
    if (riskFilter === 'LOW') return matchesSearch && (sup.liquidityRisk === 'LOW' || sup.liquidityRisk === 'Low');
    if (riskFilter === 'MEDIUM') return matchesSearch && (sup.liquidityRisk === 'MEDIUM' || sup.liquidityRisk === 'Moderate');
    return matchesSearch;
  });

  const totalOutstandingPayables = suppliers.reduce((acc, sup) => acc + (sup.outstandingAmount || 0), 0);
  const totalDiscountsCaptured = suppliers.reduce((acc, sup) => acc + (sup.capturedDiscountTotal || 0), 0);
  const criticalCount = suppliers.filter(s => s.isCritical).length;

  return (
    <div className="space-y-8 pb-12 font-mono selection:bg-blue-600 selection:text-white">
      
      {/* HEADER SECTION */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30 backdrop-blur-md flex items-center">
                <Building2 className="w-3 h-3 mr-1 text-blue-400" /> TIER-1 OEM SUPPLIER PORTAL
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 backdrop-blur-md">
                {criticalCount} CRITICAL OEM VENDORS
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 font-sans tracking-tight">
              Supplier Relationship & Liquidity Risk Directory
            </h1>
            <p className="text-xs text-slate-300 font-sans">
              Real-time monitoring of strategic importance, early-discount yield capture, and automated payment execution.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center space-x-3 text-xs shrink-0">
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold">Total Discretionary Payables</div>
              <div className="text-base font-bold text-amber-400">{formatINR(totalOutstandingPayables)}</div>
            </div>
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold">Discounts Captured</div>
              <div className="text-base font-bold text-emerald-400">{formatINR(totalDiscountsCaptured)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* INTERACTIVE CONTROLS BAR */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-[#0F172A]/40 p-4 rounded-xl border border-white/10 backdrop-blur-xl shadow-xl">
        
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search vendor name, component, ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 outline-none focus:border-blue-500 transition font-sans"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-2 text-xs overflow-x-auto w-full md:w-auto">
          {[
            { id: 'ALL', label: 'All Vendors' },
            { id: 'CRITICAL', label: 'Critical Tier-1 Only' },
            { id: 'LOW', label: 'Low Risk' },
            { id: 'MEDIUM', label: 'Moderate Risk' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setRiskFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-bold transition shrink-0 ${
                riskFilter === tab.id
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

      </div>

      {/* SUPPLIER CARDS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredSuppliers.map((sup) => {
          const isExecuted = executedSuppliers[sup.id];
          const isExecuting = executingSupplierId === sup.id;
          const score = sup.strategicImportance || 5;

          return (
            <div 
              key={sup.id}
              className={`backdrop-blur-2xl bg-[#0F172A]/60 border rounded-2xl p-6 space-y-4 shadow-2xl transition-all duration-300 relative overflow-hidden group ${
                sup.isCritical 
                  ? 'border-blue-500/30 hover:border-blue-500/60' 
                  : 'border-white/10 hover:border-white/20'
              }`}
            >
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-400/30 to-transparent"></div>

              {/* Top Title Row */}
              <div className="flex items-start justify-between gap-3 border-b border-white/10 pb-3">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-100 text-base font-sans tracking-tight">{sup.name}</span>
                    {sup.isCritical && (
                      <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-red-950 text-red-400 border border-red-800 shrink-0">
                        CRITICAL TIER-1
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 font-sans">{sup.category}</p>
                </div>

                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border shrink-0 backdrop-blur-md ${
                  sup.liquidityRisk === 'LOW' || sup.liquidityRisk === 'Low'
                    ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                    : 'bg-amber-950 text-amber-400 border-amber-800'
                }`}>
                  RISK: {sup.liquidityRisk}
                </span>
              </div>

              {/* Strategic Importance Score */}
              <div className="space-y-1.5 font-sans">
                <div className="flex justify-between text-xs text-slate-300">
                  <span className="font-bold">Strategic Importance Index</span>
                  <span className="font-bold text-blue-400">{score}/5 Stars</span>
                </div>
                <div className="flex space-x-1.5">
                  {[1, 2, 3, 4, 5].map((seg) => (
                    <div
                      key={seg}
                      className={`h-2 flex-1 rounded-full transition-all duration-500 ${
                        seg <= score ? 'bg-gradient-to-r from-blue-500 to-emerald-400 shadow-sm' : 'bg-slate-800'
                      }`}
                    ></div>
                  ))}
                </div>
              </div>

              {/* Financial Metrics Box */}
              <div className="grid grid-cols-3 gap-3 bg-slate-950/60 p-4 rounded-xl border border-white/5 font-mono text-xs">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Outstanding</div>
                  <div className="font-bold text-slate-100 mt-0.5">{formatINR(sup.outstandingAmount)}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold">On-Time Pay</div>
                  <div className="font-bold text-emerald-400 mt-0.5">{sup.onTimePaymentPct || 98.0}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Captured Yield</div>
                  <div className="font-bold text-blue-400 mt-0.5">{formatINR(sup.capturedDiscountTotal)}</div>
                </div>
              </div>

              {/* Action & Terms Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
                <div className="text-xs text-slate-400 font-sans space-y-0.5">
                  <div>Payment Terms: <strong className="text-slate-200 font-mono">{sup.paymentTerms || 'Net-30'}</strong></div>
                  <div>AI Status: <strong className="text-emerald-400 font-mono">{sup.aiStatus || 'OPTIMAL ALLOCATION'}</strong></div>
                </div>

                <button
                  disabled={isExecuted || isExecuting}
                  onClick={() => handleExecuteEarlyPayment(sup)}
                  className={`py-2 px-4 rounded-xl text-xs font-bold font-sans transition-all duration-300 shadow-lg flex items-center justify-center space-x-2 shrink-0 ${
                    isExecuted
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40 cursor-default'
                      : isExecuting
                      ? 'bg-slate-800 text-slate-400 cursor-wait'
                      : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/30 hover:scale-105 active:scale-95'
                  }`}
                >
                  {isExecuting ? (
                    <span>Dispatching Wire...</span>
                  ) : isExecuted ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>Wire Dispatched</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Execute Early Wire</span>
                    </>
                  )}
                </button>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
