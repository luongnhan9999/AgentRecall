import pytest
import json

def test_cooling_window_cannot_be_accelerated_by_unrelated_vault_activity(client):
    """
    Steward verification test:
    Proves that 12/24-block cooling-off windows mature ONLY with elapsed chain time,
    and CANNOT be accelerated by unrelated vault activity.
    """
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]
    attacker = client.accounts[2]
    victim = "0x8888888888888888888888888888888888888888"

    # 1. OEM registers legitimate warranty vault
    tx1 = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-TESLA-ALPHA", "v1.0.0", 100],
        value=1000000000000000000
    )
    vault_id = tx1.return_value

    # 2. Consumer files claim and enters AWAITING_PAYOUT
    contract.connect(consumer).file_lemon_claim(
        args=[vault_id, "https://telemetry.org/vin_alpha.json"]
    )

    client.provider.make_request(
        method="sim_installMocks",
        params={
            "llm_mocks": {
                ".*": json.dumps({
                    "canary": "CANARY_AGENT_RECALL_LEMON_V1",
                    "verdict": "LEMON_FULL_REFUND",
                    "confidence": 99,
                    "severity_score": 90,
                    "reason": "Critical brake failure confirmed."
                })
            },
            "web_mocks": {".*": {"status": 200, "body": "DTC:U0129 CRITICAL"}}
        }
    )
    contract.connect(consumer).adjudicate_lemon_claim(args=[vault_id])

    # 3. Simulate spam burst of unrelated vault activity
    for i in range(10):
        contract.connect(attacker).register_warranty_vault(
            args=[victim, f"VIN-SPAM-BURST-{i}", "v1.0", 50],
            value=100000000000000000
        )

    # 4. Immediate finalization on target vault MUST REVERT
    with pytest.raises(Exception) as exc_info:
        contract.connect(oem).finalize_settlement(args=[vault_id])
    assert "cooling-off" in str(exc_info.value).lower()


def test_appeal_verdict_allowed_within_window_despite_unrelated_vaults(client):
    """
    STEWARD REQUIRED RUNTIME COVERAGE:
    Exercises `appeal_verdict` within the cooling-off window after intense unrelated vault activity,
    proving that unrelated vault activity CANNOT prematurely close the appeal window.
    """
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]
    attacker = client.accounts[2]
    victim = "0x8888888888888888888888888888888888888888"

    # 1. Register warranty vault
    tx1 = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-APPEAL-CHECK", "v1.0.0", 100],
        value=1000000000000000000
    )
    vault_id = tx1.return_value

    # 2. File claim and adjudicate
    contract.connect(consumer).file_lemon_claim(
        args=[vault_id, "https://telemetry.org/appeal_check.json"]
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
                    "reason": "Normal operational parameters."
                })
            },
            "web_mocks": {".*": {"status": 200, "body": "STATUS:OK"}}
        }
    )
    contract.connect(consumer).adjudicate_lemon_claim(args=[vault_id])

    # 3. Attacker bursts 15 unrelated vaults to simulate protocol-action manipulation
    for i in range(15):
        contract.connect(attacker).register_warranty_vault(
            args=[victim, f"VIN-UNRELATED-BURST-{i}", "v1.0", 10],
            value=100000000000000000
        )

    # 4. Appeal within active window MUST SUCCEED despite 15 unrelated vaults
    contract.connect(consumer).appeal_verdict(
        args=[vault_id, "Legitimate appeal: independent inspection shows battery defect."],
        value=100000000000000000
    )
    v_data = json.loads(contract.get_vault(args=[vault_id]).call())
    assert v_data["status"] == 6  # STATUS_DISPUTED
    assert v_data["dispute_bond"] == str(100000000000000000)


