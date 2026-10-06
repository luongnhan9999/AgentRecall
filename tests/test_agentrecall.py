import pytest
import json
import hashlib
from pathlib import Path

try:
    from genlayer import *
except ImportError:
    pass


def test_contract_syntax_and_structure(contract_source):
    """Verify that contract file adheres to GenVM python specifications."""
    assert contract_source.startswith('# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }')
    assert "class WarrantyVault:" in contract_source
    assert "class Contract(gl.Contract):" in contract_source
    assert "def register_warranty_vault(" in contract_source
    assert "def pledge_warranty_escrow(" in contract_source
    assert "def file_lemon_claim(" in contract_source
    assert "def adjudicate_lemon_claim(" in contract_source
    assert "def appeal_verdict(" in contract_source
    assert "def adjudicate_appeal(" in contract_source
    assert "def finalize_settlement(" in contract_source
    assert "def cancel_or_reclaim(" in contract_source
    assert "def get_vault(" in contract_source
    assert "def get_reputation_profile(" in contract_source
    assert "def get_oem_leaderboard(" in contract_source


def test_vault_struct_attributes(contract_source):
    """Ensure WarrantyVault struct defines all state fields including telemetry, canary, and trust attributes."""
    expected_fields = [
        "vault_id: u64",
        "manufacturer: Address",
        "consumer: Address",
        "escrow_amount: bigint",
        "dispute_bond: bigint",
        "device_vin_or_serial: str",
        "firmware_version: str",
        "diagnostic_log_url: str",
        "evidence_hash: str",
        "verdict: str",
        "reason: str",
        "is_fast_track: bool",
        "co_guarantor_count: u32",
    ]
    for field in expected_fields:
        assert field in contract_source, f"Missing field in WarrantyVault: {field}"


def test_agentrecall_critical_flaw_full_refund(client):
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]

    # Step 1: OEM deposits warranty escrow
    tx_create = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-TESLA-99214X", "v2026.4.12", 6000],
        value=1000000000000000000  # 1 GEN
    )
    vault_id = tx_create.return_value

    # Step 2: Consumer files claim with CAN-bus crash log
    contract.connect(consumer).file_lemon_claim(
        args=[vault_id, "https://telemetry-archive.org/ev_logs/vin99214x_brake_failure.json"]
    )

    # Step 3: Mock AI Diagnostic Court -> Critical regenerative brake DTC (Severity 92)
    client.provider.make_request(
        method="sim_installMocks",
        params={
            "llm_mocks": {
                ".*": json.dumps({
                    "canary": "CANARY_AGENT_RECALL_LEMON_V1",
                    "verdict": "LEMON_FULL_REFUND",
                    "confidence": 98,
                    "severity_score": 92,
                    "reason": "Critical DTC U0129 & BMS cell thermal runaway failure verified. Lemon Law applies."
                })
            },
            "web_mocks": {
                ".*": {"status": 200, "body": "DTC:U0129 STATUS:CRITICAL BMS_CELL_DELTA:1.8V BRAKE_REGEN:FAILED"}
            }
        }
    )

    contract.connect(consumer).adjudicate_lemon_claim(args=[vault_id])

    v_data = json.loads(contract.get_vault(args=[vault_id]).call())
    assert v_data["status"] == 2  # AWAITING_PAYOUT
    assert v_data["verdict"] == "LEMON_FULL_REFUND"
    assert v_data["severity_score"] == 92
    assert len(v_data["evidence_hash"]) == 64


def test_agentrecall_appeal_partial_degraded_bond_accounting(client):
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]

    tx_create = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-LUCID-8812A", "v2026.1.0", 6000],
        value=1000000000000000000
    )
    vault_id = tx_create.return_value

    contract.connect(consumer).file_lemon_claim(
        args=[vault_id, "https://telemetry-archive.org/ev_logs/vin8812a_infotainment.json"]
    )

    # Initial verdict is CLAIM_REJECTED (flaw assumed benign)
    client.provider.make_request(
        method="sim_installMocks",
        params={
            "llm_mocks": {
                ".*": json.dumps({
                    "canary": "CANARY_AGENT_RECALL_LEMON_V1",
                    "verdict": "CLAIM_REJECTED",
                    "confidence": 90,
                    "severity_score": 20,
                    "reason": "Infotainment UI lag is non-critical software cosmetic issue."
                })
            },
            "web_mocks": {".*": {"status": 200, "body": "UI_FPS:18 LATENCY:400ms"}}
        }
    )
    contract.connect(consumer).adjudicate_lemon_claim(args=[vault_id])

    # Consumer appeals with 10% bond demanding full refund
    contract.connect(consumer).appeal_verdict(
        args=[vault_id, "Evidence that UI lag crashes reversing camera during reverse."],
        value=100000000000000000  # 0.1 GEN
    )

    # Appellate Board rules PARTIAL (camera defect repairable, not full vehicle buyback)
    client.provider.make_request(
        method="sim_installMocks",
        params={
            "llm_mocks": {
                ".*": json.dumps({
                    "canary": "CANARY_AGENT_RECALL_LEMON_V1",
                    "verdict": "APPEAL_UPHELD_PARTIAL",
                    "reason": "Reverse camera lag verified; partial ECU replacement compensation granted."
                })
            },
            "web_mocks": {".*": {"status": 200, "body": "CAMERA_DELAY:3200ms"}}
        }
    )
    contract.connect(consumer).adjudicate_appeal(
        args=[vault_id, "https://independent-lab.org/vin8812a_camera_test.txt"]
    )

    v_final = json.loads(contract.get_vault(args=[vault_id]).call())
    assert v_final["status"] == 4  # SETTLED_PARTIAL
    assert v_final["verdict"] == "PARTIAL_REPAIR_COMPENSATION"


