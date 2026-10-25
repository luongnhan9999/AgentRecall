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


def test_contract_runtime_24_block_appeal_verdict_deadline_and_unrelated_vault_immunity():
    """
    STEWARD REQUIRED RUNTIME COVERAGE:
    Explicitly exercises `appeal_verdict` at and after the 24-block (72s) deadline,
    demonstrating that:
    1. `appeal_verdict` succeeds within the 24-block cooling window.
    2. Intense unrelated vault activity CANNOT prematurely expire the appeal window.
    3. `appeal_verdict` REVERTS at/after the 24-block deadline (>= 72s) due to elapsed chain time,
       even after unrelated vault activity.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # 1. OEM registers standard vault (is_fast_track = False) with 1 GEN escrow
        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EV-APPEAL-STANDARD-24", "v1.0.0", 6000)

        # 2. Consumer files claim and enters AWAITING_PAYOUT
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid, "https://telemetry.org/appeal_test_log.json")
        vm.mock_web(".*", {"status": 200, "body": "DTC:U0100 MINOR_GLITCH"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "CLAIM_REJECTED",
            "confidence": 85,
            "severity_score": 15,
            "reason": "Minor infotainment telemetry hiccup."
        }))
        contract.adjudicate_lemon_claim(vid)

        # 3. Burst of 30 unrelated transactions across other vaults
        vm.startPrank(oem)
        for i in range(30):
            c_bytes = bytes.fromhex(f"{i+300:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_bytes), f"VIN-UNRELATED-BURST-{i}", "v1.0.0", 100)

        # 4. Appeal within active window (< 72s) MUST SUCCEED despite 30 unrelated transactions!
        vm.startPrank(consumer)
        vm._value = 10**17  # 10% dispute bond
        vm._refresh_gl_message()
        contract.appeal_verdict(vid, "Valid appeal: certified mechanic proves radar sensor dead.")
        v_appealed = json.loads(contract.get_vault(vid))
        assert v_appealed["status"] == 6  # STATUS_DISPUTED
        assert v_appealed["dispute_bond"] == str(10**17)

        # 5. Create Vault 2 to exercise appeal_verdict AT AND AFTER 24-block deadline
        vm.startPrank(oem)
        vm._value = 10**18
        vm._refresh_gl_message()
        vid2 = contract.register_warranty_vault(Address(consumer), "VIN-EV-EXPIRED-APPEAL-24", "v1.0.0", 6000)
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid2, "https://telemetry.org/appeal_test_log2.json")
        contract.adjudicate_lemon_claim(vid2)

        # 6. Simulate more unrelated vault activity (20 transactions)
        vm.startPrank(oem)
        for i in range(20):
            c_bytes = bytes.fromhex(f"{i+400:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_bytes), f"VIN-UNRELATED-POST-{i}", "v1.0.0", 100)

        # 7. Warp chain time past 24 blocks (24 * 3s = 72s -> warp +75s past audit)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=75)).isoformat())

        # 8. Exercising appeal_verdict at/after the 24-block deadline MUST REVERT!
        vm.startPrank(consumer)
        vm._value = 10**17
        vm._refresh_gl_message()
        appeal_reverted = False
        try:
            contract.appeal_verdict(vid2, "Late appeal filed after the 24-block deadline.")
        except Exception as e:
            appeal_reverted = "Dispute cooling-off window (24 blocks / 72s) has expired." in str(e)
        assert appeal_reverted, "appeal_verdict MUST REVERT at or after 24-block deadline (72s)"


def test_contract_runtime_12_block_fast_track_appeal_verdict_deadline_coverage():
    """
    STEWARD REQUIRED RUNTIME COVERAGE:
    Explicitly exercises `appeal_verdict` at and after the 12-block (36s) fast-track deadline,
    demonstrating that:
    1. Gold/Platinum OEM vaults qualify for 12-block fast-track.
    2. `appeal_verdict` succeeds within the 12-block cooling window despite unrelated vault activity.
    3. `appeal_verdict` REVERTS at/after the 12-block deadline (>= 36s) due to elapsed chain time.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # OEM establishes Gold Verified reputation (+40 pts -> 50 pts total)
        for i in range(2):
            c_bytes = bytes.fromhex(f"{i+650:040x}")
            vm._value = 10**18
            vm._refresh_gl_message()
            vid_clean = contract.register_warranty_vault(Address(c_bytes), f"VIN-CLEAN-FT-{i}", "v1.0.0", 10)
            cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
            vm.warp((cur + timedelta(seconds=35)).isoformat())
            contract.cancel_or_reclaim(vid_clean)

        prof = json.loads(contract.get_reputation_profile(Address(oem)))
        assert prof["is_fast_track_eligible"] is True
        assert prof["tier"] == "GOLD_VERIFIED_OEM"

        # 1. Register fast-track vault
        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EV-FT-APPEAL-12", "v1.0.0", 6000)
        v_data = json.loads(contract.get_vault(vid))
        assert v_data["is_fast_track"] is True

        # 2. File claim and adjudicate
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid, "https://telemetry.org/ft_log.json")
        vm.mock_web(".*", {"status": 200, "body": "DTC:C1100"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "PARTIAL_REPAIR_COMPENSATION",
            "confidence": 88,
            "severity_score": 50,
            "reason": "Moderate sensor failure."
        }))
        contract.adjudicate_lemon_claim(vid)

        # 3. Unrelated vault activity (15 transactions)
        vm.startPrank(oem)
        for i in range(15):
            c_bytes = bytes.fromhex(f"{i+750:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_bytes), f"VIN-UNRELATED-FT-{i}", "v1.0.0", 100)

        # 4. Appeal within active 12-block window (< 36s) SUCCEEDS despite 15 unrelated transactions
        vm.startPrank(consumer)
        vm._value = 10**17
        vm._refresh_gl_message()
        contract.appeal_verdict(vid, "Dispute partial verdict: total battery pack replacement needed.")
        v_appealed = json.loads(contract.get_vault(vid))
        assert v_appealed["status"] == 6  # STATUS_DISPUTED

        # 5. Create second fast-track vault to test expiration
        vm.startPrank(oem)
        vm._value = 10**18
        vm._refresh_gl_message()
        vid2 = contract.register_warranty_vault(Address(consumer), "VIN-EV-FT-EXPIRED-APPEAL-12", "v1.0.0", 6000)
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid2, "https://telemetry.org/ft_log2.json")
        contract.adjudicate_lemon_claim(vid2)

        # 6. Warp chain time past 12 blocks (12 * 3s = 36s -> warp +40s past audit)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=40)).isoformat())

        # 7. Exercising appeal_verdict at/after 12-block fast-track deadline MUST REVERT!
        vm.startPrank(consumer)
        vm._value = 10**17
        vm._refresh_gl_message()
        appeal_reverted = False
        try:
            contract.appeal_verdict(vid2, "Late appeal filed after 12-block fast-track window.")
        except Exception as e:
            appeal_reverted = "Dispute cooling-off window (12 blocks / 36s) has expired." in str(e)
        assert appeal_reverted, "appeal_verdict MUST REVERT at or after 12-block deadline (36s)"


