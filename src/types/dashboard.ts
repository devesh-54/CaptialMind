export type PageId = 
  | 'command-center'
  | 'invoices'
  | 'receivables'
  | 'suppliers'
  | 'financing'
  | 'scenario-simulator'
  | 'agent-activity'
  | 'decision-history';

export type AIActionType = 'Pay Now' | 'Pay at Maturity' | 'Finance' | 'Delay' | 'Retain';

export interface OptionCandidate {
  id: string;
  action: AIActionType;
  title: string;
  score: number; // 0-100
  costBenefit: string;
  riskNote: string;
  breachesFloor: boolean;
  breachDay?: string;
  selected: boolean;
  sparklineData: { day: string; cash: number }[];
  tradeoffRationale?: string;
}

export interface Invoice {
  id: string;
  supplierName: string;
  supplierCategory: string;
  amount: number;
  dueDate: string;
  discountPct: number;
  discountDeadline: string;
  priorityScore: number;
  aiAction: AIActionType;
  strategicImportance: 1 | 2 | 3 | 4 | 5;
  reasoning: string;
  candidates?: OptionCandidate[];
}

export interface Receivable {
  id: string;
  customerName: string;
  amount: number;
  expectedDate: string;
  collectionProbability: number;
  expectedDelayDays: number;
  status: 'On Time' | 'Slight Delay' | 'At Risk';
}

export interface Supplier {
  id: string;
  name: string;
  category: string;
  strategicImportance: 1 | 2 | 3 | 4 | 5;
  isCritical: boolean;
  liquidityRisk: 'LOW' | 'MEDIUM' | 'HIGH';
  outstandingInvoices: number;
  outstandingAmount: number;
  onTimePaymentPct: number;
  capturedDiscountTotal: number;
}

export interface ActivityEvent {
  id: string;
  timestamp: string;
  stage: 'OBSERVE' | 'FORECAST' | 'DECIDE' | 'EXECUTE';
  title: string;
  detail: string;
  impact?: string;
}

export interface DecisionRecord {
  id: string;
  timestamp: string;
  triggerEvent: string;
  decision: string;
  amount: number;
  confidence: number;
  status: 'Executed' | 'Pending Approval' | 'Superseded';
  version?: string;
  supersededBy?: string;
  reasons: string[];
}
