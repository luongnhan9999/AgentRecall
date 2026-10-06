import React from 'react';
import { Shield, Cpu, Activity, Clock, FileWarning, Eye, AlertCircle, ArrowUpRight, CheckCircle, Scale, Award, Zap, Radio } from 'lucide-react';
import { WarrantyVault } from '../types/vault';
import { formatGen, getStatusBadge, getSeverityStyle, shortenAddress } from '../utils/formatters';

interface VaultCardProps {
  vault: WarrantyVault;
  account: string | null;
  onOpenFileClaim: (vault: WarrantyVault) => void;
  onOpenAdjudicate: (vault: WarrantyVault) => void;
  onOpenAppeal: (vault: WarrantyVault) => void;
  onOpenInspector: (vault: WarrantyVault) => void;
  onOpenSyndicate: (vault: WarrantyVault) => void;
  onFinalizeSettlement: (vaultId: number) => void;
  onCancelOrReclaim: (vaultId: number) => void;
  isProcessing: boolean;
}

export const VaultCard: React.FC<VaultCardProps> = ({
  vault,
  account,
  onOpenFileClaim,
  onOpenAdjudicate,
  onOpenAppeal,
  onOpenInspector,
  onOpenSyndicate,
  onFinalizeSettlement,
  onCancelOrReclaim,
  isProcessing,
}) => {
  const statusInfo = getStatusBadge(vault.status);
  const sevInfo = getSeverityStyle(vault.severity_score);
  const userAddr = account ? account.toLowerCase() : '';
  const isMfg = userAddr === vault.manufacturer.toLowerCase();

  return (
    <div className="bg-[#0D121F] border border-slate-800/90 hover:border-orange-500/40 rounded-3xl p-5 transition-all duration-300 flex flex-col justify-between relative group overflow-hidden shadow-lg hover:shadow-orange-950/20">
      {/* Background Accent glow */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 rounded-full blur-2xl pointer-events-none group-hover:bg-orange-500/10 transition-all"></div>

      {/* Top Header */}
      <div>
        <div className="flex items-center justify-between mb-3.5">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-orange-400">
              ECU #{vault.vault_id}
            </span>
            {vault.is_fast_track && (
              <span className="flex items-center space-x-1 px-2 py-0.5 rounded-md text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Zap className="w-3 h-3" />
                <span>12H FAST</span>
              </span>
            )}
            {vault.co_guarantor_count > 1 && (
              <span className="flex items-center space-x-1 px-2 py-0.5 rounded-md text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Award className="w-3 h-3" />
                <span>{vault.co_guarantor_count} BACKERS</span>
              </span>
            )}
          </div>
          <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-mono font-medium border ${statusInfo.color}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${statusInfo.dot} animate-pulse`}></span>
            <span>{statusInfo.label}</span>
          </span>
        </div>

        {/* VIN & Firmware */}
        <div className="mb-4">
          <h4 className="text-base font-bold font-mono text-white tracking-wide truncate group-hover:text-orange-300 transition">
            {vault.device_vin_or_serial}
          </h4>
          <div className="flex items-center space-x-3 text-xs font-mono text-slate-400 mt-1.5">
            <span className="flex items-center space-x-1">
              <Cpu className="w-3.5 h-3.5 text-orange-400" />
              <span>FW: {vault.firmware_version}</span>
            </span>
            <span className="text-slate-600">•</span>
            <span>Escrow: <strong className="text-emerald-400 font-bold">{formatGen(vault.escrow_amount)} GEN</strong></span>
          </div>
        </div>

        {/* OEM and Consumer Addresses */}
        <div className="grid grid-cols-2 gap-2 p-2.5 bg-[#080C16] rounded-2xl border border-slate-800/80 text-[11px] font-mono mb-4">
          <div>
            <span className="text-slate-500 block uppercase text-[10px]">OEM Vendor</span>
            <span className="text-slate-300 font-medium">{shortenAddress(vault.manufacturer, 4)}</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase text-[10px]">Device Owner</span>
            <span className="text-slate-300 font-medium">{shortenAddress(vault.consumer, 4)}</span>
          </div>
        </div>

        {/* Diagnostic Verdict & Severity */}
        {vault.status !== 0 && (
          <div className="p-3.5 bg-[#080C16] rounded-2xl border border-slate-800/80 space-y-2.5 mb-4">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400 flex items-center space-x-1.5">
                <Radio className="w-3 h-3 text-orange-400" />
                <span>AI Jury Verdict</span>
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${sevInfo.badge}`}>
                {vault.verdict || 'PENDING'}
              </span>
            </div>
            <p className="text-xs text-slate-300 font-mono italic line-clamp-2 bg-slate-900/60 p-2 rounded-lg border border-slate-800/40">
              "{vault.reason}"
            </p>
            {vault.severity_score > 0 && (
              <div>
                <div className="flex justify-between text-[10px] font-mono text-slate-400 mb-1">
                  <span>Critical Defect Index</span>
                  <span className="text-rose-400 font-bold">{vault.severity_score}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full ${sevInfo.bar} transition-all duration-500`} style={{ width: `${vault.severity_score}%` }}></div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="pt-3 border-t border-slate-800/80 space-y-2.5">
        <div className="flex items-center justify-between">
          <button
            onClick={() => onOpenInspector(vault)}
            className="flex items-center space-x-1.5 text-xs font-mono text-slate-400 hover:text-orange-400 transition py-1"
          >
            <Eye className="w-3.5 h-3.5 text-orange-400" />
            <span>Blackbox Telemetry</span>
          </button>

          {/* Syndicate Co-Fund button for ACTIVE vaults */}
          {vault.status === 0 && (
            <button
              onClick={() => onOpenSyndicate(vault)}
              className="text-xs font-mono text-amber-400 hover:text-amber-300 flex items-center space-x-1 font-semibold"
            >
              <Award className="w-3.5 h-3.5" />
              <span>Co-Guarantee</span>
            </button>
          )}
        </div>

        {/* Dynamic State Buttons */}
        <div className="flex flex-wrap gap-2 pt-1">
          {/* Status 0: File Claim (Consumer) */}
          {vault.status === 0 && (
            <button
              onClick={() => onOpenFileClaim(vault)}
              disabled={isProcessing}
              className="flex-1 py-2.5 px-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-xl text-xs font-bold font-mono tracking-wider transition shadow-md shadow-orange-600/20 disabled:opacity-50"
            >
              FILE LEMON CLAIM
            </button>
          )}

          {/* Status 1: Trigger AI Diagnostic Jury Adjudication */}
          {vault.status === 1 && (
            <button
              onClick={() => onOpenAdjudicate(vault)}
              disabled={isProcessing}
              className="flex-1 py-2.5 px-3 bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white rounded-xl text-xs font-bold font-mono tracking-wider transition shadow-lg shadow-rose-600/25 disabled:opacity-50 animate-pulse"
            >
              DISPATCH AI JURY
            </button>
          )}

          {/* Status 2: In Cooling Window -> Appeal or Finalize Settlement */}
          {vault.status === 2 && (
            <>
              <button
                onClick={() => onOpenAppeal(vault)}
                disabled={isProcessing}
                className="flex-1 py-2 px-3 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-medium font-space transition shadow-md shadow-purple-600/20 disabled:opacity-50"
              >
                Appeal (10% Bond)
              </button>
              <button
                onClick={() => onFinalizeSettlement(vault.vault_id)}
                disabled={isProcessing}
                className="flex-1 py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-medium font-space transition shadow-md shadow-emerald-600/20 disabled:opacity-50"
              >
                Finalize Payout
              </button>
            </>
          )}

          {/* Status 0 & Expired: OEM can reclaim cleanly */}
          {vault.status === 0 && isMfg && (
            <button
              onClick={() => onCancelOrReclaim(vault.vault_id)}
              disabled={isProcessing}
              className="py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-medium font-space transition disabled:opacity-50"
            >
              Reclaim Expired
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

