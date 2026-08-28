export type PageId = 
  | 'command-center' 
  | 'todays-decisions'
  | 'execution-sequence'
  | 'invoices' 
  | 'receivables' 
  | 'suppliers' 
  | 'financing' 
  | 'scenario-simulator' 
  | 'agent-activity' 
  | 'decision-history'
  | 'data-stream'
  | 'live-stream-table';

export interface KPIState {
  availableCash: number;
  protectedCash: number;
  deployableCapital: number;
  risk30d: 'LOW' | 'MEDIUM' | 'HIGH';
  wcEfficiency: number;
  financingExposure: number;
}

export interface SubScores {
  liquidity: number;
  financial: number;
  supplier: number;
  risk: number;
}

export interface OptionCandidate {
  id: string;
  action: 'Pay Now' | 'Pay at Maturity' | 'Finance' | 'Delay' | 'Retain';
  title: string;
  score: number;
  subScores?: SubScores;
  costBenefit: string;
  riskNote: string;
  breachesFloor: boolean;
  breachDay?: string;
  selected: boolean;
  sparklineData: { day: string; cash: number }[];
}

export interface HeroRecommendation {
  title: string;
  confidence: number;
  breakdown: { label: string; amount: number }[];
  reasoning: string;
}
