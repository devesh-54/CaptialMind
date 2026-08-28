import { OptionCandidate } from '../types/dashboard';

export const mockOptionCandidates: OptionCandidate[] = [
  {
    id: 'OPT-1',
    action: 'Pay Now',
    title: 'Pay Now (Selected)',
    score: 96,
    subScores: { liquidity: 98, financial: 95, supplier: 92, risk: 96 },
    costBenefit: 'Captures ₹33,440 net early discounts',
    riskNote: 'Stays safely above ₹15.0L floor throughout',
    breachesFloor: false,
    selected: true,
    sparklineData: [
      { day: 'Aug 28', cash: 48.2 },
      { day: 'Aug 30', cash: 38.8 },
      { day: 'Sep 02', cash: 42.1 },
      { day: 'Sep 05', cash: 36.5 },
      { day: 'Sep 08', cash: 29.4 },
      { day: 'Sep 12', cash: 34.0 },
      { day: 'Sep 18', cash: 41.5 },
      { day: 'Sep 25', cash: 52.0 }
    ]
  },
  {
    id: 'OPT-2',
    action: 'Pay at Maturity',
    title: 'Pay at Maturity',
    score: 61,
    subScores: { liquidity: 65, financial: 42, supplier: 78, risk: 62 },
    costBenefit: 'Costs ₹33,440 in forfeited discount yield',
    riskNote: 'Stays above floor; zero early settlement return',
    breachesFloor: false,
    selected: false,
    sparklineData: [
      { day: 'Aug 28', cash: 48.2 },
      { day: 'Aug 30', cash: 48.2 },
      { day: 'Sep 02', cash: 48.2 },
      { day: 'Sep 05', cash: 29.8 },
      { day: 'Sep 08', cash: 27.2 },
      { day: 'Sep 12', cash: 31.5 },
      { day: 'Sep 18', cash: 39.0 },
      { day: 'Sep 25', cash: 48.5 }
    ]
  },
  {
    id: 'OPT-3',
    action: 'Finance',
    title: 'Bank Credit Line',
    score: 74,
    subScores: { liquidity: 90, financial: 65, supplier: 85, risk: 58 },
    costBenefit: 'Costs ₹18,000 interest (8.5% APR)',
    riskNote: 'Preserves cash today; net yield reduced by interest',
    breachesFloor: false,
    selected: false,
    sparklineData: [
      { day: 'Aug 28', cash: 48.2 },
      { day: 'Aug 30', cash: 48.2 },
      { day: 'Sep 02', cash: 45.0 },
      { day: 'Sep 05', cash: 40.5 },
      { day: 'Sep 08', cash: 35.0 },
      { day: 'Sep 12', cash: 38.2 },
      { day: 'Sep 18', cash: 44.0 },
      { day: 'Sep 25', cash: 52.0 }
    ]
  },
  {
    id: 'OPT-4',
    action: 'Delay',
    title: 'Delay Payment (+10d)',
    score: 32,
    subScores: { liquidity: 40, financial: 25, supplier: 30, risk: 28 },
    costBenefit: '₹0 immediate cash outflow',
    riskNote: 'Breaches reserve floor (₹12.5L) on Day 18',
    breachesFloor: true,
    breachDay: 'Sep 18',
    selected: false,
    sparklineData: [
      { day: 'Aug 28', cash: 48.2 },
      { day: 'Aug 30', cash: 48.2 },
      { day: 'Sep 02', cash: 45.0 },
      { day: 'Sep 05', cash: 22.0 },
      { day: 'Sep 08', cash: 18.0 },
      { day: 'Sep 12', cash: 16.5 },
      { day: 'Sep 18', cash: 12.5 },
      { day: 'Sep 25', cash: 29.0 }
    ]
  },
  {
    id: 'OPT-5',
    action: 'Retain',
    title: 'Retain Cash Buffer',
    score: 45,
    subScores: { liquidity: 85, financial: 20, supplier: 35, risk: 40 },
    costBenefit: 'Maximizes nominal cash reserve',
    riskNote: 'Forfeits ₹33.4k & risks supplier delivery hold',
    breachesFloor: false,
    selected: false,
    sparklineData: [
      { day: 'Aug 28', cash: 48.2 },
      { day: 'Aug 30', cash: 48.2 },
      { day: 'Sep 02', cash: 48.2 },
      { day: 'Sep 05', cash: 48.2 },
      { day: 'Sep 08', cash: 42.0 },
      { day: 'Sep 12', cash: 40.0 },
      { day: 'Sep 18', cash: 45.0 },
      { day: 'Sep 25', cash: 52.0 }
    ]
  }
];

