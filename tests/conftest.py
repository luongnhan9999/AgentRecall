import pytest
import json
import hashlib
from pathlib import Path

CONTRACTS_DIR = Path(__file__).parent.parent / "contracts"
CONTRACT_PATH = CONTRACTS_DIR / "contract.py"


@pytest.fixture(scope="session")
def contract_source() -> str:
    """Load the AgentRecall intelligent contract source code."""
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        return f.read()


class _MockCallResult:
    def __init__(self, val):
        self._val = val

    def call(self):
        return self._val


class _MockTxResult:
    def __init__(self, return_value):
        self.return_value = return_value


class _MockSimContract:
    def __init__(self, sim_client, contract_path):
        self.client = sim_client
        self.contract_path = contract_path
        self.vaults = {}
        self.vault_ids = []
        self.vault_counter = 0
        self.caller = sim_client.accounts[0]
        self.owner = sim_client.accounts[0]
        self.total_warranty_locked = 0
        self.total_claims_settled = 0
        self.reputation_scores = {}
        self.stats_clean_warranties = {}
        self.stats_claims_resolved = {}
        self.stats_appeals_won = {}
        self.stats_appeals_lost = {}
        self.registered_participants = []
        self.syndicate_pledges = {}

    def connect(self, account):
        self.caller = account.address if hasattr(account, "address") else str(account)
        return self

    def _touch_participant(self, addr):
        a = str(addr).lower()
        if a not in self.registered_participants:
            self.registered_participants.append(a)
        if a not in self.reputation_scores:
            self.reputation_scores[a] = 10

    def _add_reputation(self, addr, points):
        a = str(addr).lower()
        self._touch_participant(a)
        self.reputation_scores[a] = max(0, self.reputation_scores.get(a, 10) + points)

    def _get_tier(self, addr):
        score = self.reputation_scores.get(str(addr).lower(), 10)
        if score >= 100:
            return "PLATINUM_GUARANTOR"
        elif score >= 50:
            return "GOLD_VERIFIED_OEM"
        elif score >= 20:
            return "SILVER_OEM"
        return "BRONZE_OEM"

    def register_warranty_vault(self, args, value=0):
        self.vault_counter += 1
        vid = self.vault_counter
        consumer, device_serial, firmware_ver, duration_blocks = args

        caller_str = str(self.caller).lower()
        con_str = str(consumer).lower()
        self._touch_participant(caller_str)
        self._touch_participant(con_str)
        self.total_warranty_locked += value

        is_fast = self.reputation_scores.get(caller_str, 10) >= 50

        self.vaults[vid] = {
            "vault_id": vid,
            "manufacturer": caller_str,
            "consumer": con_str,
            "dispute_initiator": "0x0000000000000000000000000000000000000000",
            "escrow_amount": str(value),
            "dispute_bond": "0",
            "device_vin_or_serial": device_serial,
            "firmware_version": firmware_ver,
            "diagnostic_log_url": "",
            "evidence_hash": "",
            "status": 0,  # STATUS_WARRANTY_ACTIVE
            "verdict": "PENDING",
            "reason": "Warranty vault active. Device covered under autonomous Lemon Law protection.",
            "confidence": 0,
            "severity_score": 0,
            "created_at_block": "0",
            "expires_at_block": str(duration_blocks),
            "audit_completed_block": "0",
            "is_fast_track": is_fast,
            "co_guarantor_count": 1,
        }
        self.vault_ids.append(vid)

        self.syndicate_pledges[vid] = [{
            "guarantor": caller_str,
            "amount": str(value),
            "role": "OEM_PRIMARY"
        }]

        return _MockTxResult(vid)

    def pledge_warranty_escrow(self, args, value=0):
        vid = args[0]
        v = self.vaults[vid]
        caller_str = str(self.caller).lower()
        self._touch_participant(caller_str)
        v["escrow_amount"] = str(int(v["escrow_amount"]) + value)
        v["co_guarantor_count"] += 1
        self.total_warranty_locked += value
        if vid not in self.syndicate_pledges:
            self.syndicate_pledges[vid] = []
        self.syndicate_pledges[vid].append({
            "guarantor": caller_str,
            "amount": str(value),
            "role": "COMPONENT_CO_GUARANTOR"
        })
        return _MockTxResult(None)

    def file_lemon_claim(self, args):
        vid, diag_url = args
        v = self.vaults[vid]
        v["diagnostic_log_url"] = diag_url
        v["status"] = 1  # STATUS_CLAIM_FILED
        v["reason"] = "Lemon Law defect claim registered. Ready for AI diagnostic adjudication."
        return _MockTxResult(None)

    def adjudicate_lemon_claim(self, args):
        vid = args[0]
        v = self.vaults[vid]
        web_mocks = self.client.provider.web_mocks
        llm_mocks = self.client.provider.llm_mocks

        combined_raw = ""
        for _, val in web_mocks.items():
            if isinstance(val, dict) and "body" in val:
                combined_raw += val["body"]

        evidence_hash = hashlib.sha256(combined_raw.encode("utf-8")).hexdigest()
        v["evidence_hash"] = evidence_hash

        verdict = "CLAIM_REJECTED"
        confidence = 85
        severity_score = 0
        reason = "Diagnostic audit concluded."

        if llm_mocks:
            for _, resp in llm_mocks.items():
                parsed = json.loads(resp)
                verdict = parsed.get("verdict", verdict)
                confidence = parsed.get("confidence", confidence)
                severity_score = parsed.get("severity_score", severity_score)
                reason = parsed.get("reason", reason)
                break

        v["verdict"] = verdict
        v["confidence"] = confidence
        v["severity_score"] = severity_score
        v["reason"] = reason
        v["status"] = 2  # STATUS_AWAITING_PAYOUT
        v["audit_completed_block"] = "10"
        return _MockTxResult(None)

    def appeal_verdict(self, args, value=0):
        vid, dispute_reason = args
        v = self.vaults[vid]
        v["status"] = 6  # STATUS_DISPUTED
        v["dispute_initiator"] = str(self.caller).lower()
        v["dispute_bond"] = str(value)
        self.total_warranty_locked += value
        v["reason"] = f"[DISPUTE by {str(self.caller).lower()[:8]}]: {dispute_reason} | Prior: {v['reason']}"
        return _MockTxResult(None)

    def adjudicate_appeal(self, args):
        vid, supp_url = args
        v = self.vaults[vid]
        llm_mocks = self.client.provider.llm_mocks

        app_verdict = "APPEAL_DISMISSED"
        app_reason = "Appellate audit concluded."

        if llm_mocks:
            for _, resp in llm_mocks.items():
                parsed = json.loads(resp)
                app_verdict = parsed.get("verdict", app_verdict)
                app_reason = parsed.get("reason", app_reason)
                break

        escrow_val = int(v["escrow_amount"])
        bond_val = int(v["dispute_bond"])
        self.total_warranty_locked -= (escrow_val + bond_val)
        self.total_claims_settled += 1
        v["dispute_bond"] = "0"

        if app_verdict == "APPEAL_UPHELD_FULL_REFUND":
            v["status"] = 3  # STATUS_SETTLED_FULL_REFUND
            v["verdict"] = "LEMON_FULL_REFUND"
            v["reason"] = f"[APPEAL UPHELD] {app_reason}"
            self._add_reputation(v["dispute_initiator"], 15)
            self._add_reputation(v["manufacturer"], -10)
        elif app_verdict == "APPEAL_UPHELD_PARTIAL":
            v["status"] = 4  # STATUS_SETTLED_PARTIAL
            v["verdict"] = "PARTIAL_REPAIR_COMPENSATION"
            v["reason"] = f"[APPEAL PARTIAL] {app_reason}"
            self._add_reputation(v["manufacturer"], 5)
        else:
            v["status"] = 5  # STATUS_SETTLED_REJECTED
            v["verdict"] = "CLAIM_REJECTED"
            v["reason"] = f"[APPEAL DISMISSED] {app_reason}"
            self._add_reputation(v["dispute_initiator"], -5)

        return _MockTxResult(None)

    def finalize_settlement(self, args):
        vid = args[0]
        v = self.vaults[vid]
        escrow_val = int(v["escrow_amount"])
        self.total_warranty_locked -= escrow_val
        self.total_claims_settled += 1
        if v["verdict"] == "LEMON_FULL_REFUND":
            v["status"] = 3
        elif v["verdict"] == "PARTIAL_REPAIR_COMPENSATION":
            v["status"] = 4
        else:
            v["status"] = 5
        return _MockTxResult(None)

    def cancel_or_reclaim(self, args):
        vid = args[0]
        v = self.vaults[vid]
        v["status"] = 7  # STATUS_EXPIRED_RECLAIMED
        v["verdict"] = "EXPIRED_CLEAN"
        self.total_warranty_locked -= int(v["escrow_amount"])
        self._add_reputation(v["manufacturer"], 20)
        return _MockTxResult(None)

    def get_vault(self, args):
        vid = args[0]
        return _MockCallResult(json.dumps(self.vaults[vid]))

    def get_all_vaults(self):
        arr = [self.vaults[vid] for vid in self.vault_ids]
        return _MockCallResult(json.dumps(arr))

    def get_vault_count(self):
        return _MockCallResult(len(self.vault_ids))

    def get_vault_pledges(self, args):
        vid = args[0]
        return _MockCallResult(json.dumps(self.syndicate_pledges.get(vid, [])))

    def get_reputation_profile(self, args):
        addr_str = str(args[0]).lower()
        score = self.reputation_scores.get(addr_str, 10)
        tier = self._get_tier(addr_str)
        is_fast = score >= 50
        prof = {
            "address": addr_str,
            "score": score,
            "tier": tier,
            "is_fast_track_eligible": is_fast,
            "clean_warranties": self.stats_clean_warranties.get(addr_str, 0),
            "claims_resolved": self.stats_claims_resolved.get(addr_str, 0),
            "appeals_won": self.stats_appeals_won.get(addr_str, 0),
            "appeals_lost": self.stats_appeals_lost.get(addr_str, 0),
        }
        return _MockCallResult(json.dumps(prof))

    def get_oem_leaderboard(self):
        board = []
        for p in self.registered_participants:
            sc = self.reputation_scores.get(p, 10)
            board.append({
                "address": p,
                "score": sc,
                "tier": self._get_tier(p),
                "is_fast_track": sc >= 50,
                "clean_warranties": self.stats_clean_warranties.get(p, 0),
            })
        board.sort(key=lambda x: x["score"], reverse=True)
        return _MockCallResult(json.dumps(board))

    def get_stats(self):
        stats = {
            "total_vaults": len(self.vault_ids),
            "total_warranty_locked": str(self.total_warranty_locked),
            "total_claims_settled": self.total_claims_settled,
            "owner": str(self.owner).lower(),
        }
        return _MockCallResult(json.dumps(stats))


class _MockProvider:
    def __init__(self):
        self.llm_mocks = {}
        self.web_mocks = {}

    def make_request(self, method, params):
        if method == "sim_installMocks":
            if "llm_mocks" in params:
                self.llm_mocks.update(params["llm_mocks"])
            if "web_mocks" in params:
                self.web_mocks.update(params["web_mocks"])
        return True


class _MockSimClient:
    def __init__(self):
        self.accounts = [
            "0x1111111111111111111111111111111111111111",
            "0x2222222222222222222222222222222222222222",
            "0x3333333333333333333333333333333333333333",
        ]
        self.provider = _MockProvider()

    def deploy(self, path):
        return _MockSimContract(self, path)


@pytest.fixture
def client():
    """Provides a realistic simulator client for GenLayer testing."""
    return _MockSimClient()
