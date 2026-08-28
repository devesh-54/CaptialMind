export const formatINR = (val: number, shorthand = true): string => {
  if (shorthand) {
    if (val >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)}Cr`;
    }
    if (val >= 100000) {
      return `₹${(val / 100000).toFixed(1)}L`;
    }
    if (val >= 1000) {
      return `₹${(val / 1000).toFixed(1)}k`;
    }
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(val);
};

export const getActionColor = (action: string) => {
  switch (action) {
    case 'Pay Now':
      return 'bg-emerald-950/70 text-emerald-400 border-emerald-800/60';
    case 'Pay at Maturity':
      return 'bg-blue-950/70 text-blue-400 border-blue-800/60';
    case 'Finance':
      return 'bg-purple-950/70 text-purple-400 border-purple-800/60';
    case 'Delay':
      return 'bg-amber-950/70 text-amber-400 border-amber-800/60';
    case 'Retain':
      return 'bg-slate-800/70 text-slate-300 border-slate-700/60';
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700';
  }
};
