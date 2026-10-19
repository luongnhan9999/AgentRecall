export interface WarrantyVault {
  vault_id: number;
  manufacturer: string;
  consumer: string;
  dispute_initiator: string;
  escrow_amount: string;
  dispute_bond: string;
  device_vin_or_serial: string;
  firmware_version: string;
  diagnostic_log_url: string;
  evidence_hash: string;
  status: number;
  verdict: string;
  reason: string;
  confidence: number;
  severity_score: number;
  created_at_block: string;
  expires_at_block: string;
  audit_completed_block: string;
  is_fast_track: boolean;
  co_guarantor_count: number;
  fleet_circuit_breaker_active?: boolean;
  firmware_fault_count?: number;
}

export interface FirmwareSafetyReport {
  firmware_version: string;
  critical_fault_count: number;
  circuit_breaker_active: boolean;
  recall_timestamp: string;
  safety_status: string;
  threshold: number;
}

export interface SyndicatePledge {
  guarantor: string;
  amount: string;
  role: string;
}

export interface OEMProfile {
  address: string;
  score: number;
  tier: string;
  is_fast_track_eligible: boolean;
  clean_warranties: number;
  claims_resolved: number;
  appeals_won: number;
  appeals_lost: number;
}

export interface OEMLeaderboardEntry {
  address: string;
  score: number;
  tier: string;
  is_fast_track: boolean;
  clean_warranties: number;
}

export interface ProtocolStats {
  total_vaults: number;
  total_warranty_locked: string;
  total_claims_settled: number;
  owner: string;
}
