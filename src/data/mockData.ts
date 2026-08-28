import { Invoice, Receivable, Supplier, ActivityEvent, DecisionRecord } from '../types/dashboard';

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
    reasoning: 'Strategic Tier-1 supplier. Captures ₹23,000 discount (32.4% annualized return). Buffer exceeds ₹15L safety floor.'
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
    detail: 'Allocated ₹18.4L across Tata Steel & Apex Logistics to capture ₹33,440 combined discounts.',
    impact: '+₹33.4k Yield'
  },
  {
    id: 'ACT-104',
    timestamp: '2m ago',
    stage: 'FORECAST',
    title: 'Receivable Risk Updated',
    detail: 'Probability shift on Bajaj Auto (82% → 64%). Shifted Zenith Packaging invoice to Dynamic Financing.',
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
    decision: 'Early Settlement - Tata Steel',
    amount: 920000,
    confidence: 96,
    status: 'Pending Approval',
    version: 'v1.2',
    reasons: [
      '2.5% discount captures ₹23,000 net value (32.4% annualized return).',
      'Post-payment cash remains at ₹33.2L, well above ₹15.0L safety reserve.',
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
