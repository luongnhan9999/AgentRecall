# Changelog

All notable changes to the AgentRecall protocol will be documented in this file.

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
