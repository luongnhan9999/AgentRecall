import pytest
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from gltest.direct.loader import deploy_contract, create_test_addresses
from gltest.direct.vm import VMContext

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


# =====================================================================
# Contract-Runtime Tests for Valid Chain Time & Maturation Verification
# (Resolves Steward Feedback: Eliminating protocol-action counters)
# =====================================================================

def test_contract_runtime_24_block_cooling_and_appeal_windows_mature_with_chain_time():
    """
    Contract-Runtime Test:
    Demonstrates that standard 24-block (72s) appeal and finalization windows
    mature strictly with elapsed chain time and CANNOT be accelerated by
    unrelated vault activity.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # 1. OEM registers Lemon Law warranty vault with 1 GEN escrow
        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EV-TESLA-99214X", "v2026.4.12", 6000)

        # 2. Consumer files Lemon Law claim
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid, "https://telemetry-archive.org/ev_logs/brake_failure.json")

        # 3. Adjudicate claim via AI consensus -> status AWAITING_PAYOUT
        vm.mock_web(".*", {"status": 200, "body": "DTC:U0129 STATUS:CRITICAL BMS_CELL_DELTA:1.8V BRAKE_REGEN:FAILED"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "LEMON_FULL_REFUND",
            "confidence": 98,
            "severity_score": 92,
            "reason": "Critical DTC U0129 & BMS cell thermal runaway failure verified."
        }))
        contract.adjudicate_lemon_claim(vid)

        v_adjudicated = json.loads(contract.get_vault(vid))
        assert v_adjudicated["status"] == 2  # AWAITING_PAYOUT
        assert v_adjudicated["is_fast_track"] is False  # Standard 24-block cooling window

        # 4. Immediate finalization must fail (cooling-off window active)
        early_finalize_blocked = False
        try:
            contract.finalize_settlement(vid)
        except Exception as e:
            early_finalize_blocked = "Cooling-off challenge window (24 blocks / 72s) is still active." in str(e)
        assert early_finalize_blocked, "Finalization must be blocked during active cooling-off window"

        # 5. Simulate intense UNRELATED VAULT ACTIVITY (25 transactions across other vaults)
        vm.startPrank(oem)
        for i in range(25):
            c_bytes = bytes.fromhex(f"{i+500:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_bytes), f"VIN-UNRELATED-TX-{i}", "v1.0.0", 100)

        # 6. Verify finalization STILL fails after 25 unrelated transactions!
        # This proves unrelated vault actions DO NOT advance cooling-off deadlines!
        vm.startPrank(consumer)
        unrelated_accelerate_blocked = False
        try:
            contract.finalize_settlement(vid)
        except Exception as e:
            unrelated_accelerate_blocked = "Cooling-off challenge window (24 blocks / 72s) is still active." in str(e)
        assert unrelated_accelerate_blocked, "Unrelated vault activity must NOT accelerate cooling-off finalization"

        # 7. Warp chain time past 72 seconds (24 blocks * 3s = 72s -> warp +75s)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=75)).isoformat())

        # 8. Now finalization SUCCEEDS because actual chain time has matured!
        contract.finalize_settlement(vid)
        v_final = json.loads(contract.get_vault(vid))
        assert v_final["status"] == 3  # SETTLED_FULL_REFUND
        assert v_final["verdict"] == "LEMON_FULL_REFUND"


def test_contract_runtime_12_block_fast_track_cooling_window_matures_with_chain_time():
    """
    Contract-Runtime Test:
    Demonstrates that Gold/Platinum 12-block (36s) fast-track appeal and finalization
    windows mature strictly with elapsed chain time and cannot be accelerated by
    unrelated vault activity.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # OEM establishes Gold Verified reputation (+40 pts -> 50 pts total)
        for i in range(2):
            c_bytes = bytes.fromhex(f"{i+600:040x}")
            vm._value = 10**18
            vm._refresh_gl_message()
            vid_clean = contract.register_warranty_vault(Address(c_bytes), f"VIN-CLEAN-{i}", "v1.0.0", 10)
            cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
            vm.warp((cur + timedelta(seconds=35)).isoformat())
            contract.cancel_or_reclaim(vid_clean)

        prof = json.loads(contract.get_reputation_profile(Address(oem)))
        assert prof["is_fast_track_eligible"] is True
        assert prof["tier"] == "GOLD_VERIFIED_OEM"

        # OEM registers fast-track vault
        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EV-LUCID-AIR-GT", "v2026.5.0", 6000)
        v_data = json.loads(contract.get_vault(vid))
        assert v_data["is_fast_track"] is True

        # Consumer files claim
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid, "https://telemetry-archive.org/ev_logs/sensor_failure.json")

        # Adjudicate claim
        vm.mock_web(".*", {"status": 200, "body": "DTC:C1200 SENSOR_LATENCY:800ms STEERING_TORQUE:DEGRADED"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "PARTIAL_REPAIR_COMPENSATION",
            "confidence": 90,
            "severity_score": 65,
            "reason": "Moderate steering torque sensor failure. Partial repair compensation applies."
        }))
        contract.adjudicate_lemon_claim(vid)

        # Immediate finalization must fail (12 blocks / 36s active)
        try:
            contract.finalize_settlement(vid)
            assert False, "Should not finalize immediately"
        except Exception as e:
            assert "Cooling-off challenge window (12 blocks / 36s) is still active." in str(e)

        # 15 unrelated transactions on other vaults
        vm.startPrank(oem)
        for i in range(15):
            c_bytes = bytes.fromhex(f"{i+700:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_bytes), f"VIN-UNRELATED-FT-{i}", "v1.0.0", 100)

        # Finalize must STILL fail after unrelated actions
        vm.startPrank(consumer)
        try:
            contract.finalize_settlement(vid)
            assert False, "Should not finalize after unrelated transactions"
        except Exception as e:
            assert "Cooling-off challenge window (12 blocks / 36s) is still active." in str(e)

        # Advance chain time by 20s (less than 36s required) -> must STILL fail
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=20)).isoformat())
        try:
            contract.finalize_settlement(vid)
            assert False, "Should not finalize at 20s (< 36s)"
        except Exception as e:
            assert "Cooling-off challenge window (12 blocks / 36s) is still active." in str(e)

        # Advance chain time past 36s (additional 20s -> total 40s)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=20)).isoformat())

        # Finalize now SUCCEEDS
        contract.finalize_settlement(vid)
        v_final = json.loads(contract.get_vault(vid))
        assert v_final["status"] == 4  # SETTLED_PARTIAL
        assert v_final["verdict"] == "PARTIAL_REPAIR_COMPENSATION"


