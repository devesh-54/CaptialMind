import React, { useState, useEffect } from 'react';
import { mockSuppliers } from '../data/mockData';
import { formatINR } from '../utils/formatters';
import { fetchSuppliersData } from '../services/api';

export const Suppliers: React.FC = () => {
  const [suppliers, setSuppliers] = useState<any[]>(mockSuppliers);

  useEffect(() => {
    async function load() {
      const data = await fetchSuppliersData();
      if (data) {
        setSuppliers(data);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Supplier Relationship & Liquidity Risk</h1>
        <p className="text-xs text-slate-400">Strategic Importance Index and Discount Capture History</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {suppliers.map((sup) => (
          <div key={sup.id} className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-4">
            
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold text-slate-100 text-base">{sup.name}</h3>
                  {sup.isCritical && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950 text-red-400 border border-red-800">
                      CRITICAL TIER-1
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 font-mono mt-0.5">{sup.category}</p>
              </div>

              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                sup.liquidityRisk === 'LOW' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' :
                sup.liquidityRisk === 'MEDIUM' ? 'bg-amber-950 text-amber-400 border-amber-800' :
                'bg-red-950 text-red-400 border-red-800'
              }`}>
                RISK: {sup.liquidityRisk}
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-[11px] font-mono text-slate-400">
                <span>Strategic Importance</span>
                <span className="font-bold text-slate-200">{sup.strategicImportance}/5</span>
              </div>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((seg) => (
                  <div
                    key={seg}
                    className={`h-2 flex-1 rounded-sm ${
                      seg <= sup.strategicImportance ? 'bg-blue-500' : 'bg-slate-800'
                    }`}
                  ></div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 bg-slate-900/60 p-3 rounded border border-slate-800 font-mono text-xs">
              <div>
                <div className="text-[10px] text-slate-500">Outstanding</div>
                <div className="font-bold text-slate-200">{formatINR(sup.outstandingAmount)}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500">On-Time Pay</div>
                <div className="font-bold text-emerald-400">{sup.onTimePaymentPct}%</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500">Discounts Captured</div>
                <div className="font-bold text-blue-400">{formatINR(sup.capturedDiscountTotal)}</div>
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};
