# Security Policy

## Supported Versions
Only the latest deployed version on GenLayer StudioNet is supported.

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Smart Contract Security Architecture
1. **Canary Verification Token**: Every prompt response must echo the static canary token `CANARY_AGENT_RECALL_LEMON_V1`.
2. **Untrusted Data Isolation**: All incoming vehicle telemetry and external URLs scraped via `gl.nondet.web.render` are placed strictly within XML tags (`<telemetry>...</telemetry>`) and treated as untrusted.
3. **Multi-Validator Consensus Hash Pinning**: All participating validators compute a SHA-256 hash of the exact raw text received from the diagnostic log URL. If the hash differs between validators, consensus will reject the transaction.
4. **Economic Anti-Griefing Bonds**: Disputing an AI verdict requires posting a 10% cash bond. Malicious or unmerited appeals result in bond slashing.
5. **No Admin Privileges**: The contract does not implement emergency fund withdrawal or administrative backdoors; funds can only be released through autonomous diagnostic consensus or clean duration expiration.
