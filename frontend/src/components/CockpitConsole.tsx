import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Cpu, 
  Radio, 
  Terminal, 
  BatteryCharging, 
  Zap, 
  AlertOctagon, 
  ShieldCheck, 
  CheckCircle2, 
  Crosshair,
  Gauge,
  Layers,
  Sparkles
} from 'lucide-react';
import { WarrantyVault } from '../types/vault';
import { formatGen, shortenAddress } from '../utils/formatters';

interface CockpitConsoleProps {
  vaults: WarrantyVault[];
  onSelectVault: (vault: WarrantyVault) => void;
  onAdjudicateClaim: (vault: WarrantyVault) => void;
  onOpenFileClaim: (vault: WarrantyVault) => void;
  isProcessing: boolean;
}

export const CockpitConsole: React.FC<CockpitConsoleProps> = ({
  vaults,
  onSelectVault,
  onAdjudicateClaim,
  onOpenFileClaim,
  isProcessing,
}) => {
  const [selectedVaultIndex, setSelectedVaultIndex] = useState<number>(0);
  const [telemetryTick, setTelemetryTick] = useState<number>(0);
  const [simulatedLogs, setSimulatedLogs] = useState<string[]>([
    '[OBD-II CAN0] CAN-ID: 0x18DAF110 DLC:8 DATA: 03 22 D1 00 00 00 00 00',
    '[BMS_CELL_DELTA] Max cell: 4.192V | Min cell: 3.410V | Delta: 782mV [CRITICAL_IMBALANCE]',
    '[FIRMWARE_INTEGRITY] SHA256: e8b9f1... match GenLayer attested build',
    '[GENVM_AI_ORACLE] Consensus weights: 5/5 agreement on Lemon Law Code § 1793.22(e)(1)'
  ]);

  // Periodic telemetry fluctuation
  useEffect(() => {
    const timer = setInterval(() => {
      setTelemetryTick((prev) => (prev + 1) % 100);
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  const currentVault = vaults[selectedVaultIndex] || vaults[0];

  return (
    <div className="relative mb-8 rounded-3xl bg-[#090D18] border border-orange-500/20 overflow-hidden shadow-2xl shadow-orange-950/20">
      {/* Top Cockpit Header Bar */}
      <div className="px-5 py-3.5 bg-[#0C1222] border-b border-orange-500/20 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-orange-500/10 border border-orange-500/30">
            <Radio className="w-4 h-4 text-orange-400 animate-pulse" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full animate-ping"></span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold tracking-wider text-orange-400 uppercase">
                COCKPIT TELEMETRY &amp; CAN-BUS JURY RADAR
              </span>
              <span className="px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-300 font-mono text-[10px]">
                LIVE LINK
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">
              Autonomous Diagnostic Consensus for EV Powertrain &amp; IoT Firmware
            </p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center space-x-1.5 text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>GenVM StudioNet: OK</span>
          </div>
          <div className="hidden sm:flex items-center space-x-1.5 text-slate-400">
            <span className="w-2 h-2 rounded-full bg-orange-400 animate-ping"></span>
            <span>Baud: 500 kbps (CAN-2.0B)</span>
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-orange-400 font-bold">
            {vaults.length} Units Monitored
          </div>
        </div>
      </div>

      {/* Main Cockpit Content Grid */}
      <div className="p-5 grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Device / Vehicle Selector & ECU Diagnostics (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase text-slate-400 flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5 text-orange-400" />
              <span>Registered Firmware Vaults</span>
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              Select unit to inspect
            </span>
          </div>

          {/* Quick Vault Carousel / Pills */}
          <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1">
            {vaults.map((v, idx) => {
              const isSelected = selectedVaultIndex === idx;
              const isCritical = v.status === 3 || v.severity_score >= 80;
              const isClaimed = v.status === 1;

              return (
                <button
                  key={v.vault_id}
                  onClick={() => {
                    setSelectedVaultIndex(idx);
                    onSelectVault(v);
                  }}
                  className={`w-full text-left p-3 rounded-2xl border transition-all flex items-center justify-between ${
                    isSelected
                      ? 'bg-orange-500/10 border-orange-500/60 shadow-lg shadow-orange-500/10'
                      : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center font-mono text-xs font-bold ${
                        isSelected
                          ? 'bg-orange-500 text-black shadow-md shadow-orange-500/30'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      #{v.vault_id}
                    </div>
                    <div className="truncate max-w-[170px] sm:max-w-[210px]">
                      <div className="text-xs font-bold font-mono text-white truncate">
                        {v.device_vin_or_serial}
                      </div>
                      <div className="text-[10px] font-mono text-slate-400 flex items-center space-x-1.5">
                        <span>FW {v.firmware_version}</span>
                        <span>•</span>
                        <span className="text-emerald-400 font-semibold">{formatGen(v.escrow_amount)} GEN</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end">
                    <span
                      className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                        v.status === 0
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : v.status === 1
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse'
                          : v.status === 3
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          : 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                      }`}
                    >
                      {v.status === 0
                        ? 'COVERED'
                        : v.status === 1
                        ? 'CLAIM FILED'
                        : v.status === 3
                        ? '100% LEMON'
                        : 'RESOLVED'}
                    </span>
                    {v.severity_score > 0 && (
                      <span className="text-[10px] font-mono text-rose-400 font-bold mt-1">
                        Sev: {v.severity_score}%
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Quick Action Button for current vault */}
          {currentVault && (
            <div className="pt-2 flex items-center gap-2">
              {currentVault.status === 1 ? (
                <button
                  onClick={() => onAdjudicateClaim(currentVault)}
                  disabled={isProcessing}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-mono text-xs font-bold tracking-wider shadow-lg shadow-orange-500/25 flex items-center justify-center space-x-2 transition disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>DISPATCH AI JURY CONSENSUS</span>
                </button>
              ) : currentVault.status === 0 ? (
                <button
                  onClick={() => onOpenFileClaim(currentVault)}
                  disabled={isProcessing}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-rose-600/90 hover:bg-rose-500 text-white font-mono text-xs font-bold tracking-wider shadow-lg shadow-rose-600/20 flex items-center justify-center space-x-2 transition disabled:opacity-50"
                >
                  <AlertOctagon className="w-4 h-4" />
                  <span>REPORT CRITICAL FIRMWARE BUG</span>
                </button>
              ) : (
                <button
                  onClick={() => onSelectVault(currentVault)}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs font-bold tracking-wider flex items-center justify-center space-x-2 transition"
                >
                  <Terminal className="w-4 h-4 text-orange-400" />
                  <span>INSPECT TELEMETRY BLACKBOX</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Right: Telemetry Oscilloscope & Battery Health HUD (7 cols) */}
        <div className="lg:col-span-7 bg-[#060A14] border border-slate-800 rounded-2xl p-4 flex flex-col justify-between">
          <div>
            {/* Header / Subsystem Telemetry */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
              <div className="flex items-center space-x-2">
                <Gauge className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
                  ECU Diagnostics &amp; Cell Oscilloscope
                </span>
              </div>
              <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400">
                <span>Sampling: 100Hz</span>
                <span className="text-orange-400">|</span>
                <span>ISO-14229 UDS</span>
              </div>
            </div>

            {/* Oscilloscope Grid / Simulated Waveforms */}
            <div className="relative h-28 bg-[#03060E] rounded-xl border border-emerald-500/20 p-2 overflow-hidden mb-3">
              {/* Scanline effect */}
              <div className="absolute inset-0 scanline-overlay pointer-events-none opacity-40"></div>
              
              {/* Vertical sweep line */}
              <div className="absolute top-0 bottom-0 w-0.5 bg-gradient-to-b from-orange-400 via-amber-300 to-transparent animate-scan-vertical pointer-events-none"></div>

              {/* Real-time Oscilloscope bars simulation */}
              <div className="h-full flex items-end justify-between gap-1 px-1 relative z-10">
                {Array.from({ length: 24 }).map((_, i) => {
                  // Generate dynamic cell voltage heights
                  const isFaultCell = (i === 7 || i === 18) && (currentVault?.severity_score || 0) > 40;
                  const baseHeight = 45 + Math.sin((i + telemetryTick) * 0.5) * 20;
                  const height = isFaultCell ? Math.max(15, baseHeight - 35) : Math.min(95, baseHeight + 10);

                  return (
                    <div key={i} className="flex-1 flex flex-col items-center h-full justify-end group">
                      <div
                        className={`w-full rounded-t-sm transition-all duration-300 ${
                          isFaultCell
                            ? 'bg-rose-500 shadow-md shadow-rose-500/50'
                            : height > 70
                            ? 'bg-emerald-400'
                            : 'bg-amber-400'
                        }`}
                        style={{ height: `${height}%` }}
                      ></div>
                    </div>
                  );
                })}
              </div>

              <div className="absolute top-2 left-2 text-[10px] font-mono text-emerald-400/80 bg-[#060A14]/90 px-1.5 py-0.5 rounded border border-emerald-500/20">
                Pack Delta: {currentVault?.severity_score && currentVault.severity_score > 50 ? '782mV [FAIL]' : '14mV [PASS]'}
              </div>
              <div className="absolute top-2 right-2 text-[10px] font-mono text-orange-400/80 bg-[#060A14]/90 px-1.5 py-0.5 rounded border border-orange-500/20">
                Firmware: {currentVault?.firmware_version || '2026.4.12'}
              </div>
            </div>

            {/* Diagnostic Trouble Codes (DTC) Readout */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono mb-3">
              <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] text-slate-500 block">DTC CODE</span>
                <span className={`font-bold ${currentVault?.severity_score && currentVault.severity_score > 50 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {currentVault?.severity_score && currentVault.severity_score > 50 ? 'P0A1F / U0129' : 'NO_FAULT'}
                </span>
              </div>
              <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] text-slate-500 block">BATTERY SOH</span>
                <span className="font-bold text-white">
                  {currentVault?.severity_score && currentVault.severity_score > 50 ? '64.2% [RECALL]' : '98.6% [HEALTHY]'}
                </span>
              </div>
              <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 col-span-2 sm:col-span-1">
                <span className="text-[10px] text-slate-500 block">ESCROW BACKING</span>
                <span className="font-bold text-emerald-400">
                  {formatGen(currentVault?.escrow_amount || '0')} GEN
                </span>
              </div>
            </div>
          </div>

          {/* Live Terminal Stream */}
          <div className="p-2.5 rounded-xl bg-black/90 border border-slate-800/90 font-mono text-[11px] text-slate-300 space-y-1">
            <div className="flex items-center justify-between text-[10px] text-slate-500 pb-1 border-b border-slate-800/50">
              <span className="flex items-center space-x-1">
                <Terminal className="w-3 h-3 text-orange-400" />
                <span>GENVM DIAGNOSTIC STREAM</span>
              </span>
              <span className="text-emerald-400 animate-pulse">● STREAMING</span>
            </div>
            <div className="text-slate-400 truncate">
              {simulatedLogs[(telemetryTick % simulatedLogs.length)]}
            </div>
            <div className="text-orange-400/90 truncate font-semibold">
              &gt; VIN {currentVault?.device_vin_or_serial || 'Tesla Model S Plaid'} | Consensus Verdict: {currentVault?.verdict || 'PENDING'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
