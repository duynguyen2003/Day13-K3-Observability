# Bằng chứng correlation ID và PII

Log validator không phát hiện PII leak tiềm ẩn sau bước scrubbing đệ quy.

Một số request đã được làm sạch trong `data/logs.jsonl`:

```json
{"event":"request_received","session_id":"trace-session-05","user_id_hash":"64f6ec689229","feature":"qa","correlation_id":"req-2ea4d3c5","payload":{"message_preview":"Here is my phone [REDACTED_PHONE_VN], what should be logged?"}}
{"event":"request_received","session_id":"trace-session-09","user_id_hash":"4d14d5d4f719","feature":"qa","correlation_id":"req-935b74f6","payload":{"message_preview":"What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}}
{"event":"response_sent","session_id":"k3-challenge-s05","feature":"refund","correlation_id":"req-6aba26cc","latency_ms":3703,"cost_usd":0.001767}
```

Cùng một `correlation_id` xuất hiện ở event request và response, nhờ đó có thể nối triệu chứng từ metric hoặc trace với structured log tương ứng.
