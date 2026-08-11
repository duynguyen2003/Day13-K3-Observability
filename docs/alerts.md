# Alert va Runbook

Moi alert phai dua tren trieu chung nguoi dung hoac SLO, khong dua truc tiep vao ten implementation noi bo.

## Alert 1

- Ten: high_latency_p95
- Severity: warning
- SLI/SLO lien quan: latency_p95_ms <= 3000
- Dieu kien va thoi gian duy tri: p95 latency cao hon 3000 ms trong 5 phut
- Anh huong toi nguoi dung: nguoi dung phai cho lau, chat co cam giac treo
- Ba buoc kiem tra dau tien: mo panel latency; loc trace cham trong cung time range; tim log cung correlation_id de xac dinh span cham
- Mitigation tam thoi: tat incident/feature gay cham, giam concurrency hoac rollback prompt/model neu thay doi gan nhat lien quan
- Owner: observability-oncall

## Alert 2

- Ten: elevated_error_rate
- Severity: critical
- SLI/SLO lien quan: error_rate_pct <= 2
- Dieu kien va thoi gian duy tri: error rate cao hon 2% trong 5 phut
- Anh huong toi nguoi dung: request that bai hoac tra 500, khong nhan duoc cau tra loi
- Ba buoc kiem tra dau tien: mo panel errors; nhom theo error_type; lay trace/log cung correlation_id cua mot request fail
- Mitigation tam thoi: rollback thay doi gan nhat, tat incident/feature loi hoac chuyen sang fallback answer
- Owner: observability-oncall

## Alert 3

- Ten: cost_budget_burn
- Severity: warning
- SLI/SLO lien quan: daily_cost_usd <= 2.5
- Dieu kien va thoi gian duy tri: chi phi trong ngay cao hon 2.5 USD trong 15 phut
- Anh huong toi nguoi dung: he thong co the bi throttle hoac cat tinh nang de bao ve ngan sach
- Ba buoc kiem tra dau tien: mo panel cost/tokens; so sanh tokens_in va tokens_out; mo trace co cost cao nhat de xem prompt/docs co bat thuong khong
- Mitigation tam thoi: giam max output, rollback prompt dai, bat rate limit hoac tat luong gay cost spike
- Owner: observability-oncall
