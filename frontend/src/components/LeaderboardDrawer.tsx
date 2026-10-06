import React, { useState } from 'react';
import { X, Award, Shield, CheckCircle2, TrendingUp, Zap } from 'lucide-react';
import { OEMLeaderboardEntry, OEMProfile } from '../types/vault';
import { getTierBadge, shortenAddress } from '../utils/formatters';

interface LeaderboardDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  leaderboard: OEMLeaderboardEntry[];
  userProfile: OEMProfile | null;
}

export const LeaderboardDrawer: React.FC<LeaderboardDrawerProps> = ({
  isOpen,
  onClose,
  leaderboard,
  userProfile,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-[#151C2C] border-l border-slate-800 h-full flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-[#0B0F19]">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
              <Award className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h3 className="text-base font-bold font-space text-white">OEM Reliability Index</h3>
              <p className="text-xs text-slate-400">On-Chain Trust Tiers & Fast-Track Eligibility</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-6 flex-1">
          {/* User's Own Profile */}
          {userProfile && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase text-slate-400">Your OEM Profile</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono border ${getTierBadge(userProfile.tier).color}`}>
                  {getTierBadge(userProfile.tier).label}
                </span>
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold font-mono text-white">{userProfile.score}</span>
                <span className="text-xs text-slate-400 font-mono">Trust Points</span>
              </div>

              {userProfile.is_fast_track_eligible ? (
                <div className="flex items-center space-x-1.5 text-xs text-amber-400 font-mono bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">
                  <Zap className="w-3.5 h-3.5" />
                  <span>Eligible for 12-Block Fast-Track Cooling Window</span>
                </div>
              ) : (
                <div className="text-xs text-slate-400 font-mono">
                  Standard 24-Block Cooling Window (Unlock Fast-Track at ≥50 pts)
                </div>
              )}

              <div className="grid grid-cols-2 gap-2 pt-1 text-xs font-mono text-slate-400 border-t border-slate-800">
                <div>Clean Warranties: <span className="text-emerald-400 font-bold">{userProfile.clean_warranties}</span></div>
                <div>Resolved Claims: <span className="text-white font-bold">{userProfile.claims_resolved}</span></div>
              </div>
            </div>
          )}

          {/* Tiers Reference */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
            <h4 className="text-xs font-mono uppercase text-slate-300 font-semibold">Trust Tier Thresholds</h4>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex items-center justify-between text-cyan-400">
                <span>Platinum Guarantor (≥100 pts)</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-cyan-500/10 rounded border border-cyan-500/20">12 BLOCKS</span>
              </div>
              <div className="flex items-center justify-between text-amber-400">
                <span>Gold Verified OEM (≥50 pts)</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-amber-500/10 rounded border border-amber-500/20">12 BLOCKS</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Silver OEM (≥20 pts)</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-slate-500/10 rounded border border-slate-500/20">24 BLOCKS</span>
              </div>
              <div className="flex items-center justify-between text-orange-400">
                <span>Bronze OEM (&lt;20 pts)</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-orange-500/10 rounded border border-orange-500/20">24 BLOCKS</span>
              </div>
            </div>
          </div>

          {/* Leaderboard Table */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono uppercase text-slate-400">Top Verified OEMs</h4>
            <div className="space-y-2">
              {leaderboard.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No registered participants yet.</p>
              ) : (
                leaderboard.map((oem, idx) => {
                  const tierBadge = getTierBadge(oem.tier);
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between"
                    >
                      <div className="flex items-center space-x-2.5">
                        <span className="text-xs font-mono font-bold text-slate-500 w-4">#{idx + 1}</span>
                        <div>
                          <span className="text-xs font-mono text-white block">
                            {shortenAddress(oem.address, 4)}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400">
                            {oem.clean_warranties} Clean Warranties
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-bold font-mono text-amber-400 block">
                          {oem.score} pts
                        </span>
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono border ${tierBadge.color}`}>
                          {tierBadge.label}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
