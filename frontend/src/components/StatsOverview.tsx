import React from 'react';
import { Shield, AlertTriangle, Scale, Coins } from 'lucide-react';
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
      title: 'TOTAL WARRANTY LOCKED',
      value: `${formatGen(stats?.total_warranty_locked || '0')} GEN`,
      subtext: 'Escrow backed by OEMs & component suppliers',
      icon: Coins,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    },
    {
      title: 'ACTIVE DEVICE VAULTS',
      value: activeCount.toString(),
      subtext: `${stats?.total_vaults || 0} lifetime registered vehicles/devices`,
      icon: Shield,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/20',
    },
    {
      title: 'CRITICAL LEMON RECALLS',
      value: criticalRecallCount.toString(),
      subtext: '100% full buyback/refund enforced by AI court',
      icon: AlertTriangle,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/20',
    },
    {
      title: 'CLAIMS SETTLED',
      value: (stats?.total_claims_settled || 0).toString(),
      subtext: 'Autonomous consensus audits concluded',
      icon: Scale,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-[#151C2C]/80 border border-slate-800 hover:border-slate-700/80 transition shadow-sm relative overflow-hidden group"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono tracking-wider text-slate-400 uppercase">
                {c.title}
              </span>
              <div className={`p-2 rounded-xl ${c.bgColor} ${c.borderColor} border`}>
                <Icon className={`w-4 h-4 ${c.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold font-mono tracking-tight text-white mb-1">
              {c.value}
            </div>
            <p className="text-xs text-slate-400">
              {c.subtext}
            </p>
            <div className="absolute inset-x-0 bottom-0 h-0.5 bg-gradient-to-r from-transparent via-slate-700 to-transparent opacity-0 group-hover:opacity-100 transition"></div>
          </div>
        );
      })}
    </div>
  );
};
