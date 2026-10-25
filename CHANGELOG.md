# Changelog

All notable changes to the AgentRecall protocol will be documented in this file.

## [v3.2.1] - 2026-10-25
### Added & Fixed (Steward Joaquin Review Remediation)
- **Appellate Outcome Synchronization for Fleet Safety Circuit Breakers (`contracts/contract.py`)**:
  - Fully synchronized `firmware_critical_faults` and `fleet_circuit_breaker_active` to reflect final appellate outcomes in `adjudicate_appeal`.
  - **Defects Overturned on Appeal**: When provisional full-refund verdicts are reversed on appeal (e.g. to partial repair or rejection), confirmed critical fault counts decrement. When count falls below threshold (< 3), the recall circuit breaker automatically deactivates to `False` and resets recall timestamps.
  - **Defects Established Only on Appeal**: When a critical flaw is proven via supplemental laboratory logs on appeal after an initial rejection, fault counts properly increment and trip the circuit breaker if the safety threshold is reached.
- **Steward Joaquin Regression Coverage (`tests/test_agentrecall.py`)**:
  - `test_regression_three_provisional_full_refund_verdicts_later_reversed_deactivates_circuit_breaker`: Exercises 3 provisional full-refund verdicts tripping the breaker, followed by 3 reversals deactivating it back to healthy.
  - `test_regression_critical_defect_established_only_on_appeal`: Exercises a claim initially rejected, then proven on appeal, properly incrementing firmware fault count.
  - Test suite expanded with 100% pass rate.

## [v3.2.0] - 2026-10-19
### Added
- **Autonomous Fleet Safety Recall Circuit Breaker (Track 4.6: Autonomous Protocols)**:
  - Implemented firmware defect threshold tracking (`FLEET_CIRCUIT_BREAKER_THRESHOLD = 3`) across the entire fleet.
  - Automatically trips an on-chain safety circuit breaker (`fleet_circuit_breaker_active = True`) when 3+ critical defects are validated by GenVM consensus on a specific firmware build.
  - Broadcasts public NHTSA / Lemon Law recall alerts and marks affected vehicles with active safety warnings.
  - Added on-chain views: `get_firmware_safety_report(firmware_version)` and `is_fleet_circuit_breaker_active(firmware_version)`.
- **Multi-Perspective AI Diagnostic Adjudication (Track 4.1 & 4.2: GenVM AI Jury)**:
  - Upgraded GenVM AI prompt to perform a 3-perspective forensic audit:
    1. *Sensor Forensics*: BMS cell delta, thermocouple spikes, CAN-Bus cyclic redundancy check.
    2. *Firmware Engineering*: Memory leaks, race conditions, ECU watchdog timeouts.
    3. *Statutory Lemon Law Compliance*: Magnuson-Moss & California Song-Beverly Consumer Warranty Acts.
  - Enforced strict structured JSON forensic breakdowns (`sensor_forensics`, `firmware_integrity`, `lemon_law_statutory`) with automated Canary Token anti-jailbreak protection.
- **Milestone Test Verification Suite (`tests/test_agentrecall.py`)**:
  - Expanded test suite to **20/20 passing tests (100% pass rate)** covering fleet circuit breakers, multi-perspective verdicts, time-based appeal cooling-off, and warranty reclamations.
- **Interactive Cockpit & Diagnostic UI Upgrades (`frontend/`)**:
  - Integrated 3-Perspective Forensic Audit tab in `DiagnosticInspectorModal.tsx`.
  - Added real-time animated `FLEET RECALL` pulsing badges and telemetry presets for pack thermal runaway.
  - Added dedicated Autonomous Protocol Circuit Breaker warning banner in `CockpitConsole.tsx`.


## [v3.0.0] - 2026-10-06
### Added
- **On-Chain OEM Reliability & Trust Tier Engine (`contracts/contract.py`)**:
  - Implemented credit score accounting with operational metrics: `stats_clean_warranties`, `stats_claims_resolved`, `stats_appeals_won`, and `stats_appeals_lost`.
  - Defined 4 distinct Trust Tiers: `BRONZE_OEM` (<20 pts), `SILVER_OEM` (20-49 pts), `GOLD_VERIFIED_OEM` (50-99 pts), and `PLATINUM_GUARANTOR` ($\ge 100$ pts).
  - Implemented **Dynamic Fast-Track Adjudication**: Gold and Platinum OEMs qualify for an expedited **12-block dispute cooling-off window**, while Bronze/Silver retain the standard 24 blocks.
  - Implemented `@gl.public.view def get_reputation_profile(user_address)` and `@gl.public.view def get_oem_leaderboard()` returning top 20 ranked manufacturers.
- **Syndicate Co-Guarantor Escrow Pool (`contracts/contract.py`)**:
  - Implemented `@gl.public.write.payable def pledge_warranty_escrow(vault_id)` enabling Tier-1 battery cell makers (CATL, LG) to co-guarantee hardware reliability.
  - Implemented proportional solvency clawback: in the event of partial repairs or clean expiration, escrow shares are distributed proportionally without precision loss.
  - Implemented `@gl.public.view def get_vault_pledges(vault_id)` inspecting active syndicate pledges.
- **Milestone v3 Verification Suite (`tests/test_agentrecall.py`)**:
  - Full suite expanded to 7/7 passing tests (100% pass rate).
- **Automotive Diagnostic Console Frontend (`frontend/`)**:
  - Added Syndicate Co-Guarantor Escrow Modal with contribution slider.
  - Added On-Chain OEM Leaderboard & Trust Tier Drawer displaying ranks, scores, badges, and fast-track statuses.
  - Added dynamic `⚡ 12H FAST-TRACK` and `GUARANTORS` badges on qualifying vaults.

## [v2.0.0] - 2026-10-06
### Added
- **Stake-Based Judicial Appeal Protocol**:
  - Implemented `@gl.public.write.payable def appeal_verdict(vault_id, dispute_reason)` with mandatory 10% staked bond.
  - Implemented Supreme Appellate Diagnostic Board `@gl.public.write def adjudicate_appeal(...)` reviewing supplemental independent lab records.
  - Implemented bond return on appeal upheld and slashing to counterparty on appeal dismissal.
- **24-Block Cooling-off Challenge Window**:
  - Added `AWAITING_PAYOUT` state on initial consensus.
  - Payout can only be finalized via `finalize_settlement` after cooling-off window.

## [v1.0.0] - 2026-10-06
### Added
- **Core Hardware Lemon Law Escrow & AI Tribunal**:
  - Diagnostic telemetry crawling: live OBD-II DTC codes, BMS cell voltages, and firmware kernel crash dumps.
  - Canary Token Defense (`CANARY_AGENT_RECALL_LEMON_V1`).
  - Three-tier verdicts: `LEMON_FULL_REFUND` (severity $\ge 80$), `PARTIAL_REPAIR_COMPENSATION` (severity $40-79$), and `CLAIM_REJECTED` (severity $< 40$).