def test_agentrecall_appeal_dismissed_bond_slashed(client):
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]

    tx_create = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-RIVIAN-4401C", "v2026.3.0", 6000],
        value=1000000000000000000
    )
    vault_id = tx_create.return_value

    contract.connect(consumer).file_lemon_claim(
        args=[vault_id, "https://telemetry-archive.org/ev_logs/vin4401c_noise.json"]
    )

    client.provider.make_request(
        method="sim_installMocks",
        params={
            "llm_mocks": {
                ".*": json.dumps({
                    "canary": "CANARY_AGENT_RECALL_LEMON_V1",
                    "verdict": "CLAIM_REJECTED",
                    "confidence": 95,
                    "severity_score": 10,
                    "reason": "Subwoofer vibration is user audio preference, not firmware safety defect."
                })
            },
            "web_mocks": {".*": {"status": 200, "body": "AUDIO_DB:88dB"}}
        }
    )
    contract.connect(consumer).adjudicate_lemon_claim(args=[vault_id])

    contract.connect(consumer).appeal_verdict(
        args=[vault_id, "Subwoofer rattle vibrates steering column excessively."],
        value=100000000000000000
    )

    client.provider.make_request(
        method="sim_installMocks",
        params={
            "llm_mocks": {
                ".*": json.dumps({
                    "canary": "CANARY_AGENT_RECALL_LEMON_V1",
                    "verdict": "APPEAL_DISMISSED",
                    "reason": "No structural steering vibration verified in telemetry."
                })
            },
            "web_mocks": {".*": {"status": 200, "body": "STEERING_VIB:NORMAL"}}
        }
    )
    contract.connect(consumer).adjudicate_appeal(
        args=[vault_id, "https://independent-lab.org/vin4401c_vib_test.txt"]
    )

    v_final = json.loads(contract.get_vault(args=[vault_id]).call())
    assert v_final["status"] == 5  # SETTLED_REJECTED
    assert v_final["verdict"] == "CLAIM_REJECTED"


def test_agentrecall_v3_syndicate_coguarantor_pooling(client):
    """Test Milestone v3: Battery supplier / Tier-1 co-guarantor pools into warranty escrow."""
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]
    battery_vendor = client.accounts[2]

    # OEM deposits 1 GEN
    tx = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-PORSCHE-TAYCAN-01", "v2026.5.1", 6000],
        value=1000000000000000000
    )
    vid = tx.return_value

    # Battery vendor co-guarantees 0.5 GEN
    contract.connect(battery_vendor).pledge_warranty_escrow(
        args=[vid],
        value=500000000000000000
    )

    v = json.loads(contract.get_vault(args=[vid]).call())
    assert v["escrow_amount"] == "1500000000000000000"
    assert v["co_guarantor_count"] == 2

    pledges = json.loads(contract.get_vault_pledges(args=[vid]).call())
    assert len(pledges) == 2
    assert pledges[0]["role"] == "OEM_PRIMARY"
    assert pledges[1]["role"] == "COMPONENT_CO_GUARANTOR"


def test_agentrecall_v3_reputation_tiers_and_leaderboard(client):
    """Test Milestone v3: OEM reputation profile, tier progression, and leaderboard."""
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]

    # Check baseline reputation
    prof = json.loads(contract.get_reputation_profile(args=[str(oem)]).call())
    assert prof["score"] == 10
    assert prof["tier"] == "BRONZE_OEM"
    assert prof["is_fast_track_eligible"] is False

    # Create & clean expiry to gain +20 pts
    tx = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-BYD-SEAL-771", "v2026.2.0", 100],
        value=1000000000000000000
    )
    vid = tx.return_value

    contract.connect(oem).cancel_or_reclaim(args=[vid])

    prof2 = json.loads(contract.get_reputation_profile(args=[str(oem)]).call())
    assert prof2["score"] == 30
    assert prof2["tier"] == "SILVER_OEM"

    board = json.loads(contract.get_oem_leaderboard().call())
    assert len(board) >= 1
    assert board[0]["address"] == str(oem).lower()
