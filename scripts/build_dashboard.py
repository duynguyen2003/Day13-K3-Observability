from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
OUTPUT_PATH = REPO_ROOT / "submission" / "dashboard.html"


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * percent / 100) - 1))
    return ordered[index]


def load_events() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    events = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
            event["_ts"] = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
            events.append(event)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return events


def build_summary(events: list[dict]) -> dict:
    responses = [event for event in events if event.get("event") == "response_sent"]
    requests = [event for event in events if event.get("event") == "request_received"]
    failures = [event for event in events if event.get("event") == "request_failed"]
    latencies = [float(event["latency_ms"]) for event in responses if event.get("latency_ms") is not None]
    costs = [float(event.get("cost_usd", 0)) for event in responses]
    token_in = sum(int(event.get("tokens_in", 0) or 0) for event in responses)
    token_out = sum(int(event.get("tokens_out", 0) or 0) for event in responses)
    quality = [float(event["quality_score"]) for event in responses if event.get("quality_score") is not None]

    latest = max((event["_ts"] for event in events), default=datetime.now(timezone.utc))
    cutoff = latest - timedelta(minutes=60)
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: {"requests": 0, "cost": 0.0})
    for event in events:
        if event["_ts"] < cutoff:
            continue
        bucket = event["_ts"].strftime("%H:%M")
        if event.get("event") == "request_received":
            buckets[bucket]["requests"] += 1
        if event.get("event") == "response_sent":
            buckets[bucket]["cost"] += float(event.get("cost_usd", 0) or 0)

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event_count": len(events),
        "response_count": len(responses),
        "request_count": len(requests),
        "failure_count": len(failures),
        "latency": {"p50": percentile(latencies, 50), "p95": percentile(latencies, 95), "p99": percentile(latencies, 99)},
        "error_rate": (len(failures) / len(requests) * 100) if requests else 0.0,
        "error_breakdown": dict(Counter(event.get("error_type", "unknown") for event in failures)),
        "total_cost": sum(costs),
        "tokens_in": token_in,
        "tokens_out": token_out,
        "quality": mean(quality) if quality else 0.0,
        "traffic": dict(buckets),
    }


