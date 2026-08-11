# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Repository: https://github.com/duynguyen2003/Day13-K3-Observability
- Thành viên: Duy Nguyen (GitHub: duynguyen2003)
- Commit SHA cuối: điền sau khi commit và push lần cuối.

## 2. Kết quả kỹ thuật

- `python -m pytest -q`: 22 test passed.
- `python scripts/validate_logs.py`: điểm ước tính 100/100; 49 bản ghi, 23 correlation ID và 0 PII leak tiềm ẩn.
- `python scripts/validate_dashboard.py`: hợp lệ, đủ 6/6 panel theo contract.
- Dashboard runtime: [dashboard.html](dashboard.html), được sinh từ `data/logs.jsonl` bằng lệnh `python scripts/build_dashboard.py`.

## 3. Logging và tracing

- Mỗi request có `x-request-id`/`correlation_id`; response header cũng trả về request ID và thời gian xử lý.
- Log có đủ `user_id_hash`, `session_id`, `feature`, `model` và `env`.
- PII redaction đệ quy che email, số điện thoại Việt Nam, CCCD, thẻ tín dụng, hộ chiếu và trường dữ liệu có dạng địa chỉ.
- Bằng chứng log đã làm sạch: [log-correlation-and-pii.md](evidence/log-correlation-and-pii.md).
- Ảnh trace waterfall: `submission/evidence/trace-waterfall.png`.

## 4. Quản lý phiên bản prompt

- Tên prompt: `day13-chat`.
- Session bằng chứng baseline: `prompt-baseline-evidence`, correlation ID `req-b43c7b77`.
- Session bằng chứng candidate: `prompt-candidate-evidence`, correlation ID `req-79774a76`.
- Label `production` đã được chuyển từ version 1 sang version 2, sau đó rollback về version 1. Ảnh: `submission/evidence/prompt-label-rollback.png`.
- Lưu ảnh trace baseline và candidate với tên `prompt-baseline-trace.png` và `prompt-candidate-trace.png`. Mỗi ảnh cần hiển thị `prompt_name`, `prompt_label`, `prompt_version` và `prompt_source=langfuse`.

## 5. Dashboard, SLO và alert

- Dashboard có 6 panel: phân vị latency, lưu lượng request, tỷ lệ/phân loại lỗi, chi phí, token vào/ra và quality proxy.
- Khoảng thời gian mặc định là 60 phút, refresh theo contract mỗi 30 giây.
- SLO: P95 latency <= 3000 ms, error rate <= 2%, chi phí ngày <= 2,50 USD và quality trung bình >= 0,75.
- Alert gồm `high_latency_p95`, `elevated_error_rate` và `cost_budget_burn`. Runbook nằm trong [docs/alerts.md](../docs/alerts.md).
- Lưu ảnh dashboard runtime với tên `submission/evidence/dashboard-runtime.png`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`.
- Feature bị ảnh hưởng: `refund`.
- Triệu chứng: P95 của 5 request chính thức là 3703 ms, vượt ngưỡng challenge 2000 ms.
- Correlation ID làm bằng chứng: `req-6aba26cc`, latency trong log là 3703 ms.
- Root cause: incident `rag_slow` thêm `time.sleep(2.5)` trong `app/mock_rag.py:retrieve()` trước khi truy xuất tài liệu.
- Fix action: tắt `rag_slow`; trạng thái incident đã được đưa về disabled sau khi kiểm thử.
- Preventive measure: alert theo P95 latency, kiểm tra retrieval span trong Langfuse, bổ sung timeout/circuit breaker và metric latency riêng cho RAG dependency.
- Bằng chứng chi tiết: [challenge-investigation.md](evidence/challenge-investigation.md).

## 7. Danh mục bằng chứng

Xem [evidence/README.md](evidence/README.md) để biết các ảnh cần chụp và tên file tương ứng.

## 8. Đóng góp cá nhân

| Thành viên | Phần việc | Bằng chứng kiểm tra |
|---|---|---|
| Duy Nguyen | Logging, PII redaction, Langfuse prompt/traces, dashboard, alert và điều tra incident | Tests, validators, ảnh Langfuse và Git commit cuối |
