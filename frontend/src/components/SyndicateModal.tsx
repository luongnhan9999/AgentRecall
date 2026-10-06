import React, { useState } from 'react';
import { X, Award, Coins, AlertCircle } from 'lucide-react';
import { formatGen, formatWei } from '../utils/formatters';

interface SyndicateModalProps {
  isOpen: boolean;
  onClose: () => void;
  vaultId: number;
  vinSerial: string;
  currentEscrow: string;
  onSubmit: (vaultId: number, pledgeWei: bigint) => Promise<void>;
  isSubmitting: boolean;
}

export const SyndicateModal: React.FC<SyndicateModalProps> = ({
  isOpen,
  onClose,
  vaultId,
  vinSerial,
  currentEscrow,
  onSubmit,
  isSubmitting,
}) => {
  const [pledgeGen, setPledgeGen] = useState('0.01');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const wei = formatWei(pledgeGen);
    if (wei <= 0n) {
      setError('Co-guarantor contribution must be greater than 0 GEN.');
      return;
    }
    try {
      await onSubmit(vaultId, wei);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to submit syndicate pledge');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#151C2C] border border-slate-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0B0F19]/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
              <Award className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h3 className="text-base font-bold font-space text-white">Syndicate Co-Guarantor Escrow</h3>
              <p className="text-xs text-slate-400 font-mono">Vault #{vaultId} • {vinSerial}</p>
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

          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs flex justify-between items-center">
            <span className="text-slate-400 font-mono">Current Vault Escrow:</span>
            <span className="text-emerald-400 font-mono font-bold">{formatGen(currentEscrow)} GEN</span>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
              Co-Guarantee Amount (GEN)
            </label>
            <input
              type="number"
              step="0.005"
              min="0.001"
              value={pledgeGen}
              onChange={(e) => setPledgeGen(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white focus:outline-none focus:border-amber-500 transition"
              required
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Tier-1 battery manufacturers & component suppliers co-guarantee firmware reliability with proportional solvency clawback.
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
              className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-medium font-space transition shadow-lg shadow-amber-600/20 disabled:opacity-50"
            >
              {isSubmitting ? 'Pooling Escrow...' : 'Contribute Co-Guarantee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