def write_dashboard(summary: dict) -> None:
    payload = json.dumps(summary).replace("<", "\\u003c")
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Day 13 AI Observability</title>
  <style>
    :root {{ color-scheme: dark; --bg:#111827; --surface:#1f2937; --line:#374151; --text:#f9fafb; --muted:#9ca3af; --green:#34d399; --yellow:#fbbf24; --red:#fb7185; --blue:#60a5fa; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family:Arial,sans-serif; }}
    main {{ max-width:1240px; margin:0 auto; padding:28px; }}
    header {{ display:flex; align-items:end; justify-content:space-between; gap:16px; border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:20px; }}
    h1 {{ font-size:26px; margin:0 0 6px; }} p {{ margin:0; color:var(--muted); }}
    .status {{ color:var(--green); font-weight:700; white-space:nowrap; }}
    .grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }}
    section {{ background:var(--surface); border:1px solid var(--line); border-radius:7px; padding:18px; min-height:210px; }}
    h2 {{ font-size:16px; margin:0 0 4px; }} .unit {{ font-size:12px; color:var(--muted); }}
    .value {{ font-size:32px; font-weight:700; margin:18px 0 6px; }}
    .detail {{ font-size:13px; color:var(--muted); line-height:1.55; }}
    .ok {{ color:var(--green); }} .warn {{ color:var(--yellow); }} .bad {{ color:var(--red); }}
    .bar {{ height:10px; background:#111827; border-radius:3px; overflow:hidden; margin:18px 0 8px; }}
    .bar > span {{ display:block; height:100%; background:var(--blue); }}
    table {{ width:100%; border-collapse:collapse; margin-top:14px; font-size:13px; }} td {{ border-top:1px solid var(--line); padding:7px 0; }} td:last-child {{ text-align:right; color:var(--muted); }}
    @media (max-width:760px) {{ main {{ padding:16px; }} header {{ align-items:start; flex-direction:column; }} .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body><main>
  <header><div><h1>Day 13 AI Observability</h1><p>Nguồn: data/logs.jsonl | Khoảng thời gian: 60 phút gần nhất | Refresh theo contract: 30 giây</p></div><div class=\"status\">SNAPSHOT RUNTIME</div></header>
  <div class=\"grid\" id=\"panels\"></div>
  <p style=\"margin-top:18px\">Tạo lúc {summary['generated_at']} từ {summary['event_count']} structured log event.</p>
</main>
<script>
const d = {payload};
const f = (n, digits=0) => Number(n).toLocaleString(undefined, {{maximumFractionDigits:digits}});
const state = (actual, threshold, pass) => `<span class="${{pass ? 'ok' : 'bad'}}">${{pass ? 'Đạt ngưỡng' : 'Vượt ngưỡng'}} (${{actual}} ${{pass ? 'đáp ứng' : 'không đáp ứng'}} ${{threshold}})</span>`;
const data = [
  {{title:'Phân vị latency', unit:'ms | SLO: P95 <= 3.000', value:`P95 ${{f(d.latency.p95)}}`, detail:`P50 ${{f(d.latency.p50)}} ms | P99 ${{f(d.latency.p99)}} ms<br>${{state('P95 '+f(d.latency.p95)+' ms', '3.000 ms', d.latency.p95 <= 3000)}}`, ratio:Math.min(d.latency.p95 / 3000 * 100,100)}},
  {{title:'Lưu lượng request', unit:'request mỗi phút | Mục tiêu: >= 1', value:`${{f(d.request_count)}} request`, detail:`${{Object.keys(d.traffic).length}} khoảng phút có dữ liệu | ${{state('Đã ghi nhận traffic', '>= 1 req/phút', d.request_count > 0)}}`, ratio:Math.min(d.request_count * 10,100)}},
  {{title:'Tỷ lệ và phân loại lỗi', unit:'phần trăm | SLO: <= 2%', value:`${{f(d.error_rate,2)}}%`, detail:`${{f(d.failure_count)}} lỗi / ${{f(d.request_count)}} request<br>${{state(f(d.error_rate,2)+'%', '2%', d.error_rate <= 2)}}`, ratio:Math.min(d.error_rate / 2 * 100,100)}},
  {{title:'Chi phí theo thời gian', unit:'USD | Ngân sách: <= 2,50 USD', value:`$${{f(d.total_cost,4)}}`, detail:`${{state('$'+f(d.total_cost,4), '2,50 USD', d.total_cost <= 2.5)}}`, ratio:Math.min(d.total_cost / 2.5 * 100,100)}},
  {{title:'Token đầu vào và đầu ra', unit:'token | Ngân sách: <= 50.000', value:`${{f(d.tokens_in+d.tokens_out)}}`, detail:`Đầu vào ${{f(d.tokens_in)}} | Đầu ra ${{f(d.tokens_out)}}<br>${{state(f(d.tokens_in+d.tokens_out)+' token', '50.000 token', d.tokens_in+d.tokens_out <= 50000)}}`, ratio:Math.min((d.tokens_in+d.tokens_out)/50000*100,100)}},
  {{title:'Quality proxy', unit:'điểm 0-1 | SLO: >= 0,75', value:f(d.quality,2), detail:`Điểm chất lượng trung bình<br>${{state(f(d.quality,2), '0,75', d.quality >= 0.75)}}`, ratio:Math.min(d.quality * 100,100)}}
];
document.querySelector('#panels').innerHTML = data.map(p => `<section><h2>${{p.title}}</h2><div class="unit">${{p.unit}}</div><div class="value">${{p.value}}</div><div class="bar"><span style="width:${{p.ratio}}%"></span></div><div class="detail">${{p.detail}}</div></section>`).join('');
</script></body></html>"""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    summary = build_summary(load_events())
    write_dashboard(summary)
    print(f"Dashboard da tao: {OUTPUT_PATH}")
    print(f"Latency P95: {summary['latency']['p95']:.0f} ms | Request: {summary['request_count']} | Loi: {summary['error_rate']:.2f}%")


if __name__ == "__main__":
    main()
