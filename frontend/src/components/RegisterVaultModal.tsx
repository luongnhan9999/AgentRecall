import React, { useState } from 'react';
import { X, ShieldPlus, Cpu, AlertCircle } from 'lucide-react';
import { formatWei } from '../utils/formatters';

interface RegisterVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (consumerAddress: string, vinSerial: string, firmwareVersion: string, warrantyBlocks: number, escrowWei: bigint) => Promise<void>;
  isSubmitting: boolean;
}

export const RegisterVaultModal: React.FC<RegisterVaultModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
}) => {
  const [consumerAddress, setConsumerAddress] = useState('');
  const [vinSerial, setVinSerial] = useState('');
  const [firmwareVersion, setFirmwareVersion] = useState('');
  const [escrowGen, setEscrowGen] = useState('0.05');
  const [warrantyBlocks, setWarrantyBlocks] = useState(6000);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!consumerAddress.startsWith('0x') || consumerAddress.length !== 42) {
      setError('Please provide a valid EV driver or consumer EVM address (0x...)');
      return;
    }
    if (vinSerial.trim().length < 6) {
      setError('Vehicle VIN or device serial must be at least 6 characters.');
      return;
    }
    if (!firmwareVersion.trim()) {
      setError('Declared firmware build version identifier is required.');
      return;
    }

    const escrowWei = formatWei(escrowGen);
    if (escrowWei <= 0n) {
      setError('Escrow deposit must be greater than 0 GEN.');
      return;
    }

    try {
      await onSubmit(consumerAddress.trim(), vinSerial.trim(), firmwareVersion.trim(), warrantyBlocks, escrowWei);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Transaction submission failed');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#151C2C] border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0B0F19]/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <ShieldPlus className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-base font-bold font-space text-white">Register Hardware Warranty Escrow</h3>
              <p className="text-xs text-slate-400">OEM locks lemon law guarantee backing device/EV</p>
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

          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
              Consumer / Device Owner Address
            </label>
            <input
              type="text"
              placeholder="0x..."
              value={consumerAddress}
              onChange={(e) => setConsumerAddress(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
              required
            />
            <p className="text-[11px] text-slate-400 mt-1">Recipient of full refund or partial repairs if Lemon Law triggers.</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
                VIN / Device Serial
              </label>
              <input
                type="text"
                placeholder="e.g. VIN-EV-TESLA-99214X"
                value={vinSerial}
                onChange={(e) => setVinSerial(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
                Firmware Build
              </label>
              <input
                type="text"
                placeholder="e.g. v2026.4.12"
                value={firmwareVersion}
                onChange={(e) => setFirmwareVersion(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
                Escrow Deposit (GEN)
              </label>
              <input
                type="number"
                step="0.001"
                min="0.001"
                value={escrowGen}
                onChange={(e) => setEscrowGen(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white focus:outline-none focus:border-emerald-500 transition"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
                Coverage Duration (Blocks)
              </label>
              <input
                type="number"
                min="100"
                value={warrantyBlocks}
                onChange={(e) => setWarrantyBlocks(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white focus:outline-none focus:border-emerald-500 transition"
                required
              />
            </div>
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-xl text-xs text-slate-400 flex items-start space-x-2">
            <Cpu className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
            <p>
              Autonomous consensus will govern this vault. If firmware brick or brake failure is verified, the escrow is automatically paid out to the consumer without OEM dispute delays.
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
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-medium font-space transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              {isSubmitting ? 'Locking Escrow...' : 'Lock Warranty Escrow'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
