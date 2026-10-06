import React, { useState } from 'react';
import { X, Scale, AlertOctagon, Coins, AlertCircle } from 'lucide-react';
import { formatGen, formatWei } from '../utils/formatters';

interface AppealModalProps {
  isOpen: boolean;
  onClose: () => void;
  vaultId: number;
  vinSerial: string;
  escrowAmount: string;
  isFastTrack: boolean;
  onSubmit: (vaultId: number, disputeReason: string, bondWei: bigint) => Promise<void>;
  isSubmitting: boolean;
}

export const AppealModal: React.FC<AppealModalProps> = ({
  isOpen,
  onClose,
  vaultId,
  vinSerial,
  escrowAmount,
  isFastTrack,
  onSubmit,
  isSubmitting,
}) => {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  // 10% bond requirement
  const escrowWei = BigInt(escrowAmount || '0');
  let requiredBondWei = (escrowWei * 10n) / 100n;
  if (requiredBondWei === 0n && escrowWei > 0n) requiredBondWei = 1n;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (reason.trim().length < 10) {
      setError('Detailed dispute justification (at least 10 characters) is required.');
      return;
    }

    try {
      await onSubmit(vaultId, reason.trim(), requiredBondWei);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to submit appeal');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#151C2C] border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0B0F19]/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-xl">
              <Scale className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="text-base font-bold font-space text-white">Appeal AI Diagnostic Verdict</h3>
              <p className="text-xs text-slate-400 font-mono">
                Vault #{vaultId} • Window: {isFastTrack ? '12 Blocks (Fast-Track)' : '24 Blocks (Standard)'}
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

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="flex items-start space-x-2 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono">Locked Escrow Guarantee:</span>
              <span className="text-white font-mono font-bold">{formatGen(escrowAmount)} GEN</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-purple-400 font-mono flex items-center space-x-1">
                <Coins className="w-3.5 h-3.5" />
                <span>Required 10% Dispute Bond:</span>
              </span>
              <span className="text-purple-300 font-mono font-bold">{formatGen(requiredBondWei.toString())} GEN</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
              Appeal Ground & Engineering Rebuttal
            </label>
            <textarea
              rows={4}
              placeholder="State why the AI diagnostic verdict was mistaken (e.g. regenerative brake cutoff precipitated systemic BMS thermal instability, independent laboratory dyno telemetry provided)..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition resize-none"
              required
            />
          </div>

          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-xs text-purple-300 flex items-start space-x-2">
            <AlertOctagon className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p>
              Staked bond prevents griefing. If Supreme Appellate Court upholds your appeal, 100% of your bond is refunded. If dismissed, bond is forfeited to the counterparty.
            </p>
          </div>

          <div className="pt-2 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-medium font-space transition shadow-lg shadow-purple-600/20 disabled:opacity-50"
            >
              {isSubmitting ? 'Staking Bond...' : `Stake ${formatGen(requiredBondWei.toString())} GEN & Appeal`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
