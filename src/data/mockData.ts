import { Invoice, Receivable, Supplier, ActivityEvent, DecisionRecord, OptionCandidate } from '../types/dashboard';

export const mockOptionCandidates: OptionCandidate[] = [
  {
    id: 'OPT-1',
    action: 'Pay Now',
    title: 'Pay Now (Selected)',
    score: 96,
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
      { day: 'Sep 25', cash: 52.0 },
    ]
  },
  {
    id: 'OPT-2',
    action: 'Pay at Maturity',
    title: 'Pay at Maturity',
    score: 61,
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
      { day: 'Sep 25', cash: 48.5 },
    ]
  },
  {
    id: 'OPT-3',
    action: 'Finance',
    title: 'Bank Credit Line',
    score: 74,
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
      { day: 'Sep 25', cash: 52.0 },
    ]
  },
  {
    id: 'OPT-4',
    action: 'Delay',
    title: 'Delay Payment (+10d)',
    score: 32,
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
      { day: 'Sep 25', cash: 29.0 },
    ]
  },
  {
    id: 'OPT-5',
    action: 'Retain',
    title: 'Retain Cash Buffer',
    score: 45,
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
      { day: 'Sep 25', cash: 52.0 },
    ]
  }
];

export const mockInvoices: Invoice[] = [
  {
    id: 'INV-2026-081',
    supplierName: 'Tata Steel Processing',
    supplierCategory: 'Raw Materials',
    amount: 920000,
    dueDate: '2026-09-05',
    discountPct: 2.5,
    discountDeadline: '2026-08-30',
    priorityScore: 96,
    aiAction: 'Pay Now',
    strategicImportance: 5,
    reasoning: 'Strategic Tier-1 supplier. Captures ₹23,000 discount (32.4% annualized return). Buffer exceeds ₹15L safety floor.',
    candidates: mockOptionCandidates
  },
  {
    id: 'INV-2026-084',
    supplierName: 'Apex Electronics Logistics',
    supplierCategory: 'Supply Chain',
    amount: 580000,
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
    amount: 340000,
    dueDate: '2026-09-20',
    discountPct: 0,
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
    amount: 1250000,
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
    amount: 850000,
    dueDate: '2026-09-15',
    discountPct: 0,
    discountDeadline: '-',
    priorityScore: 31,
    aiAction: 'Delay',
    strategicImportance: 2,
    reasoning: 'Receivable delay from Client Beta risks temporary liquidity dip on Sept 8th. Payment scheduled for Sept 18th.'
  }
];

export const mockReceivables: Receivable[] = [
  {
    id: 'REC-901',
    customerName: 'Mahindra Logistics',
    amount: 2450000,
    expectedDate: '2026-08-30',
    collectionProbability: 95,
    expectedDelayDays: 0,
    status: 'On Time'
  },
  {
    id: 'REC-904',
    customerName: 'Flipkart Fulfillment',
    amount: 1800000,
    expectedDate: '2026-09-04',
    collectionProbability: 82,
    expectedDelayDays: 3,
    status: 'Slight Delay'
  },
  {
    id: 'REC-908',
    customerName: 'Bajaj Auto Ancillaries',
    amount: 1200000,
    expectedDate: '2026-09-12',
    collectionProbability: 64,
    expectedDelayDays: 9,
    status: 'At Risk'
  }
];

export const mockSuppliers: Supplier[] = [
  {
    id: 'SUP-01',
    name: 'Tata Steel Processing',
    category: 'Raw Materials',
    strategicImportance: 5,
    isCritical: true,
    liquidityRisk: 'LOW',
    outstandingInvoices: 2,
    outstandingAmount: 1450000,
    onTimePaymentPct: 98,
    capturedDiscountTotal: 142000
  },
  {
    id: 'SUP-02',
    name: 'Apex Electronics Logistics',
    category: 'Supply Chain',
    strategicImportance: 4,
    isCritical: true,
    liquidityRisk: 'LOW',
    outstandingInvoices: 1,
    outstandingAmount: 580000,
    onTimePaymentPct: 94,
    capturedDiscountTotal: 54000
  },
  {
    id: 'SUP-03',
    name: 'Zenith Packaging Corp',
    category: 'Packaging',
    strategicImportance: 3,
    isCritical: false,
    liquidityRisk: 'MEDIUM',
    outstandingInvoices: 1,
    outstandingAmount: 1250000,
    onTimePaymentPct: 88,
    capturedDiscountTotal: 37500
  },
  {
    id: 'SUP-04',
    name: 'Reliance Polymers',
    category: 'Raw Materials',
    strategicImportance: 2,
    isCritical: false,
    liquidityRisk: 'HIGH',
    outstandingInvoices: 1,
    outstandingAmount: 850000,
    onTimePaymentPct: 81,
    capturedDiscountTotal: 12000
  }
];

export const mockActivityFeed: ActivityEvent[] = [
  {
    id: 'ACT-105',
    timestamp: '14s ago',
    stage: 'DECIDE',
    title: 'Optimized Day 1 Capital Deployment',
    detail: 'Evaluated 5 candidates. Selected Pay Now (Score: 96/100) over Bank Finance (74/100) & Delay (32/100).',
    impact: '+₹33.4k Net Yield'
  },
  {
    id: 'ACT-104',
    timestamp: '2m ago',
    stage: 'FORECAST',
    title: 'Receivable Risk Updated',
    detail: 'Probability shift on Bajaj Auto (82% → 64%). Simulated floor breach under Delay scenario on Day 18.',
    impact: 'Protected ₹15.0L Floor'
  },
  {
    id: 'ACT-103',
    timestamp: '11m ago',
    stage: 'OBSERVE',
    title: 'Bank API Cash Sync',
    detail: 'HDFC Treasury Account balance confirmed: ₹48,20,000. Operating reserve constraint verified.',
  },
  {
    id: 'ACT-102',
    timestamp: '45m ago',
    stage: 'EXECUTE',
    title: 'Automated Payment Released',
    detail: 'Executed batch transfer ₹4,50,000 for Invoice #INV-2026-077 (Larsen & Toubro).',
  }
];

export const mockDecisionHistory: DecisionRecord[] = [
  {
    id: 'DEC-8801',
    timestamp: '2026-08-28 14:45',
    triggerEvent: 'Daily Working Capital Run',
    decision: 'Early Settlement - Tata Steel (Pay Now)',
    amount: 920000,
    confidence: 96,
    status: 'Pending Approval',
    version: 'v1.2',
    reasons: [
      'Pay Now candidate scored 96/100 (runner-up Bank Finance scored 74/100).',
      '2.5% discount captures ₹23,000 net value (32.4% annualized return).',
      'Post-payment cash remains at ₹33.2L, well above ₹15.0L safety reserve floor.',
      'Tata Steel priority rating (5/5) critical for Q3 delivery guarantees.'
    ]
  },
  {
    id: 'DEC-8794',
    timestamp: '2026-08-27 10:15',
    triggerEvent: 'Flipkart Payment Delay (+4d)',
    decision: 'Switch Zenith Packaging to Credit Line',
    amount: 1250000,
    confidence: 88,
    status: 'Executed',
    version: 'v2.0',
    supersededBy: 'DEC-8801',
    reasons: [
      'Flipkart expected payment shifted from Aug 29 to Sept 2.',
      'Prevents cash floor dip below ₹15L threshold on Sept 1st.'
    ]
  }
];
