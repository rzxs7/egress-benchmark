from __future__ import annotations

from collections import Counter
from statistics import mean

from .models import CaseSummary, RequestResult


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    frac = k - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def summarize(case: str, rows: list[RequestResult]) -> CaseSummary:
    latencies = [r.latency_ms for r in rows]
    successes = sum(1 for r in rows if r.ok)
    status_counts = Counter(str(r.status_code) for r in rows if r.status_code is not None)
    error_counts = Counter(r.error or "" for r in rows if r.error)
    total = len(rows)
    return CaseSummary(
        case=case,
        total=total,
        successes=successes,
        failures=total - successes,
        success_rate=(successes / total) if total else 0.0,
        p50_ms=round(percentile(latencies, 0.50), 2),
        p95_ms=round(percentile(latencies, 0.95), 2),
        mean_ms=round(mean(latencies), 2) if latencies else 0.0,
        status_counts=dict(status_counts),
        error_counts=dict(error_counts),
    )
