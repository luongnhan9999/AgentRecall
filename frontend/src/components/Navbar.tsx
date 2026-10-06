import React from 'react';
import { ShieldCheck, Cpu, Wallet, ExternalLink, Zap, Activity, Radio, AlertOctagon } from 'lucide-react';
import { shortenAddress } from '../utils/formatters';
import { STUDIONET_CHAIN_CONFIG, STUDIONET_CHAIN_ID_HEX } from '../config/genlayer';

interface NavbarProps {
  account: string | null;
  balance: string;
  isConnecting: boolean;
  onConnect: () => void;
  contractAddress: string;
  onOpenLeaderboard: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  account,
  balance,
  isConnecting,
  onConnect,
  contractAddress,
  onOpenLeaderboard,
}) => {
  const switchOrAddNetwork = async () => {
    if (!window.ethereum) return;
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: STUDIONET_CHAIN_ID_HEX }],
      });
    } catch (switchError: any) {
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [STUDIONET_CHAIN_CONFIG],
          });
        } catch (addError) {
          console.error('Error adding network:', addError);
        }
      }
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-[#070B14]/90 backdrop-blur-xl border-b border-orange-500/20 shadow-2xl shadow-black/60">
      {/* Top micro-ticker line */}
      <div className="bg-[#05080E] border-b border-slate-800/60 px-4 py-1 text-[10px] font-mono text-slate-400 flex items-center justify-between">
        <div className="flex items-center space-x-3 overflow-x-auto">
          <span className="flex items-center space-x-1 text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span>GENLAYER STUDIONET 61999</span>
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-300">CALIFORNIA LEMON LAW § 1793.22 AUTOMATED</span>
          <span className="text-slate-600 hidden md:inline">|</span>
          <span className="text-orange-400 hidden md:inline">ORACLE: gl.nondet.web.render ACTIVE</span>
        </div>
        <div className="hidden sm:flex items-center space-x-2 text-[10px] text-slate-500">
          <span>LATENCY: 42ms</span>
          <span>•</span>
          <span>BLOCK TARGET: 3.2s</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-4">
          <div className="relative h-12 w-12 rounded-2xl bg-gradient-to-tr from-orange-600 via-amber-500 to-emerald-400 p-0.5 shadow-xl shadow-orange-500/20 group cursor-pointer">
            <div className="h-full w-full bg-[#070B14] rounded-[14px] flex items-center justify-center group-hover:bg-[#0C1222] transition">
              <Cpu className="h-6 w-6 text-orange-400 group-hover:scale-110 transition duration-300" />
            </div>
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#070B14] animate-pulse"></span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl sm:text-2xl font-bold font-space tracking-tight text-white flex items-center">
                Agent<span className="text-orange-400">Recall</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/30 font-mono">
                v3.0 Cockpit
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono hidden sm:block">
              Autonomous IoT &amp; EV Firmware Lemon Law Escrow
            </p>
          </div>
        </div>

        {/* Actions & Wallet */}
        <div className="flex items-center space-x-3">
          {/* Contract Link */}
          <a
            href={`https://studio.genlayer.com/address/${contractAddress}`}
            target="_blank"
            rel="noreferrer"
            className="hidden lg:flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-orange-500/40 transition"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-mono">{shortenAddress(contractAddress, 4)}</span>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </a>

          {/* Leaderboard Button */}
          <button
            onClick={onOpenLeaderboard}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#0F1626] border border-orange-500/20 text-xs font-mono text-orange-300 hover:bg-orange-500/10 hover:border-orange-500/50 transition shadow-sm"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="font-semibold">OEM RELIABILITY</span>
          </button>

          {/* Connect / Network Button */}
          {account ? (
            <div className="flex items-center space-x-2 bg-[#0C1222] border border-slate-800/80 rounded-2xl p-1.5 shadow-inner">
              <button
                onClick={switchOrAddNetwork}
                title="Switch network"
                className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-orange-500/10 text-orange-400 border border-orange-500/30 text-xs font-mono hover:bg-orange-500/20 transition"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-ping"></span>
                <span>CHAIN 61999</span>
              </button>
              <div className="px-2.5 py-1 text-xs font-mono text-emerald-400 font-bold">
                {balance} GEN
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-xl text-xs font-mono text-white border border-slate-700">
                <Wallet className="w-3.5 h-3.5 text-orange-400" />
                <span>{shortenAddress(account, 3)}</span>
              </div>
            </div>
          ) : (
            <button
              onClick={onConnect}
              disabled={isConnecting}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-orange-500 via-amber-500 to-orange-600 hover:from-orange-600 hover:to-amber-600 text-white text-xs font-bold font-mono tracking-wider shadow-lg shadow-orange-500/30 transition disabled:opacity-50"
            >
              <Wallet className="w-4 h-4" />
              <span>{isConnecting ? 'CONNECTING...' : 'CONNECT COCKPIT'}</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

