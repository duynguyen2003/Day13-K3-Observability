# Điều tra challenge: day13-k3-observability-v1

## Triệu chứng quan sát được

Challenge chính thức chạy 5 request thuộc feature `refund` khi `rag_slow` đang bật. Metrics snapshot trong tiến trình ghi nhận:

```json
{"traffic":5,"latency_p50":2651.0,"latency_p95":3703.0,"latency_p99":3703.0,"error_breakdown":{}}
```

Ngưỡng challenge là 2000 ms, vì vậy P95 đã vượt 1703 ms.

## Bằng chứng liên kết

| Session | Correlation ID | Latency trong log |
|---|---|---:|
| `k3-challenge-s05` | `req-6aba26cc` | 3703 ms |
| `k3-challenge-s03` | `req-d84a2cad` | 2650 ms |
| `k3-challenge-s04` | `req-806ac817` | 2651 ms |
| `k3-challenge-s02` | `req-ff63974c` | 2651 ms |
| `k3-challenge-s01` | `req-2bccdfeb` | 2650 ms |

## Root cause và cách xử lý

`rag_slow` thêm độ trễ 2,5 giây trong `app/mock_rag.py` trước khi hoàn thành truy xuất tài liệu. Điều này giải thích latency tăng trong khi error rate vẫn bằng 0. Incident đã được tắt sau khi chạy xong. Với môi trường production, cần thêm timeout/circuit breaker cho retrieval, ghi riêng latency của retrieval span và duy trì alert/runbook theo P95.
