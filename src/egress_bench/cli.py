from __future__ import annotations

import argparse
import asyncio

from .config import load_config
from .exporters import export_results
from .runner import run_case
from .transports import build_clients, close_clients


async def _run(config_path: str, output_dir: str) -> int:
    cfg = load_config(config_path)
    specs = await build_clients(cfg.target.url, cfg.cases, cfg.benchmark.timeout_seconds)
    all_rows = []
    summaries = []
    try:
        for spec in specs:
            print(f"\n== {spec.name} ==")
            rows, summary = await run_case(
                spec=spec,
                requests_per_case=cfg.benchmark.requests_per_case,
                concurrency=cfg.benchmark.concurrency,
                delay_between_batches_ms=cfg.benchmark.delay_between_batches_ms,
                success_min=cfg.benchmark.success_status_min,
                success_max=cfg.benchmark.success_status_max,
            )
            all_rows.extend(rows)
            summaries.append(summary)
            print(
                f"success={summary.successes}/{summary.total} "
                f"({summary.success_rate:.1%}) "
                f"p50={summary.p50_ms:.2f}ms p95={summary.p95_ms:.2f}ms "
                f"statuses={summary.status_counts}"
            )
    finally:
        await close_clients(specs)

    paths = export_results(output_dir, cfg.target.url, all_rows, summaries)
    print("\nSaved:")
    for kind, path in paths.items():
        print(f"  {kind}: {path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Authorized egress benchmark: baseline vs fixed AWS gateway vs mobile proxy vs configured IPv6"
    )
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_run(args.config, args.output)))


if __name__ == "__main__":
    main()
