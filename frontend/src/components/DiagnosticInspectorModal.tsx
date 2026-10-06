import React, { useState } from 'react';
import { X, ShieldAlert, Cpu, Hash, ExternalLink, Activity, Award, CheckCircle, Scale } from 'lucide-react';
import { WarrantyVault, SyndicatePledge } from '../types/vault';
import { formatGen, getStatusBadge, getSeverityStyle, shortenAddress } from '../utils/formatters';

interface DiagnosticInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  vault: WarrantyVault | null;
  pledges: SyndicatePledge[];
  onAdjudicateAppeal: (vaultId: number, supplementalUrl: string) => Promise<void>;
  isAdjudicatingAppeal: boolean;
}

export const DiagnosticInspectorModal: React.FC<DiagnosticInspectorModalProps> = ({
  isOpen,
  onClose,
  vault,
  pledges,
  onAdjudicateAppeal,
  isAdjudicatingAppeal,
}) => {
  const [supplementalUrl, setSupplementalUrl] = useState('');

  if (!isOpen || !vault) return null;

  const statusInfo = getStatusBadge(vault.status);
  const sevInfo = getSeverityStyle(vault.severity_score);

  const handleAppellateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supplementalUrl.trim()) return;
    await onAdjudicateAppeal(vault.vault_id, supplementalUrl.trim());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
      <div className="bg-[#151C2C] border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0B0F19]/95 backdrop-blur-md">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-orange-500/10 border border-orange-500/20 rounded-xl">
              <Cpu className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold font-space text-white">Diagnostic Blackbox Inspector</h3>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono border ${statusInfo.color}`}>
                  {statusInfo.label}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Vault #{vault.vault_id} • {vault.device_vin_or_serial}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Escrow Locked</span>
              <span className="text-sm font-bold font-mono text-emerald-400">{formatGen(vault.escrow_amount)} GEN</span>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Firmware Build</span>
              <span className="text-sm font-bold font-mono text-white">{vault.firmware_version}</span>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">AI Confidence</span>
              <span className="text-sm font-bold font-mono text-orange-400">{vault.confidence}%</span>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Severity Score</span>
              <span className="text-sm font-bold font-mono text-rose-400">{vault.severity_score}/100</span>
            </div>
          </div>

          {/* AI Diagnostic Verdict Banner */}
          <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-orange-400" />
                <span className="text-xs font-mono uppercase text-slate-300 font-semibold">
                  AI Jury Adjudication Verdict
                </span>
              </div>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono border font-semibold ${sevInfo.badge}`}>
                {vault.verdict || 'PENDING'}
              </span>
            </div>

            <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono leading-relaxed">
              "{vault.reason || 'Awaiting diagnostic log submission and consensus evaluation.'}"
            </p>

            {/* Severity Gauge */}
            <div>
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>Defect Severity Index</span>
                <span>{vault.severity_score} / 100 ({sevInfo.label})</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full ${sevInfo.bar} transition-all duration-500`}
                  style={{ width: `${vault.severity_score}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Cryptographic Evidence Digest */}
          <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
            <div className="flex items-center space-x-2 text-xs font-mono text-slate-300">
              <Hash className="w-4 h-4 text-emerald-400" />
              <span className="font-semibold uppercase">Immutable SHA-256 Telemetry Digest</span>
            </div>
            <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-emerald-400 break-all select-all">
              {vault.evidence_hash || 'Pending Telemetry Consensus Hash'}
            </div>
            {vault.diagnostic_log_url && (
              <div className="flex items-center justify-between pt-1 text-xs">
                <span className="text-slate-400 font-mono">Raw Telemetry Source:</span>
                <a
                  href={vault.diagnostic_log_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-orange-400 hover:text-orange-300 flex items-center space-x-1 font-mono"
                >
                  <span className="truncate max-w-[260px]">{vault.diagnostic_log_url}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>

          {/* Syndicate Co-Guarantor Escrow Pledges (Milestone v3) */}
          <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono uppercase text-slate-300 font-semibold flex items-center space-x-1.5">
                <Award className="w-4 h-4 text-amber-400" />
                <span>Syndicate Warranty Co-Guarantors ({pledges.length})</span>
              </span>
              <span className="text-slate-400 font-mono text-[11px]">Proportional Solvency Protection</span>
            </div>

            <div className="space-y-2 max-h-40 overflow-y-auto">
              {pledges.length === 0 ? (
                <p className="text-xs text-slate-500 italic">Sole manufacturer escrow backing.</p>
              ) : (
                pledges.map((p, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="text-slate-300 font-mono font-medium block">
                        {shortenAddress(p.guarantor, 6)}
                      </span>
                      <span className="text-[10px] text-amber-400 font-mono uppercase">{p.role}</span>
                    </div>
                    <span className="text-emerald-400 font-mono font-bold">{formatGen(p.amount)} GEN</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Appellate Review Trigger (If DISPUTED) */}
          {vault.status === 6 && (
            <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl space-y-3">
              <div className="flex items-center space-x-2 text-xs font-mono text-purple-300 font-semibold">
                <Scale className="w-4 h-4 text-purple-400" />
                <span>Supreme Appellate Court: Adjudicate Dispute</span>
              </div>
              <p className="text-xs text-slate-300">
                A 10% dispute bond has been staked ({formatGen(vault.dispute_bond)} GEN). Provide supplemental independent engineering lab audit logs to trigger appellate consensus.
              </p>
              <form onSubmit={handleAppellateSubmit} className="space-y-2 pt-1">
                <input
                  type="url"
                  placeholder="https://independent-lab.org/vin8812a_camera_test.txt"
                  value={supplementalUrl}
                  onChange={(e) => setSupplementalUrl(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition"
                  required
                />
                <button
                  type="submit"
                  disabled={isAdjudicatingAppeal}
                  className="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-medium font-space transition shadow-lg shadow-purple-600/20 disabled:opacity-50"
                >
                  {isAdjudicatingAppeal ? 'Appellate Consensus in Progress...' : 'Execute Supreme Appellate Adjudication'}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
