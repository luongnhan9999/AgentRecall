import os
import sys
import json
import time
from genlayer_py import create_client, create_account, studionet
from genlayer_py.types.calldata import CalldataAddress

PK = "0x1b807b1df022a40f872596b11565e6b6856547dc66996bd3d5a85b376ea3a0ef"
DEPLOYED_FILE = os.path.join(os.path.dirname(__file__), "deployed_address.json")

def main():
    with open(DEPLOYED_FILE, "r") as f:
        data = json.load(f)
    contract_addr = data["contract_address"]

    acct = create_account(PK)
    client = create_client(chain=studionet, account=acct)
    print(f"[*] Seeding EV & IoT Warranty Vaults into {contract_addr}...", flush=True)

    # Vault 2: Lucid Air Sapphire
    consumer_2 = CalldataAddress("0x2222222222222222222222222222222222222222")
    vin_2 = "VIN-EV-LUCID-8812A"
    fw_2 = "v2026.1.0"
    print("\n[*] Registering Vault 2 (Lucid Air Sapphire)...", flush=True)
    tx2 = client.write_contract(
        address=contract_addr,
        function_name="register_warranty_vault",
        args=[consumer_2, vin_2, fw_2, 6000],
        value=15000000000000000 # 0.015 GEN
    )
    print(f"[+] Vault 2 Tx: {tx2}", flush=True)
    client.wait_for_transaction_receipt(tx2)

    # Vault 3: Edge-Compute BMS IoT Gateway
    consumer_3 = CalldataAddress("0x3333333333333333333333333333333333333333")
    vin_3 = "IOT-BMS-GATEWAY-409"
    fw_3 = "v3.1.8-bms-edge"
    print("\n[*] Registering Vault 3 (Industrial BMS IoT)...", flush=True)
    tx3 = client.write_contract(
        address=contract_addr,
        function_name="register_warranty_vault",
        args=[consumer_3, vin_3, fw_3, 6000],
        value=8000000000000000 # 0.008 GEN
    )
    print(f"[+] Vault 3 Tx: {tx3}", flush=True)
    client.wait_for_transaction_receipt(tx3)

    # Check stats
    stats = client.read_contract(address=contract_addr, function_name="get_stats", args=[])
    all_v = client.read_contract(address=contract_addr, function_name="get_all_vaults", args=[])
    print(f"\n[+] Live On-Chain Stats: {stats}", flush=True)
    print(f"[+] Total Live Vaults: {len(json.loads(all_v))}", flush=True)

if __name__ == "__main__":
    main()
