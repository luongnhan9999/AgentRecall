# ⚡ AgentRecall: Autonomous IoT & EV Firmware Lemon Law Escrow

> **Track:** Consumer Protection / DePIN / Automotive IoT / Hardware SLA  
> **Target Network:** GenLayer StudioNet (Chain ID: `61999` / Hex: `0xF22F`, RPC: `https://studio.genlayer.com/api`)  
> **Deployed Intelligent Contract (v3.0):** [`0x7d5dC14eC572F806fE8Ce98a4B9Ae0b644448F81`](https://studio.genlayer.com/address/0x7d5dC14eC572F806fE8Ce98a4B9Ae0b644448F81)  
> **GitHub Repository:** [https://github.com/luongnhan9999/AgentRecall](https://github.com/luongnhan9999/AgentRecall)  
> **Live Production dApp:** [https://agentrecall-one.vercel.app](https://agentrecall-one.vercel.app) (Mirror: [https://agentrecall-lzdwo1yrj-tynamy.vercel.app](https://agentrecall-lzdwo1yrj-tynamy.vercel.app))

---

## 🚘 1. Bối cảnh & Bài toán nghiệp vụ

Tranh chấp bảo hành xe điện (EV) và thiết bị IoT phần cứng (*Lemon Law*) gây thiệt hại hàng chục tỷ USD mỗi năm giữa **Người tiêu dùng / Chủ phương tiện** (*Consumer / Vehicle Driver*) và **Nhà sản xuất** (*OEM / Hardware Vendor*).

### Vấn đề thực tế:
- Khi xe điện hoặc gateway IoT gặp lỗi firmware nghiêm trọng (treo hệ thống ECU, chai pin bất thường/quá nhiệt cell BMS, mất phanh tái sinh), các hãng xe thường né tránh trách nhiệm, đùn đẩy thủ tục thẩm định hoặc viện cớ người dùng tự ý can thiệp.
- Smart contract truyền thống trên EVM (Solidity) **không thể đọc hiểu log chẩn đoán OBD-II / CAN-bus** hay phân tích crash dump của kernel firmware.
- Người tiêu dùng bị kẹt vốn hàng chục ngàn USD trong khi xe nằm xưởng nhiều tháng trời.

### Giải pháp đột phá từ AgentRecall trên GenLayer:
1. **Ký quỹ bảo chứng bảo hành (`register_warranty_vault`)**: Nhà sản xuất (OEM) khóa quỹ bảo chứng hoàn tiền vào contract khi bàn giao thiết bị hoặc phát hành bản cập nhật firmware.
2. **Người dùng nộp báo cáo lỗi chẩn đoán (`file_lemon_claim`)**: Chủ xe nộp file log OBD-II / CAN-bus (mã lỗi DTC, điện áp cell pin, dump crash firmware) được lưu trữ bất biến.
3. **Bồi thẩm đoàn AI đánh giá kỹ thuật (`adjudicate_lemon_claim`)**:
   - Cào log chẩn đoán qua `gl.nondet.web.render`.
   - Phân tích mã lỗi DTC (Diagnostic Trouble Codes), số lần sạc xả, độ suy giảm pin (Battery SOH), và tần suất xảy ra lỗi.
   - **Phán quyết tự động**:
     - `LEMON_FULL_REFUND`: Lỗi firmware/phần cứng hệ thống đe dọa an toàn $\rightarrow$ Hoàn tiền 100% cho chủ xe.
     - `PARTIAL_REPAIR_COMPENSATION`: Lỗi trung bình hoặc lỗi linh kiện phụ $\rightarrow$ Cắt 40% chi phí sửa chữa cho chủ xe, 60% trả lại OEM.
     - `CLAIM_REJECTED`: Lỗi do người dùng tự ý can thiệp, độ xe, hoặc thông số bình thường $\rightarrow$ Bác đơn.
4. **Cửa sổ bảo vệ (Cooling-off window)** 24 blocks (hoặc 12 blocks Fast-Track) & cọc bond 10% chống griefing.

---

## 🚀 2. Nâng cấp Milestone Đột Phá (v1 $\rightarrow$ v2 $\rightarrow$ v3)

| Phiên bản | Tính năng then chốt & Bảo vệ mật mã | Đảm bảo hệ thống |
| :--- | :--- | :--- |
| **Milestone v1** | - **Canary Token Defense** (`CANARY_AGENT_RECALL_LEMON_V1`).<br>- Web rendering chẩn đoán telemetry CAN-bus/OBD-II.<br>- SHA-256 snapshot cryptographic evidence pinning. | Chống prompt injection tuyệt đối, đảm bảo tính tất định của đồng thuận validator. |
| **Milestone v2** | - **Stake-Based Judicial Appeal Court**: Yêu cầu cọc 10% Dispute Bond.<br>- Thắng kháng cáo: Hoàn 100% bond. Thua: Bị slash chuyển cho đối phương.<br>- **24-block Cooling-off Window** trước khi giải ngân.<br>- Zero admin backdoor. | Chống griefing attack và spam khiếu nại vô cớ, bảo toàn tài chính không có cửa rút lén. |
| **Milestone v3** | - **On-Chain OEM Reliability Engine**: Chấm điểm tín nhiệm và phân hạng OEM (Bronze, Silver, Gold, Platinum).<br>- **Dynamic Fast-Track Adjudication**: OEM đạt Gold/Platinum được rút ngắn cooling-off xuống **12 blocks**.<br>- **Syndicate Co-Guarantor Escrow Pool**: Cho phép nhà sản xuất pin (CATL, LG) và linh kiện cấp 1 đồng ký quỹ bảo chứng với cơ chế hoàn trả theo tỷ lệ (Proportional Solvency Clawback). | Mở rộng quy mô cho chuỗi cung ứng DePIN/Automotive nhiều bên tham gia, tối ưu hóa tốc độ giải ngân cho đối tác uy tín. |

---

## 🏛️ 3. Kiến trúc Smart Contract (`contracts/contract.py`)

- **Magic Pragma:** `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }`
- **GenVM Storage Types:** `TreeMap[u64, WarrantyVault]`, `DynArray[u64]`, `TreeMap[str, bigint]`, `TreeMap[str, u32]`.
- **Native Transfers:** `gl.get_contract_at(recipient).emit_transfer(value=u256(int(amount)))`.
- **Hệ thống hàm chính:**
  - `register_warranty_vault`: OEM khởi tạo ký quỹ bảo hành thiết bị.
  - `pledge_warranty_escrow`: Nhà cung cấp linh kiện đồng bảo chứng bảo hành (Milestone v3).
  - `file_lemon_claim`: Người tiêu dùng nộp bằng chứng log chẩn đoán lỗi.
  - `adjudicate_lemon_claim`: Bồi thẩm đoàn AI phân xử mã lỗi DTC và độ chai pin.
  - `appeal_verdict`: Kháng cáo với 10% cọc bond trong cửa sổ cooling-off.
  - `adjudicate_appeal`: Tòa phúc thẩm tối cao GenLayer phân xử lại với log phòng lab độc lập.
  - `finalize_settlement`: Rút tiền sau khi hết hạn cooling-off (12 hoặc 24 blocks).
  - `cancel_or_reclaim`: Hoàn cọc theo tỷ lệ nếu hết hạn bảo hành mà xe chạy tốt không lỗi.

---

## 🧪 4. Kiểm Thử Tự Động (`tests/test_agentrecall.py`)

Tất cả 7 bài test được kiểm thử tự động và vượt qua **100%**:
- `test_contract_syntax_and_structure`: Kiểm tra cú pháp GenVM.
- `test_vault_struct_attributes`: Kiểm tra trường dữ liệu storage.
- `test_agentrecall_critical_flaw_full_refund`: Lỗi phanh khẩn cấp & BMS kích hoạt hoàn tiền 100%.
- `test_agentrecall_appeal_partial_degraded_bond_accounting`: Kháng cáo cấp linh kiện được chấp thuận một phần.
- `test_agentrecall_appeal_dismissed_bond_slashed`: Kháng cáo thất bại bị phạt tịch thu bond.
- `test_agentrecall_v3_syndicate_coguarantor_pooling`: Nhà cung cấp pin đồng ký quỹ bảo chứng.
- `test_agentrecall_v3_reputation_tiers_and_leaderboard`: Chấm điểm uy tín OEM và thăng hạng.

Chạy kiểm thử:
```bash
pytest -v
```

---

## 💻 5. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Khởi chạy Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Triển khai Contract lên StudioNet:
```bash
python scripts/deploy_to_studionet.py
python scripts/seed_studionet_vaults.py
```