export const mockInvoices = [
  {
    id: 'INV-2026-081',
    supplierName: 'Tata Steel Processing',
    supplierCategory: 'Raw Materials',
    amount: 920000.0,
    dueDate: '2026-09-05',
    discountPct: 2.5,
    discountDeadline: '2026-08-30',
    priorityScore: 96,
    aiAction: 'Pay Now',
    strategicImportance: 5,
    reasoning: 'Strategic Tier-1 supplier. Captures ₹23,000 discount (32.4% annualized return). Buffer exceeds ₹15L safety floor.'
  },
  {
    id: 'INV-2026-084',
    supplierName: 'Apex Electronics Logistics',
    supplierCategory: 'Supply Chain',
    amount: 580000.0,
    dueDate: '2026-09-02',
    discountPct: 1.8,
    discountDeadline: '2026-08-31',
    priorityScore: 89,
    aiAction: 'Pay Now',
    strategicImportance: 4,
    reasoning: 'Prevents freight dispatch hold for upcoming Q3 delivery. 1.8% early payment discount captures ₹10,440.'
  },
  {
    id: 'INV-2026-089',
    supplierName: 'Infosys Cloud Operations',
    supplierCategory: 'IT Infrastructure',
    amount: 340000.0,
    dueDate: '2026-09-20',
    discountPct: 0.0,
    discountDeadline: '-',
    priorityScore: 42,
    aiAction: 'Pay at Maturity',
    strategicImportance: 3,
    reasoning: 'No early settlement discount offered. Net 30 terms allow liquidity preservation until day 28.'
  },
  {
    id: 'INV-2026-092',
    supplierName: 'Zenith Packaging Corp',
    supplierCategory: 'Packaging',
    amount: 1250000.0,
    dueDate: '2026-09-10',
    discountPct: 3.0,
    discountDeadline: '2026-08-29',
    priorityScore: 78,
    aiAction: 'Finance',
    strategicImportance: 3,
    reasoning: 'Preserves internal cash while securing 3.0% discount via Dynamic Supplier Discounting at 8.5% APR.'
  },
  {
    id: 'INV-2026-095',
    supplierName: 'Reliance Polymers',
    supplierCategory: 'Raw Materials',
    amount: 850000.0,
    dueDate: '2026-09-15',
    discountPct: 0.0,
    discountDeadline: '-',
    priorityScore: 31,
    aiAction: 'Delay',
    strategicImportance: 2,
    reasoning: 'Receivable delay from Client Beta risks temporary liquidity dip on Sept 8th. Payment scheduled for Sept 18th.'
  }
];

export const mockReceivables = [
  {
    id: 'REC-901',
    customerName: 'Mahindra Logistics',
    amount: 2450000.0,
    expectedDate: '2026-08-30',
    collectionProbability: 95.0,
    expectedDelayDays: 0,
    status: 'On Time'
  },
  {
    id: 'REC-904',
    customerName: 'Flipkart Fulfillment',
    amount: 1800000.0,
    expectedDate: '2026-09-04',
    collectionProbability: 82.0,
    expectedDelayDays: 3,
    status: 'Slight Delay'
  },
  {
    id: 'REC-908',
    customerName: 'Bajaj Auto Ancillaries',
    amount: 1200000.0,
    expectedDate: '2026-09-12',
    collectionProbability: 64.0,
    expectedDelayDays: 9,
    status: 'At Risk'
  }
];

export const mockSuppliers = [
  {
    id: 'SUP-01',
    name: 'Tata Steel Processing',
    category: 'Raw Materials',
    strategicImportance: 5,
    isCritical: true,
    liquidityRisk: 'LOW',
    outstandingInvoices: 2,
    outstandingAmount: 1450000.0,
    onTimePaymentPct: 98.0,
    capturedDiscountTotal: 142000.0
  },
  {
    id: 'SUP-02',
    name: 'Apex Electronics Logistics',
    category: 'Supply Chain',
    strategicImportance: 4,
    isCritical: true,
    liquidityRisk: 'LOW',
    outstandingInvoices: 1,
    outstandingAmount: 580000.0,
    onTimePaymentPct: 94.0,
    capturedDiscountTotal: 54000.0
  },
  {
    id: 'SUP-03',
    name: 'Zenith Packaging Corp',
    category: 'Packaging',
    strategicImportance: 3,
    isCritical: false,
    liquidityRisk: 'MEDIUM',
    outstandingInvoices: 1,
    outstandingAmount: 1250000.0,
    onTimePaymentPct: 88.0,
    capturedDiscountTotal: 37500.0
  },
  {
    id: 'SUP-04',
    name: 'Reliance Polymers',
    category: 'Raw Materials',
    strategicImportance: 2,
    isCritical: false,
    liquidityRisk: 'HIGH',
    outstandingInvoices: 1,
    outstandingAmount: 850000.0,
    onTimePaymentPct: 81.0,
    capturedDiscountTotal: 12000.0
  }
];

export const mockActivityFeed = [
  {
    id: 'ACT-105',
    timestamp: 'Just now',
    stage: 'DECIDE',
    title: 'Optimized Day 1 Capital Deployment',
    detail: 'Evaluated 5 candidates. Selected Pay Now (Score: 96/100) over Bank Finance (74/100).',
    impact: '+₹33.4k Net Yield'
  },
  {
    id: 'ACT-104',
    timestamp: '2m ago',
    stage: 'FORECAST',
    title: 'Receivable Risk Updated',
    detail: 'Probability shift on Bajaj Auto (82% → 64%). Simulated floor breach under Delay scenario.',
    impact: 'Protected ₹15.0L Floor'
  },
  {
    id: 'ACT-103',
    timestamp: '11m ago',
    stage: 'OBSERVE',
    title: 'Bank API Cash Sync',
    detail: 'HDFC Treasury Account balance confirmed: ₹48,20,000. Reserve floor verified.',
  }
];