def test_appeal_window_reverts_at_or_after_standard_24_block_deadline_with_unrelated_activity():
    """
    STEWARD REQUIRED TEST (Standard OEM - 24 blocks / 72s):
    Verifies that calling appeal_verdict AT OR AFTER the 24-block (72s) deadline strictly REVERTS,
    and cannot be bypassed, reset, or accelerated by burst activity on unrelated vaults.
    """
    from gltest.direct.loader import deploy_contract
    from gltest.direct.vm import VMContext
    from datetime import datetime, timedelta

    vm = VMContext()
    with vm.activate():
        oem, consumer, attacker = [bytes.fromhex(f"{i+1:040x}") for i in range(3)]
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # 1. Standard OEM creates Vault 1
        vm._value = 10**18
        vm._refresh_gl_message()
        v1_id = contract.register_warranty_vault(Address(consumer), "VIN-TESLA-MOD3-2026", "v12.4", 6000)

        # 2. Consumer files defect claim & AI audit completes -> enters STATUS_AWAITING_PAYOUT
        vm.startPrank(consumer)
        contract.file_lemon_claim(v1_id, "https://telemetry.org/log1.json")
        vm.mock_web(".*", {"status": 200, "body": "DTC:U0100"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "CLAIM_REJECTED",
            "confidence": 90,
            "severity_score": 10,
            "reason": "Harmless diagnostic ping."
        }))
        contract.adjudicate_lemon_claim(v1_id)

        # 3. Simulate unrelated vault activity (burst transactions on other vaults)
        vm.startPrank(attacker)
        for i in range(10):
            victim = bytes.fromhex(f"{i+50:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(victim), f"VIN-RIVIAN-R1T-{i}", "v2.0", 6000)

        # 4. Warp chain time exactly to the 24-block deadline (24 blocks * 3s = 72s)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=72)).isoformat())

        # 5. Calling appeal_verdict AT the 24-block deadline MUST REVERT!
        vm.startPrank(consumer)
        vm._value = 10**17
        vm._refresh_gl_message()
        at_deadline_reverted = False
        try:
            contract.appeal_verdict(v1_id, "Appeal filed exactly at 24-block deadline.")
        except Exception as e:
            at_deadline_reverted = "Dispute cooling-off window (24 blocks / 72s) has expired." in str(e)
        assert at_deadline_reverted, "appeal_verdict AT 24-block deadline (72s) must revert"

        # 6. Advance further past deadline (+80s)
        vm.warp((cur + timedelta(seconds=80)).isoformat())

        # 7. Calling appeal_verdict AFTER the 24-block deadline MUST ALSO REVERT!
        after_deadline_reverted = False
        try:
            contract.appeal_verdict(v1_id, "Appeal filed after 24-block deadline.")
        except Exception as e:
            after_deadline_reverted = "Dispute cooling-off window (24 blocks / 72s) has expired." in str(e)
        assert after_deadline_reverted, "appeal_verdict AFTER 24-block deadline must revert"


def test_appeal_window_reverts_at_or_after_fast_track_12_block_deadline():
    """
    STEWARD REQUIRED TEST (Fast-Track OEM - 12 blocks / 36s):
    Verifies that Gold/Platinum OEMs have a 12-block (36s) fast-track window,
    and appeal_verdict strictly reverts AT OR AFTER 36 seconds, despite unrelated vault activity.
    """
    from gltest.direct.loader import deploy_contract
    from gltest.direct.vm import VMContext
    from datetime import datetime, timedelta

    vm = VMContext()
    with vm.activate():
        oem, consumer, other = [bytes.fromhex(f"{i+10:040x}") for i in range(3)]
        vm.startPrank(oem)
        contract = deploy_contract("contracts/contract.py", vm)
        from genlayer.py.types import Address

        # OEM establishes Gold Tier reputation
        for i in range(2):
            victim = bytes.fromhex(f"{i+90:040x}")
            vm._value = 10**18
            vm._refresh_gl_message()
            vid = contract.register_warranty_vault(Address(victim), f"VIN-GOLD-{i}", "v1.0", 10)
            cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
            vm.warp((cur + timedelta(seconds=35)).isoformat())
            contract.cancel_or_reclaim(vid)

        # Register fast-track vault
        vm._value = 10**18
        vm._refresh_gl_message()
        v_fast = contract.register_warranty_vault(Address(consumer), "VIN-PORSCHE-TAYCAN-2026", "v4.1", 6000)

        vm.startPrank(consumer)
        contract.file_lemon_claim(v_fast, "https://telemetry.org/log_fast.json")
        vm.mock_web(".*", {"status": 200, "body": "DTC:C1100"})
        vm.mock_llm(".*", json.dumps({
            "canary": "CANARY_AGENT_RECALL_LEMON_V1",
            "verdict": "PARTIAL_REPAIR_COMPENSATION",
            "confidence": 90,
            "severity_score": 45,
            "reason": "Moderate sensor error."
        }))
        contract.adjudicate_lemon_claim(v_fast)

        # Unrelated activity on other vaults
        vm.startPrank(other)
        for i in range(5):
            c_addr = bytes.fromhex(f"{i+120:040x}")
            vm._value = 10**16
            vm._refresh_gl_message()
            contract.register_warranty_vault(Address(c_addr), f"VIN-OTHER-{i}", "v1.0", 100)

        # Warp chain time exactly to the 12-block fast-track deadline (12 blocks * 3s = 36s)
        cur = datetime.fromisoformat(vm._datetime.replace("Z", "+00:00"))
        vm.warp((cur + timedelta(seconds=36)).isoformat())

        # Calling appeal_verdict AT the 12-block deadline MUST REVERT!
        vm.startPrank(consumer)
        vm._value = 10**17
        vm._refresh_gl_message()
        at_deadline_reverted = False
        try:
            contract.appeal_verdict(v_fast, "Appeal filed at 12-block fast-track deadline.")
        except Exception as e:
            at_deadline_reverted = "Dispute cooling-off window (12 blocks / 36s) has expired." in str(e)
        assert at_deadline_reverted, "appeal_verdict AT 12-block deadline (36s) must revert"

        # Advance further past 12-block deadline (+45s)
        vm.warp((cur + timedelta(seconds=45)).isoformat())

        # Calling appeal_verdict AFTER the 12-block deadline MUST ALSO REVERT!
        after_deadline_reverted = False
        try:
            contract.appeal_verdict(v_fast, "Appeal filed after 12-block deadline.")
        except Exception as e:
            after_deadline_reverted = "Dispute cooling-off window (12 blocks / 36s) has expired." in str(e)
        assert after_deadline_reverted, "appeal_verdict AFTER 12-block deadline must revert"