def test_contract_runtime_warranty_expiry_matures_with_chain_time_not_unrelated_vaults():
    """
    Contract-Runtime Test:
    Demonstrates that warranty expiry period matures strictly with elapsed chain time,
    preventing premature escrow reclamation via unrelated vault transactions.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # Register vault with 100 blocks duration (= 300 seconds)
        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-WARRANTY-EXPIRY-EV", "v1.0.0", 100)

        # 1. Immediate reclaim must fail
        try:
            contract.cancel_or_reclaim(vid)
            assert False, "Should not reclaim immediately"
        except Exception as e:
            assert "Cannot reclaim: Warranty coverage duration is still active." in str(e)

        # 2. Execute 35 unrelated transactions on other vaults
        for i in range(35):
            c_bytes = bytes.fromhex(f"{i+800:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_bytes), f"VIN-DUMMY-{i}", "v1.0.0", 100)

        # 3. Reclaim must STILL fail after 35 unrelated transactions!
        try:
            contract.cancel_or_reclaim(vid)
            assert False, "Should not reclaim after unrelated vault activity"
        except Exception as e:
            assert "Cannot reclaim: Warranty coverage duration is still active." in str(e)

        # 4. Warp chain time past 300 seconds (e.g. +305 seconds)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=305)).isoformat())

        # 5. Reclaim now SUCCEEDS
        contract.cancel_or_reclaim(vid)
        v_data = json.loads(contract.get_vault(vid))
        assert v_data["status"] == 7  # EXPIRED_RECLAIMED
        assert v_data["verdict"] == "EXPIRED_CLEAN"


def test_contract_runtime_claim_cannot_be_filed_after_warranty_expired_by_time():
    """
    Contract-Runtime Test:
    Verifies that device consumers cannot file claims once elapsed chain time
    surpasses warranty expiration timestamp.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # Register vault with 50 blocks duration (= 150 seconds)
        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EXPIRED-CLAIM-EV", "v1.0.0", 50)

        # Warp chain time by 160 seconds (> 150s)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=160)).isoformat())

        # Consumer attempts to file claim -> must fail
        vm.startPrank(consumer)
        try:
            contract.file_lemon_claim(vid, "https://telemetry-archive.org/late_claim.json")
            assert False, "Should not allow claim filing after warranty expiration"
        except Exception as e:
            assert "Warranty coverage duration has expired." in str(e)

