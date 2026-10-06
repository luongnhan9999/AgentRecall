# ⚡ AgentRecall: Protocol Architecture & Consensus Mechanics

## Overview
AgentRecall is an autonomous IoT & EV firmware Lemon Law escrow and diagnostic court deployed on GenLayer. It bridges automotive consumer protection legislation with subjective AI validator consensus.

```mermaid
flowchart TD
    OEM["Vehicle OEM / Hardware Manufacturer"] -->|"register_warranty_vault (Locks Lemon Law Escrow)"| B("AgentRecall Escrow Contract")
    CG["Tier-1 Battery & Sensor Suppliers"] -->|"pledge_warranty_escrow (Pools Co-Guarantee)"| B
    CON["EV Driver / Device Consumer"] -->|"file_lemon_claim (Submits CAN-bus / OBD-II Log URL)"| B
    
    B -->|"adjudicate_lemon_claim"| T["AI Diagnostic Tribunal (gl.vm.run_nondet)"]
    T -->|"gl.nondet.web.render"| OBD["OBD-II Diagnostic Trouble Codes (DTC)"]
    T -->|"gl.nondet.web.render"| BMS["BMS Cell Telemetry & Firmware Crash Dump"]
    
    T --> D{"Consensus Verdict"}
    D -->|"Severity >= 80"| V1["LEMON_FULL_REFUND (100% Payout to Consumer)"]
    D -->|"40 <= Severity < 80"| V2["PARTIAL_REPAIR_COMPENSATION (40% Repair, 60% Return to OEM)"]
    D -->|"Severity < 40"| V3["CLAIM_REJECTED (100% Escrow Returned to OEM)"]
    
    V1 --> W1["Cooling-off Challenge Window (12h Fast-Track / 24h Standard)"]
    V2 --> W1
    V3 --> W1
    
    W1 -->|"Appeal within Window + 10% Bond"| APP["Supreme Appellate Jury"]
    W1 -->|"finalize_settlement after Window"| PAY["Native Transfer Payout Execution"]
```

## Consensus Security & Injection Defense
1. **Security Canary Token**: `CANARY_AGENT_RECALL_LEMON_V1` is strictly enforced in the system prompt and validated in `validator_fn`.
2. **XML Isolation Boundaries**: All external diagnostic telemetry text is wrapped in `<telemetry>` tags and treated as untrusted inputs.
3. **Dual Cryptographic Digest**: The contract calculates `SHA-256(raw_diagnostic)` and requires leader and validator consensus to match the snapshot digest.
4. **Milestone v3 Fast-Track Engine**: OEMs with Gold ($\ge 50$ pts) or Platinum ($\ge 100$ pts) trust status automatically unlock an expedited 12-block dispute window.
