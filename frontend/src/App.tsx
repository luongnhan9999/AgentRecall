import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Cpu, 
  Plus, 
  RefreshCw, 
  Search, 
  Filter, 
  AlertTriangle,
  Car,
  Activity,
  CheckCircle2,
  Zap
} from 'lucide-react';
import { Navbar } from './components/Navbar';
import { StatsOverview } from './components/StatsOverview';
import { VaultCard } from './components/VaultCard';
import { RegisterVaultModal } from './components/RegisterVaultModal';
import { FileClaimModal } from './components/FileClaimModal';
import { AppealModal } from './components/AppealModal';
import { DiagnosticInspectorModal } from './components/DiagnosticInspectorModal';
import { CockpitConsole } from './components/CockpitConsole';
import { SyndicateModal } from './components/SyndicateModal';
import { LeaderboardDrawer } from './components/LeaderboardDrawer';
import { 
  DEFAULT_CONTRACT_ADDRESS, 
  genlayerClient, 
  encodeGenLayerTransaction, 
  STUDIONET_CHAIN_ID_HEX 
} from './config/genlayer';
import { WarrantyVault, ProtocolStats, OEMProfile, OEMLeaderboardEntry, SyndicatePledge } from './types/vault';
import { formatGen } from './utils/formatters';

export function App() {
  const [contractAddress, setContractAddress] = useState(DEFAULT_CONTRACT_ADDRESS);
  const [account, setAccount] = useState<string | null>(null);
  const [balance, setBalance] = useState('0.00');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Protocol state
  const [stats, setStats] = useState<ProtocolStats | null>(null);
  const [vaults, setVaults] = useState<WarrantyVault[]>([]);
  const [userProfile, setUserProfile] = useState<OEMProfile | null>(null);
  const [leaderboard, setLeaderboard] = useState<OEMLeaderboardEntry[]>([]);
  const [selectedPledges, setSelectedPledges] = useState<SyndicatePledge[]>([]);

  // Filter & Search
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals state
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [claimVault, setClaimVault] = useState<WarrantyVault | null>(null);
  const [appealVault, setAppealVault] = useState<WarrantyVault | null>(null);
  const [inspectorVault, setInspectorVault] = useState<WarrantyVault | null>(null);
  const [syndicateVault, setSyndicateVault] = useState<WarrantyVault | null>(null);
  const [isLeaderboardOpen, setIsLeaderboardOpen] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 6000);
  };

  // Connect MetaMask
  const connectWallet = async () => {
    if (!window.ethereum) {
      alert('MetaMask or EVM web3 wallet not detected. Please install an EVM wallet.');
      return;
    }
    setIsConnecting(true);
    try {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      if (accounts && accounts.length > 0) {
        setAccount(accounts[0]);
        await updateBalance(accounts[0]);
      }
    } catch (err: any) {
      console.error('Wallet connection error:', err);
    } finally {
      setIsConnecting(false);
    }
  };

  const updateBalance = async (addr: string) => {
    if (!window.ethereum) return;
    try {
      const balHex = await window.ethereum.request({
        method: 'eth_getBalance',
        params: [addr, 'latest'],
      });
      const balDec = BigInt(balHex);
      setBalance(formatGen(balDec.toString()));
    } catch (e) {
      console.error('Balance fetch failed:', e);
    }
  };

  // Fetch On-Chain State from GenLayer StudioNet
  const fetchContractState = async () => {
    setIsLoading(true);
    try {
      // 1. Fetch Stats
      const rawStats = await (genlayerClient as any).readContract({
        address: contractAddress,
        functionName: 'get_stats',
        args: [],
      });
      if (rawStats) {
        setStats(typeof rawStats === 'string' ? JSON.parse(rawStats) : rawStats);
      }

      // 2. Fetch Vaults
      const rawVaults = await (genlayerClient as any).readContract({
        address: contractAddress,
        functionName: 'get_all_vaults',
        args: [],
      });
      if (rawVaults) {
        const parsed = typeof rawVaults === 'string' ? JSON.parse(rawVaults) : rawVaults;
        setVaults(parsed.reverse()); // latest first
      }

      // 3. Fetch Leaderboard
      try {
        const rawBoard = await (genlayerClient as any).readContract({
          address: contractAddress,
          functionName: 'get_oem_leaderboard',
          args: [],
        });
        if (rawBoard) {
          setLeaderboard(typeof rawBoard === 'string' ? JSON.parse(rawBoard) : rawBoard);
        }
      } catch (err) {
        console.warn('Leaderboard fetch skipped:', err);
      }

      // 4. User OEM profile
      if (account) {
        try {
          const rawProfile = await (genlayerClient as any).readContract({
            address: contractAddress,
            functionName: 'get_reputation_profile',
            args: [account],
          });
          if (rawProfile) {
            setUserProfile(typeof rawProfile === 'string' ? JSON.parse(rawProfile) : rawProfile);
          }
        } catch (e) {
          console.warn('Profile fetch skipped:', e);
        }
      }
    } catch (error) {
      console.error('Failed to read on-chain contract:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchContractState();
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          updateBalance(accounts[0]);
        } else {
          setAccount(null);
        }
      });
    }
  }, [contractAddress, account]);

  // Execute Transaction via MetaMask + GenLayer StudioNet Consensus Bridge
  const sendContractTransaction = async (functionName: string, args: any[], valueWei: bigint = 0n) => {
    if (!account) {
      await connectWallet();
      return;
    }
    setIsProcessing(true);
    showNotification(`Broadcasting ${functionName} to GenLayer StudioNet...`, 'info');

    try {
      const { to, data } = encodeGenLayerTransaction(account, contractAddress, functionName, args);
      const txParams: any = {
        from: account,
        to,
        data,
        value: `0x${valueWei.toString(16)}`,
      };

      const txHash = await window.ethereum.request({
        method: 'eth_sendTransaction',
        params: [txParams],
      });

      showNotification(`Transaction sent! Waiting for validator consensus... (${txHash.slice(0, 10)}...)`, 'info');

      // Wait 12 seconds for consensus block inclusion
      setTimeout(async () => {
        await fetchContractState();
        if (account) updateBalance(account);
        setIsProcessing(false);
        showNotification(`${functionName} confirmed on GenLayer StudioNet!`, 'success');
      }, 12000);
    } catch (err: any) {
      console.error('Transaction failed:', err);
      setIsProcessing(false);
      showNotification(err?.message || 'Transaction rejected or failed', 'error');
      throw err;
    }
  };

  // Actions
  const handleRegisterVault = async (
    consumer: string,
    vin: string,
    firmware: string,
    blocks: number,
    escrowWei: bigint
  ) => {
    await sendContractTransaction('register_warranty_vault', [consumer, vin, firmware, blocks], escrowWei);
  };

  const handleFileClaim = async (vaultId: number, logUrl: string) => {
    await sendContractTransaction('file_lemon_claim', [vaultId, logUrl]);
  };

  const handleAdjudicateClaim = async (vault: WarrantyVault) => {
    await sendContractTransaction('adjudicate_lemon_claim', [vault.vault_id]);
  };

  const handleAppeal = async (vaultId: number, disputeReason: string, bondWei: bigint) => {
    await sendContractTransaction('appeal_verdict', [vaultId, disputeReason], bondWei);
  };

  const handleAdjudicateAppeal = async (vaultId: number, supplementalUrl: string) => {
    await sendContractTransaction('adjudicate_appeal', [vaultId, supplementalUrl]);
  };

  const handleFinalizeSettlement = async (vaultId: number) => {
    await sendContractTransaction('finalize_settlement', [vaultId]);
  };

  const handleCancelOrReclaim = async (vaultId: number) => {
    await sendContractTransaction('cancel_or_reclaim', [vaultId]);
  };

  const handleSyndicatePledge = async (vaultId: number, pledgeWei: bigint) => {
    await sendContractTransaction('pledge_warranty_escrow', [vaultId], pledgeWei);
  };

  const handleOpenInspector = async (vault: WarrantyVault) => {
    setInspectorVault(vault);
    try {
      const raw = await (genlayerClient as any).readContract({
        address: contractAddress,
        functionName: 'get_vault_pledges',
        args: [vault.vault_id],
      });
      if (raw) {
        setSelectedPledges(typeof raw === 'string' ? JSON.parse(raw) : raw);
      }
    } catch {
      setSelectedPledges([]);
    }
  };

  // Filtering
  const filteredVaults = vaults.filter((v) => {
    if (filterStatus === 'ACTIVE' && v.status !== 0) return false;
    if (filterStatus === 'CLAIMED' && v.status !== 1) return false;
    if (filterStatus === 'COOLING' && v.status !== 2) return false;
    if (filterStatus === 'REFUNDED' && v.status !== 3) return false;
    if (filterStatus === 'DISPUTED' && v.status !== 6) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        v.device_vin_or_serial.toLowerCase().includes(q) ||
        v.firmware_version.toLowerCase().includes(q) ||
        v.consumer.toLowerCase().includes(q) ||
        v.manufacturer.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const activeCount = vaults.filter((v) => v.status === 0).length;
  const criticalRecallCount = vaults.filter((v) => v.status === 3).length;

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col">
      <Navbar
        account={account}
        balance={balance}
        isConnecting={isConnecting}
        onConnect={connectWallet}
        contractAddress={contractAddress}
        onOpenLeaderboard={() => setIsLeaderboardOpen(true)}
      />

      {/* Notification Toast */}
      {notification && (
        <div className="fixed bottom-5 right-5 z-50 animate-bounce">
          <div
            className={`px-4 py-3 rounded-xl border text-xs font-mono shadow-2xl flex items-center space-x-2 ${
              notification.type === 'success'
                ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
                : notification.type === 'error'
                ? 'bg-rose-950/90 border-rose-500/50 text-rose-300'
                : 'bg-slate-900/90 border-orange-500/50 text-orange-300'
            }`}
          >
            <span>{notification.message}</span>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* Hero Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-2.5 py-1 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-mono flex items-center space-x-1.5">
                <Car className="w-3.5 h-3.5" />
                <span>Automotive DePIN & IoT Lemon Law Escrow</span>
              </span>
              <span className="text-xs font-mono text-slate-500">GenVM Subjective Diagnostic Jury</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-space text-white tracking-tight">
              Firmware & Hardware Lemon Law Escrow
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Eliminate lengthy OEM warranty avoidance. When critical firmware bugs or battery runaway occurs, AI consensus automatically liquidates warranty escrow to protect EV owners and device purchasers.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={fetchContractState}
              disabled={isLoading}
              className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl text-slate-300 hover:text-white hover:border-slate-700 transition"
              title="Refresh contract state"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-orange-400' : ''}`} />
            </button>

            <button
              onClick={() => setIsRegisterOpen(true)}
              className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl text-xs font-medium font-space shadow-lg shadow-orange-500/25 transition"
            >
              <Plus className="w-4 h-4" />
              <span>Register Warranty Vault</span>
            </button>
          </div>
        </div>

        {/* Protocol Stats */}
        <StatsOverview
          stats={stats}
          activeCount={activeCount}
          criticalRecallCount={criticalRecallCount}
        />

        {/* Live Cockpit Telemetry & CAN-Bus Console HUD */}
        {vaults.length > 0 && (
          <CockpitConsole
            vaults={vaults}
            onSelectVault={handleOpenInspector}
            onAdjudicateClaim={handleAdjudicateClaim}
            onOpenFileClaim={(v) => setClaimVault(v)}
            isProcessing={isProcessing}
          />
        )}

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6 bg-[#0A0E1A]/80 p-3 rounded-2xl border border-slate-800/80 shadow-md">
          {/* Status Tabs */}
          <div className="flex items-center space-x-1 overflow-x-auto pb-1 sm:pb-0">
            {['ALL', 'ACTIVE', 'CLAIMED', 'COOLING', 'REFUNDED', 'DISPUTED'].map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono transition whitespace-nowrap ${
                  filterStatus === st
                    ? 'bg-orange-500/15 text-orange-400 border border-orange-500/40 font-bold shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search VIN, Firmware, Address..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3.5 py-1.5 bg-[#070A14] border border-slate-800 rounded-xl text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition"
            />
          </div>
        </div>

        {/* Vaults Grid */}
        {isLoading && vaults.length === 0 ? (
          <div className="p-16 text-center space-y-3 bg-[#0A0E1A]/50 border border-slate-800/80 rounded-3xl">
            <RefreshCw className="w-8 h-8 mx-auto animate-spin text-orange-400" />
            <p className="text-sm font-mono text-slate-400">Loading live warranty vaults from GenLayer StudioNet...</p>
          </div>
        ) : filteredVaults.length === 0 ? (
          <div className="p-16 text-center space-y-3 bg-[#0A0E1A]/50 border border-slate-800/80 rounded-3xl">
            <Car className="w-8 h-8 mx-auto text-slate-600" />
            <p className="text-sm font-mono text-slate-400">No warranty vaults matching filter.</p>
            <button
              onClick={() => setIsRegisterOpen(true)}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded-xl text-xs font-medium font-space transition"
            >
              Register First Vault
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredVaults.map((vault) => (
              <VaultCard
                key={vault.vault_id}
                vault={vault}
                account={account}
                onOpenFileClaim={(v) => setClaimVault(v)}
                onOpenAdjudicate={handleAdjudicateClaim}
                onOpenAppeal={(v) => setAppealVault(v)}
                onOpenInspector={handleOpenInspector}
                onOpenSyndicate={(v) => setSyndicateVault(v)}
                onFinalizeSettlement={handleFinalizeSettlement}
                onCancelOrReclaim={handleCancelOrReclaim}
                isProcessing={isProcessing}
              />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#060911] py-6 text-center text-xs font-mono text-slate-500">
        AgentRecall Lemon Law Escrow Protocol • GenLayer StudioNet (Chain ID 61999 / Hex 0xF22F)
      </footer>

      {/* Modals */}
      <RegisterVaultModal
        isOpen={isRegisterOpen}
        onClose={() => setIsRegisterOpen(false)}
        onSubmit={handleRegisterVault}
        isSubmitting={isProcessing}
      />

      {claimVault && (
        <FileClaimModal
          isOpen={!!claimVault}
          onClose={() => setClaimVault(null)}
          vaultId={claimVault.vault_id}
          vinSerial={claimVault.device_vin_or_serial}
          onSubmit={handleFileClaim}
          isSubmitting={isProcessing}
        />
      )}

      {appealVault && (
        <AppealModal
          isOpen={!!appealVault}
          onClose={() => setAppealVault(null)}
          vaultId={appealVault.vault_id}
          vinSerial={appealVault.device_vin_or_serial}
          escrowAmount={appealVault.escrow_amount}
          isFastTrack={appealVault.is_fast_track}
          onSubmit={handleAppeal}
          isSubmitting={isProcessing}
        />
      )}

      <DiagnosticInspectorModal
        isOpen={!!inspectorVault}
        onClose={() => setInspectorVault(null)}
        vault={inspectorVault}
        pledges={selectedPledges}
        onAdjudicateAppeal={handleAdjudicateAppeal}
        isAdjudicatingAppeal={isProcessing}
      />

      {syndicateVault && (
        <SyndicateModal
          isOpen={!!syndicateVault}
          onClose={() => setSyndicateVault(null)}
          vaultId={syndicateVault.vault_id}
          vinSerial={syndicateVault.device_vin_or_serial}
          currentEscrow={syndicateVault.escrow_amount}
          onSubmit={handleSyndicatePledge}
          isSubmitting={isProcessing}
        />
      )}

      <LeaderboardDrawer
        isOpen={isLeaderboardOpen}
        onClose={() => setIsLeaderboardOpen(false)}
        leaderboard={leaderboard}
        userProfile={userProfile}
      />
    </div>
  );
}

export default App;
