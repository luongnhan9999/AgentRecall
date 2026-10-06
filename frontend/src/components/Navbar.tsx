import React from 'react';
import { ShieldCheck, Cpu, Wallet, ExternalLink, Zap } from 'lucide-react';
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
    <header className="sticky top-0 z-40 bg-[#0B0F19]/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-4">
          <div className="h-11 w-11 rounded-xl bg-gradient-to-tr from-orange-600 via-amber-500 to-emerald-400 p-0.5 shadow-lg shadow-orange-500/20">
            <div className="h-full w-full bg-[#0B0F19] rounded-[10px] flex items-center justify-center">
              <Cpu className="h-6 w-6 text-orange-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold font-space tracking-tight text-white">AgentRecall</span>
              <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wider rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20 font-mono">
                v3.0 StudioNet
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono hidden sm:block">
              Autonomous IoT & EV Firmware Lemon Law Escrow
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
            className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-slate-700 transition"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-mono">{shortenAddress(contractAddress, 4)}</span>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </a>

          {/* Leaderboard Button */}
          <button
            onClick={onOpenLeaderboard}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-200 hover:bg-slate-800 hover:border-slate-700 transition"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>OEM Reliability</span>
          </button>

          {/* Connect / Network Button */}
          {account ? (
            <div className="flex items-center space-x-2 bg-slate-900/90 border border-slate-800 rounded-xl p-1.5">
              <button
                onClick={switchOrAddNetwork}
                title="Switch network"
                className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-orange-500/10 text-orange-400 border border-orange-500/20 text-xs font-mono"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse"></span>
                <span>61999</span>
              </button>
              <div className="px-2.5 py-1 text-xs font-mono text-emerald-400 font-medium">
                {balance} GEN
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-lg text-xs font-mono text-white">
                <Wallet className="w-3.5 h-3.5 text-slate-400" />
                <span>{shortenAddress(account, 3)}</span>
              </div>
            </div>
          ) : (
            <button
              onClick={onConnect}
              disabled={isConnecting}
              className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white text-xs font-medium font-space shadow-lg shadow-orange-500/25 transition disabled:opacity-50"
            >
              <Wallet className="w-4 h-4" />
              <span>{isConnecting ? 'Connecting...' : 'Connect Wallet'}</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
