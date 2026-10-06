import React, { useState } from 'react';
import { X, FileText, UploadCloud, AlertCircle } from 'lucide-react';

interface FileClaimModalProps {
  isOpen: boolean;
  onClose: () => void;
  vaultId: number;
  vinSerial: string;
  onSubmit: (vaultId: number, logUrl: string) => Promise<void>;
  isSubmitting: boolean;
}

export const FileClaimModal: React.FC<FileClaimModalProps> = ({
  isOpen,
  onClose,
  vaultId,
  vinSerial,
  onSubmit,
  isSubmitting,
}) => {
  const [logUrl, setLogUrl] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const clean = logUrl.trim();
    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      setError('Please provide a valid public telemetry log URL (http:// or https://)');
      return;
    }

    try {
      await onSubmit(vaultId, clean);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to file Lemon Law claim');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#151C2C] border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0B0F19]/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-orange-500/10 border border-orange-500/20 rounded-xl">
              <UploadCloud className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <h3 className="text-base font-bold font-space text-white">File Lemon Law Claim</h3>
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

          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1.5">
              OBD-II / CAN-Bus / Telemetry URL
            </label>
            <input
              type="url"
              placeholder="https://telemetry-archive.org/ev_logs/vin99214x_brake_failure.json"
              value={logUrl}
              onChange={(e) => setLogUrl(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition"
              required
            />
            <p className="text-[11px] text-slate-400 mt-1">
              URL must be public for GenLayer validators to scrape via gl.nondet.web.render.
            </p>
          </div>

          {/* Quick presets for test demo */}
          <div className="space-y-1.5">
            <label className="block text-xs font-mono uppercase text-slate-500">Preset Diagnostic Telemetry</label>
            <div className="flex flex-col gap-1.5">
              <button
                type="button"
                onClick={() => setLogUrl('https://telemetry-archive.org/ev_logs/vin99214x_brake_failure.json')}
                className="text-left px-2.5 py-1.5 bg-slate-900/60 border border-slate-800/80 rounded-lg text-xs font-mono text-slate-300 hover:text-white hover:border-orange-500/40 transition"
              >
                🚨 Critical Regenerative Brake & BMS Failure (Severity 92)
              </button>
              <button
                type="button"
                onClick={() => setLogUrl('https://telemetry-archive.org/ev_logs/vin8812a_infotainment.json')}
                className="text-left px-2.5 py-1.5 bg-slate-900/60 border border-slate-800/80 rounded-lg text-xs font-mono text-slate-300 hover:text-white hover:border-orange-500/40 transition"
              >
                ⚠️ Moderate Infotainment / ECU Lag (Severity 55)
              </button>
            </div>
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
              className="px-5 py-2.5 bg-orange-600 hover:bg-orange-500 text-white rounded-xl text-xs font-medium font-space transition shadow-lg shadow-orange-600/20 disabled:opacity-50"
            >
              {isSubmitting ? 'Registering Claim...' : 'Submit Diagnostic Proof'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
