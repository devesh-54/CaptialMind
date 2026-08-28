import React from 'react';
import { mockActivityFeed } from '../data/mockData';
import { Eye, TrendingUp, Cpu, PlayCircle } from 'lucide-react';

export const AgentActivity: React.FC = () => {
  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'OBSERVE':
        return <Eye className="w-4 h-4 text-blue-400" />;
      case 'FORECAST':
        return <TrendingUp className="w-4 h-4 text-purple-400" />;
      case 'DECIDE':
        return <Cpu className="w-4 h-4 text-emerald-400" />;
      case 'EXECUTE':
        return <PlayCircle className="w-4 h-4 text-amber-400" />;
      default:
        return <Eye className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Autonomous Agent Activity Timeline</h1>
        <p className="text-xs text-slate-400">Live Stream of Autonomous Sense-Make-Decide-Execute Loop Operations</p>
      </div>

      <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-6 relative">
        <div className="absolute left-9 top-8 bottom-8 w-0.5 bg-slate-800"></div>

        <div className="space-y-8 relative">
          {mockActivityFeed.map((act) => (
            <div key={act.id} className="flex items-start space-x-4 group">
              
              {/* Event stage icon */}
              <div className="w-8 h-8 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center z-10 shadow">
                {getStageIcon(act.stage)}
              </div>

              {/* Event details */}
              <div className="flex-1 bg-slate-900/60 border border-slate-800 rounded-lg p-4 font-mono space-y-1">
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-950 text-blue-400 border border-blue-800">
                      {act.stage}
                    </span>
                    <h3 className="font-bold text-slate-200 text-sm font-sans">{act.title}</h3>
                  </div>
                  <span className="text-[11px] text-slate-500">{act.timestamp}</span>
                </div>

                <p className="text-xs text-slate-400 pt-1 leading-relaxed font-sans">{act.detail}</p>

                {act.impact && (
                  <div className="pt-2 flex justify-end">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                      {act.impact}
                    </span>
                  </div>
                )}
              </div>

            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