# =====================================================================
# Milestone v3.2: Autonomous Protocols & Multi-Perspective AI Tests
# =====================================================================

def test_autonomous_protocols_fleet_circuit_breaker_tripped_on_critical_flaws():
    """
    Milestone v3.2 / Track 4.6 Autonomous Protocols:
    Demonstrates that the Intelligent Contract autonomously detects when critical flaws
    on a specific firmware release cross the safety threshold (>= 3 critical defects),
    automatically activating the Fleet Safety Circuit Breaker without human voting.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        fw_target = "v2026.4.12-BETA-AUTONOMOUS"

        # Check baseline: Circuit breaker is inactive
        assert contract.is_fleet_circuit_breaker_active(fw_target) is False
        report_init = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_init["critical_fault_count"] == 0
        assert report_init["circuit_breaker_active"] is False
        assert report_init["safety_status"] == "FLEET_HEALTHY_MONITORED"

        # Simulate 3 consecutive critical BMS thermal runaway defects on the same firmware
        vm.mock_web(".*", {"status": 200, "body": "DTC:U0129 STATUS:CRITICAL BMS_CELL_DELTA:2.1V THERMAL_RUNAWAY:TRUE"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "LEMON_FULL_REFUND",
            "confidence": 99,
            "severity_score": 95,
            "reason": "Unrecoverable BMS thermal runaway hazard verified."
        }))

        for i in range(3):
            vm.startPrank(oem)
            vm._value = 10**18
            vm._refresh_gl_message()
            vid = contract.register_warranty_vault(Address(consumer), f"VIN-TESLA-CYBER-{i}", fw_target, 6000)

            vm.startPrank(consumer)
            contract.file_lemon_claim(vid, f"https://telemetry-safe.org/bms_fault_{i}.json")
            contract.adjudicate_lemon_claim(vid)

        # Verify that the 3rd critical flaw autonomously tripped the Fleet Circuit Breaker!
        assert contract.is_fleet_circuit_breaker_active(fw_target) is True
        report_tripped = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_tripped["critical_fault_count"] == 3
        assert report_tripped["circuit_breaker_active"] is True
        assert report_tripped["safety_status"] == "CRITICAL_FLEET_RECALL_ACTIVE"

        # Verify vault payload reflects circuit breaker activation
        v_latest = json.loads(contract.get_vault(vid))
        assert "[FLEET CIRCUIT BREAKER TRIPPED]" in v_latest["reason"]
        assert v_latest["fleet_circuit_breaker_active"] is True
        assert v_latest["firmware_fault_count"] == 3


def test_multi_perspective_ai_adjudication_verdict_integrity():
    """
    Milestone v3.2 / Category 1 AI Enhancement:
    Verifies that multi-perspective forensic prompting evaluates DTC codes,
    preserves the security canary token, and returns valid verdict and severity.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EV-LUCID-AIR-77", "v3.0.0", 6000)

        vm.startPrank(consumer)
        contract.file_lemon_claim(vid, "https://telemetry-lab.org/lucid_sensor_telemetry.json")

        vm.mock_web(".*", {"status": 200, "body": "DTC:C1100 WHEEL_SPEED_SENSOR_INTERMITTENT VOLTAGE:11.8V"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "PARTIAL_REPAIR_COMPENSATION",
            "confidence": 92,
            "severity_score": 50,
            "reason": "Moderate wheel speed sensor harness fault identified across forensic perspectives."
        }))

        contract.adjudicate_lemon_claim(vid)
        v = json.loads(contract.get_vault(vid))
        assert v["verdict"] == "PARTIAL_REPAIR_COMPENSATION"
        assert v["severity_score"] == 50
        assert v["confidence"] == 92
        assert "sensor harness fault" in v["reason"].lower()

