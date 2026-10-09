import pytest
import json
try:
    from genlayer import *
except ImportError:
    pass


def test_cooling_window_cannot_be_accelerated_by_unrelated_vaults(client):
    """
    Proves that creating unrelated vaults does NOT advance cooling-off windows or premature finalization.
    (Steward requirement: 12/24-block appeal and finalization windows mature with elapsed chain time
    and cannot be accelerated by unrelated vault activity).
    """
    contract = client.deploy("contracts/contract.py")
    oem = client.accounts[0]
    consumer = client.accounts[1]
    attacker = client.accounts[2]
    spam_victim = "0x9999999999999999999999999999999999999999"

    # Step 1: OEM registers legitimate warranty vault
    tx1 = contract.connect(oem).register_warranty_vault(
        args=[str(consumer), "VIN-EV-TESLA-ALPHA", "v1.0.0", 100],
        value=1000000000000000000
    )
    target_vault_id = tx1.return_value

    # Step 2: Consumer files claim
    contract.connect(consumer).file_lemon_claim(
        args=[target_vault_id, "https://telemetry.org/vin_alpha.json"]
    )

    # Step 3: Mock AI diagnostic adjudication
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
    contract.connect(consumer).adjudicate_lemon_claim(args=[target_vault_id])

    # Step 4: Attacker spam-creates 50 unrelated vaults to simulate protocol-action counter attack
    # (Attacker assigns spam_victim address to respect non-self warranty rule)
    for i in range(50):
        contract.connect(attacker).register_warranty_vault(
            args=[spam_victim, f"VIN-SPAM-{i}", "v1.0", 10],
            value=100000000000000000
        )

    # Step 5: Finalize settlement MUST REVERT because chain time has not elapsed
    with pytest.raises(Exception) as exc_info:
        contract.connect(consumer).finalize_settlement(args=[target_vault_id])
    assert "Cooling-off challenge window" in str(exc_info.value)

    # Step 6: Advance chain time past cooling-off window (75 seconds > 72s / 24 blocks)
    client.provider.make_request(
        method="sim_increaseTime",
        params=[75]
    )

    # Step 7: Finalize settlement now SUCCEEDS!
    contract.connect(consumer).finalize_settlement(args=[target_vault_id])
    v_data = json.loads(contract.get_vault(args=[target_vault_id]).call())
    assert v_data["status"] == 3  # SETTLED_FULL_REFUND
    assert v_data["verdict"] == "LEMON_FULL_REFUND"
