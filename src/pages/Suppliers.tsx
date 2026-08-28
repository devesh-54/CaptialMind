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
  Check,
  Star,
  Percent
} from 'lucide-react';
import { fetchSuppliersData, executeAction, triggerSimulatedEvent } from '../services/api';

export const Suppliers: React.FC = () => {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [executingSupplierId, setExecutingSupplierId] = useState<string | null>(null);
  const [executedSuppliers, setExecutedSuppliers] = useState<Record<string, boolean>>({});

  useEffect(() => {
    async function load() {
      const data = await fetchSuppliersData();
      const rawList = (data && data.length > 0) ? data : [
        {
          id: 'SUP010',
          name: 'Valeo India Pvt Ltd',
          category: 'Lighting Systems & Sensor Assemblies',
          liquidityRisk: 'LOW',
          isCritical: true,
          outstandingAmount: 22721445.28,
          onTimePaymentPct: 98.4,
          capturedDiscountTotal: 454428.90,
          discountPct: 2.0,
          paymentTerms: '2/10 Net-30'
        },
        {
          id: 'SUP003',
          name: 'Bosch Ltd',
          category: 'Powertrain Electronics & Fuel Injection',
          liquidityRisk: 'LOW',
          isCritical: true,
          outstandingAmount: 181400.00,
          onTimePaymentPct: 99.2,
          capturedDiscountTotal: 362800.00,
          discountPct: 1.5,
          paymentTerms: '1.5/10 Net-30'
        },
        {
          id: 'SUP001',
          name: 'Tata Steel Ltd',
          category: 'Auto Grade Sheet Metal & Structural Steel',
          liquidityRisk: 'LOW',
          isCritical: true,
          outstandingAmount: 920000.00,
          onTimePaymentPct: 97.8,
          capturedDiscountTotal: 184000.00,
          discountPct: 2.0,
          paymentTerms: '2/10 Net-30'
        },
        {
          id: 'SUP002',
          name: 'JSW Steel Ltd',
          category: 'Hot Rolled Chassis Frame Metal',
          liquidityRisk: 'LOW',
          isCritical: true,
          outstandingAmount: 680000.00,
          onTimePaymentPct: 96.0,
          capturedDiscountTotal: 136000.00,
          discountPct: 2.0,
          paymentTerms: '2/10 Net-30'
        },
        {
          id: 'SUP012',
          name: 'Apollo Tyres Ltd',
          category: 'Commercial Vehicle Heavy Fleet Radial Tires',
          liquidityRisk: 'LOW',
          isCritical: false,
          outstandingAmount: 420000.00,
          onTimePaymentPct: 94.2,
          capturedDiscountTotal: 84000.00,
          discountPct: 1.0,
          paymentTerms: '1/10 Net-30'
        },
        {
          id: 'SUP008',
          name: 'Bharat Forge Ltd',
          category: 'Forged Engine Crankshafts & Chassis Axles',
          liquidityRisk: 'MEDIUM',
          isCritical: false,
          outstandingAmount: 1450000.00,
          onTimePaymentPct: 91.5,
          capturedDiscountTotal: 0.00,
          discountPct: 0.0,
          paymentTerms: 'Net-45 Standard'
        }
      ];

      // Compute dynamic star priority based on discount offer & captured yield history across all snake_case and camelCase fields
      const processed = rawList.map((sup: any) => {
        const nameStr = sup.name || sup.supplier_name || 'Tier-1 Vendor';
        
        let discountPct = Number(sup.discountPct ?? sup.discount_percentage ?? sup.discount_pct ?? (
          nameStr.includes('Valeo') ? 2.0 :
          nameStr.includes('Bosch') ? 1.5 :
          nameStr.includes('Steel') ? 2.0 :
          nameStr.includes('Apollo') ? 1.0 : 0.0
        ));

        let capturedDiscount = Number(sup.capturedDiscountTotal ?? sup.captured_discount_total ?? (
          nameStr.includes('Valeo') ? 454428 :
          nameStr.includes('Bosch') ? 362800 :
          nameStr.includes('Steel') ? 184000 :
          nameStr.includes('Apollo') ? 84000 : 0
        ));

        let onTimePct = Number(sup.onTimePaymentPct ?? sup.on_time_payment_pct ?? (
          nameStr.includes('Bosch') ? 99.2 :
          nameStr.includes('Valeo') ? 98.4 :
          nameStr.includes('Steel') ? 97.8 : 91.5
        ));

        let calculatedStars = 2;
        let priorityTag = 'STANDARD TERMS (0% DISCOUNT)';
        let reason = 'Standard Net credit terms with 0% early discount. Defer payout to maturity.';

        if (discountPct >= 1.5 || capturedDiscount > 300000) {
          calculatedStars = 5;
          priorityTag = `TOP YIELD PRIORITY (${discountPct}% DISCOUNT)`;
          reason = `Active ${discountPct}% early discount. High historical captured returns.`;
        } else if (discountPct > 0 || capturedDiscount > 50000) {
          calculatedStars = 4;
          priorityTag = `HIGH DISCOUNT PRIORITY (${discountPct}% DISCOUNT)`;
          reason = `Offers ${discountPct}% early settlement discount yield.`;
        } else if (onTimePct > 93) {
          calculatedStars = 3;
          priorityTag = 'MODERATE PRIORITY';
          reason = 'Good payment compliance track record.';
        }

        return {
          ...sup,
          name: nameStr,
          category: sup.category || 'Automotive OEM Manufacturing',
          discountPct,
          capturedDiscountTotal: capturedDiscount,
          onTimePaymentPct: onTimePct,
          outstandingAmount: sup.outstandingAmount ?? (sup.amount ? sup.amount * 100000 : 920000),
          calculatedStars,
          priorityTag,
          reason,
          paymentTerms: sup.paymentTerms || (discountPct > 0 ? `${discountPct}/10 Net-30` : 'Net-45 Standard'),
          liquidityRisk: sup.liquidityRisk || sup.liquidity_risk || 'LOW',
          isCritical: sup.isCritical ?? sup.is_critical ?? (calculatedStars >= 4)
        };
      });

      setSuppliers(processed);
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
    
    if (riskFilter === 'TOP_DISCOUNT') return matchesSearch && sup.calculatedStars >= 4;
    if (riskFilter === 'CRITICAL') return matchesSearch && sup.isCritical;
    if (riskFilter === 'LOW') return matchesSearch && (sup.liquidityRisk === 'LOW' || sup.liquidityRisk === 'Low');
    if (riskFilter === 'STANDARD') return matchesSearch && sup.calculatedStars <= 3;
    return matchesSearch;
  });

  const totalOutstandingPayables = suppliers.reduce((acc, sup) => acc + (sup.outstandingAmount || 0), 0);
  const totalDiscountsCaptured = suppliers.reduce((acc, sup) => acc + (sup.capturedDiscountTotal || 0), 0);
  const topDiscountCount = suppliers.filter(s => s.calculatedStars >= 4).length;

  return (
    <div className="space-y-8 pb-12 font-mono selection:bg-blue-600 selection:text-white">
      
      {/* HEADER SECTION */}
      <div className="backdrop-blur-2xl bg-[#0F172A]/60 border border-white/10 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30 backdrop-blur-md flex items-center">
                <Building2 className="w-3 h-3 mr-1 text-blue-400" /> HISTORICAL YIELD-BASED SUPPLIER PRIORITY
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 backdrop-blur-md">
                {topDiscountCount} HIGH-YIELD DISCOUNT VENDORS
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 font-sans tracking-tight">
              Supplier Priority & Historical Discount Yield Directory
            </h1>
            <p className="text-xs text-slate-300 font-sans">
              Star ratings dynamically calculated from historical early payment discounts offered, captured yield history, and payment compliance.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center space-x-3 text-xs shrink-0">
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold">Total Discretionary Payables</div>
              <div className="text-base font-bold text-amber-400">{formatINR(totalOutstandingPayables)}</div>
            </div>
            <div className="bg-slate-900/80 border border-slate-700/60 px-4 py-2 rounded-xl backdrop-blur-md shadow-inner text-right">
              <div className="text-[10px] uppercase text-slate-400 font-bold font-sans">Total Captured Yield</div>
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
            placeholder="Search vendor name, discount, ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 outline-none focus:border-blue-500 transition font-sans"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-2 text-xs overflow-x-auto w-full md:w-auto">
          {[
            { id: 'ALL', label: 'All Vendors' },
            { id: 'TOP_DISCOUNT', label: '⭐️ High Discount Priority (4-5 Stars)' },
            { id: 'STANDARD', label: 'Standard Terms (2-3 Stars)' },
            { id: 'CRITICAL', label: 'Critical Tier-1 Only' }
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
          const stars = sup.calculatedStars || 3;

          return (
            <div 
              key={sup.id}
              className={`backdrop-blur-2xl bg-[#0F172A]/60 border rounded-2xl p-6 space-y-4 shadow-2xl transition-all duration-300 relative overflow-hidden group ${
                stars >= 5 
                  ? 'border-emerald-500/50 shadow-emerald-950/20 ring-1 ring-emerald-500/30' 
                  : stars === 4
                  ? 'border-blue-500/40'
                  : 'border-white/10'
              }`}
            >
              <div className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent ${
                stars >= 5 ? 'via-emerald-400/50' : stars === 4 ? 'via-blue-400/40' : 'via-slate-500/30'
              } to-transparent`}></div>

              {/* Top Title & Stars Row */}
              <div className="flex items-start justify-between gap-3 border-b border-white/10 pb-3">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-100 text-base font-sans tracking-tight">{sup.name}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${
                      stars >= 5 ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                      stars === 4 ? 'bg-blue-950 text-blue-300 border border-blue-800' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {sup.priorityTag}
                    </span>
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

              {/* Dynamic Star Rating Based on Discount Yield */}
              <div className="space-y-1.5 font-sans bg-slate-950/40 p-3 rounded-xl border border-white/5">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-300 font-bold flex items-center">
                    <Percent className="w-3.5 h-3.5 text-emerald-400 mr-1" /> Discount Priority Rating
                  </span>
                  <div className="flex items-center space-x-1">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star 
                        key={s} 
                        className={`w-4 h-4 ${
                          s <= stars 
                            ? 'text-amber-400 fill-amber-400' 
                            : 'text-slate-700 fill-slate-800'
                        }`} 
                      />
                    ))}
                    <span className="font-bold text-slate-200 ml-1 font-mono">{stars}/5</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed font-sans">{sup.reason}</p>
              </div>

              {/* Financial Metrics Box */}
              <div className="grid grid-cols-3 gap-3 bg-slate-950/60 p-4 rounded-xl border border-white/5 font-mono text-xs">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Outstanding</div>
                  <div className="font-bold text-slate-100 mt-0.5">{formatINR(sup.outstandingAmount)}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Discount Rate</div>
                  <div className="font-bold text-emerald-400 mt-0.5">{sup.discountPct ? `${sup.discountPct}% Active` : '0% (Net Terms)'}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Captured Yield</div>
                  <div className="font-bold text-blue-400 mt-0.5">{formatINR(sup.capturedDiscountTotal)}</div>
                </div>
              </div>

              {/* Action & Terms Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
                <div className="text-xs text-slate-400 font-sans space-y-0.5">
                  <div>Credit Terms: <strong className="text-slate-200 font-mono">{sup.paymentTerms || 'Net-30'}</strong></div>
                  <div>AI Action: <strong className="text-emerald-400 font-mono">{sup.aiStatus || 'OPTIMAL ALLOCATION'}</strong></div>
                </div>

                <button
                  disabled={isExecuted || isExecuting}
                  onClick={() => handleExecuteEarlyPayment(sup)}
                  className={`py-2 px-4 rounded-xl text-xs font-bold font-sans transition-all duration-300 shadow-lg flex items-center justify-center space-x-2 shrink-0 ${
                    isExecuted
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40 cursor-default'
                      : isExecuting
                      ? 'bg-slate-800 text-slate-400 cursor-wait'
                      : stars >= 4
                      ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/30 hover:scale-105 active:scale-95'
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
                      <span>{sup.discountPct > 0 ? `Capture ${sup.discountPct}% Discount Wire` : 'Execute Wire'}</span>
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
