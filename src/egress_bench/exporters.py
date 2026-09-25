from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .models import CaseSummary, RequestResult


def export_results(
    output_dir: str | Path,
    target_url: str,
    rows: list[RequestResult],
    summaries: list[CaseSummary],
) -> dict[str, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    csv_path = out / f"requests-{stamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["case", "request_index", "ok", "status_code", "latency_ms", "error"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())

    json_path = out / f"summary-{stamp}.json"
    json_path.write_text(
        json.dumps(
            {
                "target": target_url,
                "generated_at_utc": stamp,
                "summaries": [s.to_dict() for s in summaries],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    md_path = out / f"summary-{stamp}.md"
    lines = [
        "# Egress Benchmark Summary",
        "",
        f"Target: `{target_url}`",
        "",
        "| Case | Success | p50 ms | p95 ms | Mean ms | Statuses |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for s in summaries:
        lines.append(
            f"| {s.case} | {s.successes}/{s.total} ({s.success_rate:.1%}) | "
            f"{s.p50_ms:.2f} | {s.p95_ms:.2f} | {s.mean_ms:.2f} | `{s.status_counts}` |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"csv": csv_path, "json": json_path, "markdown": md_path}
