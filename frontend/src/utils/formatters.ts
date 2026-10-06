export function shortenAddress(address: string, chars: number = 4): string {
  if (!address) return '';
  return `${address.substring(0, chars + 2)}...${address.substring(address.length - chars)}`;
}

export function formatGen(weiValue: string | number | bigint): string {
  try {
    const valBig = BigInt(weiValue.toString());
    const whole = valBig / 10n ** 18n;
    const remainder = valBig % 10n ** 18n;
    const decimal = remainder.toString().padStart(18, '0').slice(0, 4);
    return `${whole}.${decimal}`;
  } catch {
    return '0.0000';
  }
}

export function formatWei(genAmount: string | number): bigint {
  try {
    const parts = genAmount.toString().split('.');
    const whole = BigInt(parts[0] || '0') * 10n ** 18n;
    let fraction = 0n;
    if (parts[1]) {
      const fracStr = parts[1].slice(0, 18).padEnd(18, '0');
      fraction = BigInt(fracStr);
    }
    return whole + fraction;
  } catch {
    return 0n;
  }
}

export function getStatusBadge(status: number) {
  switch (status) {
    case 0:
      return {
        label: 'COVERAGE ACTIVE',
        color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        dot: 'bg-emerald-400',
      };
    case 1:
      return {
        label: 'CLAIM FILED',
        color: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
        dot: 'bg-orange-400 animate-pulse',
      };
    case 2:
      return {
        label: 'AWAITING PAYOUT',
        color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        dot: 'bg-amber-400 animate-pulse',
      };
    case 3:
      return {
        label: 'FULL LEMON REFUND',
        color: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        dot: 'bg-rose-400',
      };
    case 4:
      return {
        label: 'PARTIAL COMPENSATION',
        color: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        dot: 'bg-blue-400',
      };
    case 5:
      return {
        label: 'CLAIM REJECTED',
        color: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
        dot: 'bg-slate-400',
      };
    case 6:
      return {
        label: 'IN DISPUTE / APPEAL',
        color: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
        dot: 'bg-purple-400 animate-ping',
      };
    case 7:
      return {
        label: 'EXPIRED / RECLAIMED',
        color: 'bg-slate-600/10 text-slate-400 border-slate-600/30',
        dot: 'bg-slate-500',
      };
    default:
      return {
        label: 'UNKNOWN',
        color: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
        dot: 'bg-slate-400',
      };
  }
}

export function getSeverityStyle(score: number) {
  if (score >= 80) {
    return {
      label: 'CRITICAL HAZARD',
      badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      bar: 'bg-rose-500',
    };
  } else if (score >= 40) {
    return {
      label: 'MODERATE DEFECT',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      bar: 'bg-amber-500',
    };
  }
  return {
    label: 'BENIGN / NORMAL',
    badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    bar: 'bg-emerald-500',
  };
}

export function getTierBadge(tier: string) {
  switch (tier) {
    case 'PLATINUM_GUARANTOR':
      return {
        label: 'Platinum Guarantor',
        color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      };
    case 'GOLD_VERIFIED_OEM':
      return {
        label: 'Gold Verified OEM',
        color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      };
    case 'SILVER_OEM':
      return {
        label: 'Silver OEM',
        color: 'bg-slate-400/10 text-slate-300 border-slate-400/30',
      };
    default:
      return {
        label: 'Bronze OEM',
        color: 'bg-orange-700/10 text-orange-400 border-orange-700/30',
      };
  }
}
