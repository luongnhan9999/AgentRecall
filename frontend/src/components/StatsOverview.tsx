import React from 'react';
import { Shield, AlertTriangle, Scale, Coins, Zap } from 'lucide-react';
import { formatGen } from '../utils/formatters';
import { ProtocolStats } from '../types/vault';

interface StatsOverviewProps {
  stats: ProtocolStats | null;
  activeCount: number;
  criticalRecallCount: number;
}

export const StatsOverview: React.FC<StatsOverviewProps> = ({
  stats,
  activeCount,
  criticalRecallCount,
}) => {
  const cards = [
    {
      title: 'TOTAL WARRANTY ESCROW',
      value: `${formatGen(stats?.total_warranty_locked || '0')} GEN`,
      subtext: 'Cryptographically locked by OEMs & syndicates',
      icon: Coins,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      glowColor: 'group-hover:shadow-emerald-950/40',
    },
    {
      title: 'ACTIVE TELEMETRY VAULTS',
      value: activeCount.toString(),
      subtext: `${stats?.total_vaults || 0} registered fleet units on StudioNet`,
      icon: Shield,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/30',
      glowColor: 'group-hover:shadow-orange-950/40',
    },
    {
      title: 'CRITICAL LEMON LIQUIDATIONS',
      value: criticalRecallCount.toString(),
      subtext: '100% full buyback/refund enforced by AI court',
      icon: AlertTriangle,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/30',
      glowColor: 'group-hover:shadow-rose-950/40',
    },
    {
      title: 'AI JURY CONSENSUS SETTLED',
      value: (stats?.total_claims_settled || 0).toString(),
      subtext: 'GenVM subjective diagnostic audits concluded',
      icon: Scale,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/30',
      glowColor: 'group-hover:shadow-cyan-950/40',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className={`p-5 rounded-3xl bg-[#090D18]/90 border border-slate-800/80 hover:border-orange-500/30 transition-all duration-300 shadow-xl ${c.glowColor} relative overflow-hidden group`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-mono tracking-wider text-slate-400 uppercase font-semibold">
                {c.title}
              </span>
              <div className={`p-2.5 rounded-2xl ${c.bgColor} ${c.borderColor} border shadow-inner`}>
                <Icon className={`w-4 h-4 ${c.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold font-mono tracking-tight text-white mb-1">
              {c.value}
            </div>
            <p className="text-xs text-slate-400 font-mono">
              {c.subtext}
            </p>
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-transparent via-orange-500/40 to-transparent opacity-0 group-hover:opacity-100 transition duration-500"></div>
          </div>
        );
      })}
    </div>
  );
};

