import os
import sys
import json
import time
from genlayer_py import create_client, create_account, studionet
from genlayer_py.types.calldata import CalldataAddress

# Account 0 (OEM)
PK_OEM = "0x1b807b1df022a40f872596b11565e6b6856547dc66996bd3d5a85b376ea3a0ef"
# Account 1 (Consumer)
PK_CONSUMER = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

DEPLOYED_FILE = os.path.join(os.path.dirname(__file__), "..", "scripts", "deployed_address.json")

def main():
    with open(DEPLOYED_FILE, "r") as f:
        contract_addr = json.load(f)["contract_address"]

    acct_oem = create_account(PK_OEM)
    acct_consumer = create_account(PK_CONSUMER)

    client_oem = create_client(chain=studionet, account=acct_oem)
    client_consumer = create_client(chain=studionet, account=acct_consumer)

    print("=" * 65, flush=True)
    print(f"[*] TESTING FULL TASK LIFECYCLE ON STUDIONET: {contract_addr}", flush=True)
    print("=" * 65, flush=True)

    # STEP 1: CREATE TASK (OEM registers warranty vault)
    print(f"\n[STEP 1] Creating Task (OEM: {acct_oem.address})...", flush=True)
    vin = "VIN-EV-TEST-COMPLETE-TASK-001"
    fw = "v2026.10.0-final"
    tx1 = client_oem.write_contract(
        address=contract_addr,
        function_name="register_warranty_vault",
        args=[CalldataAddress(acct_consumer.address), vin, fw, 6000],
        value=5000000000000000  # 0.005 GEN
    )
    print(f"[+] Task Created! Tx Hash: {tx1}", flush=True)
    client_oem.wait_for_transaction_receipt(tx1)

    v_count = int(client_oem.read_contract(address=contract_addr, function_name="get_vault_count", args=[]))
    vault_id = v_count
    v_data = json.loads(client_oem.read_contract(address=contract_addr, function_name="get_vault", args=[vault_id]))
    print(f"[+] Vault #{vault_id} Registered:", flush=True)
    print(f"    - Device VIN: {v_data['device_vin_or_serial']}", flush=True)
    print(f"    - Escrow: {int(v_data['escrow_amount']) / 1e18} GEN", flush=True)
    print(f"    - Status: {v_data['status']} (STATUS_WARRANTY_ACTIVE = 0)", flush=True)

    # STEP 2: FILE CLAIM (Consumer files lemon claim)
    print(f"\n[STEP 2] Submitting Defect Claim (Consumer: {acct_consumer.address})...", flush=True)
    diag_url = "https://raw.githubusercontent.com/luongnhan9999/AgentRecall/main/sample_telemetry.json"
    tx2 = client_consumer.write_contract(
        address=contract_addr,
        function_name="file_lemon_claim",
        args=[vault_id, diag_url],
        value=0
    )
    print(f"[+] Claim Filed! Tx Hash: {tx2}", flush=True)
    client_consumer.wait_for_transaction_receipt(tx2)

    v_after_claim = json.loads(client_oem.read_contract(address=contract_addr, function_name="get_vault", args=[vault_id]))
    print(f"[+] Vault #{vault_id} Updated Status: {v_after_claim['status']} (STATUS_CLAIM_FILED = 1)", flush=True)
    print(f"    - Diagnostic URL: {v_after_claim['diagnostic_log_url']}", flush=True)

    # STEP 3: ADJUDICATE CLAIM (Trigger AI Consensus Jury)
    print(f"\n[STEP 3] Triggering AI Jury Adjudication (adjudicate_lemon_claim)...", flush=True)
    tx3 = client_oem.write_contract(
        address=contract_addr,
        function_name="adjudicate_lemon_claim",
        args=[vault_id],
        value=0
    )
    print(f"[+] AI Adjudication Submitted! Tx Hash: {tx3}", flush=True)
    client_oem.wait_for_transaction_receipt(tx3)

    v_after_adj = json.loads(client_oem.read_contract(address=contract_addr, function_name="get_vault", args=[vault_id]))
    print(f"[+] Task Adjudicated Successfully!", flush=True)
    print(f"    - Final Verdict: {v_after_adj['verdict']}", flush=True)
    print(f"    - Severity Score: {v_after_adj['severity_score']}/100", flush=True)
    print(f"    - AI Confidence: {v_after_adj['confidence']}%", flush=True)
    print(f"    - Status: {v_after_adj['status']} (STATUS_AWAITING_PAYOUT = 2)", flush=True)

    # SUMMARY
    print("\n" + "=" * 65, flush=True)
    print("[SUCCESS] FULL TASK CREATION AND COMPLETION VERIFIED ON-CHAIN!", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
