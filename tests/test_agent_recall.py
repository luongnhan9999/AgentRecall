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