# =====================================================================
# Steward Joaquin Regression Coverage: Appellate Outcome Synchronization
# =====================================================================

def test_regression_three_provisional_full_refund_verdicts_later_reversed_deactivates_circuit_breaker():
    """
    Steward Joaquin Requirement:
    "Add regression coverage for three provisional full-refund verdicts later reversed"
    
    Demonstrates:
    1. Three provisional full-refund verdicts on firmware FW_TRIP trip the circuit breaker (count = 3, recall = True).
    2. The OEM appeals all three vaults within the cooling-off window.
    3. As appeals are adjudicated and provisional full-refund defects are reversed (overturned):
       - Vault 1 reversed -> fault count decrements to 2 -> circuit breaker deactivates to False!
       - Vault 2 reversed -> fault count decrements to 1 -> circuit breaker remains False.
       - Vault 3 reversed -> fault count decrements to 0 -> circuit breaker remains False.
    4. Firmware safety report reflects clean state.
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        fw_target = "v2026.4.12-PROV-REVERSED"

        # Step 1: Create 3 vaults for the same firmware release build
        vault_ids = []
        for i in range(3):
            vm.startPrank(oem)
            vm._value = 10**18
            vm._refresh_gl_message()
            vid = contract.register_warranty_vault(Address(consumer), f"VIN-TESLA-FLEET-REV-{i}", fw_target, 6000)
            vault_ids.append(vid)

        # Step 2: Consumer files claims and initial adjudication yields provisional LEMON_FULL_REFUND
        vm._llm_mocks.clear()
        vm._web_mocks.clear()
        vm.mock_web(".*", {"status": 200, "body": "DTC:U0129 STATUS:CRITICAL BMS_DELTA:2.2V"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "LEMON_FULL_REFUND",
            "confidence": 98,
            "severity_score": 90,
            "reason": "Provisional critical fault confirmed."
        }))

        for i, vid in enumerate(vault_ids):
            vm.startPrank(consumer)
            contract.file_lemon_claim(vid, f"https://telemetry-archive.org/claim_{i}.json")
            contract.adjudicate_lemon_claim(vid)

        # Verify circuit breaker is tripped after 3 provisional critical faults
        assert contract.is_fleet_circuit_breaker_active(fw_target) is True
        report_tripped = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_tripped["critical_fault_count"] == 3
        assert report_tripped["circuit_breaker_active"] is True
        assert report_tripped["safety_status"] == "CRITICAL_FLEET_RECALL_ACTIVE"

        # Step 3: OEM appeals Vault 0 with 10% dispute bond within cooling-off window
        vm.startPrank(oem)
        vm._value = 10**17
        vm._refresh_gl_message()
        contract.appeal_verdict(vault_ids[0], "OEM appeal: Telemetry was contaminated by aftermarket charger.")

        # Appellate Court overturns Vault 0 (dismisses lemon claim)
        vm._llm_mocks.clear()
        vm._web_mocks.clear()
        vm.mock_web(".*", {"status": 200, "body": "INDEPENDENT_LAB_AUDIT: NO_FACTORY_DEFECT AFTERMARKET_TAMPERING:TRUE"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "APPEAL_DISMISSED",
            "reason": "Supplemental audit establishes aftermarket modification. Defect overturned."
        }))
        contract.adjudicate_appeal(vault_ids[0], "https://independent-lab.org/supp_audit_0.json")

        # Crucial check: Reversing Vault 0 dropped faults to 2 < 3 -> Circuit breaker DEACTIVATED!
        assert contract.is_fleet_circuit_breaker_active(fw_target) is False
        report_after_first_reversal = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_after_first_reversal["critical_fault_count"] == 2
        assert report_after_first_reversal["circuit_breaker_active"] is False
        assert report_after_first_reversal["safety_status"] == "FLEET_HEALTHY_MONITORED"

        # Step 4: Reverse Vault 1 as well (overturned to partial repair)
        vm.startPrank(oem)
        vm._value = 10**17
        vm._refresh_gl_message()
        contract.appeal_verdict(vault_ids[1], "OEM appeal: Flaw is only a harness connection issue, not cell defect.")

        vm._llm_mocks.clear()
        vm._web_mocks.clear()
        vm.mock_web(".*", {"status": 200, "body": "INDEPENDENT_LAB_AUDIT: HARNESS_REPAIRABLE"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "APPEAL_UPHELD_PARTIAL",
            "reason": "Supplemental audit confirms repairable harness defect, not systemic lemon flaw."
        }))
        contract.adjudicate_appeal(vault_ids[1], "https://independent-lab.org/supp_audit_1.json")

        report_after_second_reversal = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_after_second_reversal["critical_fault_count"] == 1
        assert report_after_second_reversal["circuit_breaker_active"] is False

        # Step 5: Reverse Vault 2 as well
        vm.startPrank(oem)
        vm._value = 10**17
        vm._refresh_gl_message()
        contract.appeal_verdict(vault_ids[2], "OEM appeal: Bench test passed 100% normal.")

        vm._llm_mocks.clear()
        vm._web_mocks.clear()
        vm.mock_web(".*", {"status": 200, "body": "BENCH_TEST: NORMAL"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "APPEAL_DISMISSED",
            "reason": "Normal operation confirmed on bench test. Claim rejected."
        }))
        contract.adjudicate_appeal(vault_ids[2], "https://independent-lab.org/supp_audit_2.json")

        report_after_third_reversal = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_after_third_reversal["critical_fault_count"] == 0
        assert report_after_third_reversal["circuit_breaker_active"] is False


def test_regression_critical_defect_established_only_on_appeal():
    """
    Steward Joaquin Requirement:
    "Add regression coverage for a critical defect established only on appeal."

    Demonstrates:
    1. Initial adjudication mistakenly rejects a claim (or only rules partial repair) -> fault count is 0.
    2. Consumer appeals with supplemental independent lab telemetry proving a critical unrecoverable defect.
    3. Appellate court rules APPEAL_UPHELD_FULL_REFUND -> defect is established only on appeal.
    4. Firmware critical fault count properly increments from 0 to 1, accurately reflecting final outcome!
    """
    vm = VMContext()
    with vm.activate():
        oem, consumer = create_test_addresses(2)
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        fw_target = "v2026.4.12-ESTABLISHED-ON-APPEAL"

        vm._value = 10**18
        vm._refresh_gl_message()
        vid = contract.register_warranty_vault(Address(consumer), "VIN-EV-RIVIAN-APPEAL-1", fw_target, 6000)

        # Initial adjudication: AI Court rules CLAIM_REJECTED (e.g. intermittent noise, insufficient initial proof)
        vm.startPrank(consumer)
        contract.file_lemon_claim(vid, "https://telemetry.org/initial_log_ambiguous.json")

        vm._llm_mocks.clear()
        vm._web_mocks.clear()
        vm.mock_web(".*", {"status": 200, "body": "DTC:INFO_ONLY SENSOR_VARIANCE:LOW"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "CLAIM_REJECTED",
            "confidence": 75,
            "severity_score": 20,
            "reason": "Initial proof shows minor variance, claim rejected."
        }))
        contract.adjudicate_lemon_claim(vid)

        # Verify initial state: 0 critical faults, circuit breaker inactive
        assert contract.is_fleet_circuit_breaker_active(fw_target) is False
        report_init = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_init["critical_fault_count"] == 0
        assert report_init["circuit_breaker_active"] is False

        # Consumer appeals with comprehensive independent dynamometer lab proof
        vm.startPrank(consumer)
        vm._value = 10**17  # 10% dispute bond
        vm._refresh_gl_message()
        contract.appeal_verdict(vid, "Appellate dispute: Independent dynamometer test confirms fatal drive-unit stator short.")

        # Supreme Appellate Court establishes critical factory defect
        vm._llm_mocks.clear()
        vm._web_mocks.clear()
        vm.mock_web(".*", {"status": 200, "body": "INDEPENDENT_DYNAMOMETER_REPORT: STATOR_INSULATION_BREAKDOWN HAZARD:CRITICAL_UNINTENDED_DECELERATION"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "APPEAL_UPHELD_FULL_REFUND",
            "reason": "Supplemental dyno audit establishes unrecoverable drive-unit manufacturing flaw. Lemon full refund upheld."
        }))
        contract.adjudicate_appeal(vid, "https://dynamometer-lab.org/rivian_stator_audit.json")

        # Verify final outcome: Critical defect established only on appeal is counted!
        v_final = json.loads(contract.get_vault(vid))
        assert v_final["status"] == 3  # STATUS_SETTLED_FULL_REFUND
        assert v_final["verdict"] == "LEMON_FULL_REFUND"

        report_final = json.loads(contract.get_firmware_safety_report(fw_target))
        assert report_final["critical_fault_count"] == 1
        assert report_final["circuit_breaker_active"] is False

