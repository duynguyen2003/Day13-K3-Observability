# Checklist bằng chứng

Các bằng chứng dạng văn bản trong thư mục này đã được tạo từ kết quả chạy thực tế. Trước khi nộp bài, cần chụp thêm các ảnh sau:

| Tên file | Nội dung bắt buộc nhìn thấy |
|---|---|
| `langfuse-traces-list.png` | Danh sách ít nhất 10 trace trên Langfuse. Có thể tìm các session từ `trace-session-01` đến `trace-session-10`. |
| `trace-waterfall.png` | Một trace waterfall đầy đủ, nhìn thấy chi tiết generation/span. |
| `prompt-baseline-trace.png` | Session `prompt-baseline-evidence`; metadata của prompt hiển thị label `baseline` và version 1. |
| `prompt-candidate-trace.png` | Session `prompt-candidate-evidence`; metadata của prompt hiển thị label `candidate` và version 2. |
| `prompt-label-rollback.png` | Danh sách prompt version cho thấy label `production` đã được đưa trở lại version 1. |
| `dashboard-runtime.png` | File `submission/dashboard.html` hiển thị đủ 6 panel, đơn vị, ngưỡng và khoảng thời gian. |
| `challenge-trace.png` | Một challenge trace thuộc session `k3-challenge-*`, ưu tiên `k3-challenge-s05`. |

Không đưa `.env`, API key hoặc ảnh chứa secret vào thư mục này.
