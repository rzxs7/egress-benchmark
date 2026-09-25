from __future__ import annotations

import asyncio
import time

from .metrics import summarize
from .models import CaseSummary, RequestResult
from .transports import ClientSpec


async def _one_request(
    spec: ClientSpec,
    request_index: int,
    success_min: int,
    success_max: int,
) -> RequestResult:
    started = time.perf_counter()
    try:
        resp = await spec.client.get(
            spec.request_url,
            headers={
                "User-Agent": "egress-benchmark/0.1 (+authorized-network-test)",
                "Accept": "application/json,text/plain,*/*",
                "Cache-Control": "no-cache",
            },
        )
        latency_ms = (time.perf_counter() - started) * 1000
        return RequestResult(
            case=spec.name,
            request_index=request_index,
            ok=success_min <= resp.status_code <= success_max,
            status_code=resp.status_code,
            latency_ms=round(latency_ms, 2),
        )
    except Exception as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        return RequestResult(
            case=spec.name,
            request_index=request_index,
            ok=False,
            status_code=None,
            latency_ms=round(latency_ms, 2),
            error=f"{type(exc).__name__}: {exc}",
        )


async def run_case(
    spec: ClientSpec,
    requests_per_case: int,
    concurrency: int,
    delay_between_batches_ms: int,
    success_min: int,
    success_max: int,
) -> tuple[list[RequestResult], CaseSummary]:
    rows: list[RequestResult] = []
    for start in range(0, requests_per_case, concurrency):
        stop = min(start + concurrency, requests_per_case)
        batch = await asyncio.gather(
            *(
                _one_request(spec, i, success_min, success_max)
                for i in range(start, stop)
            )
        )
        rows.extend(batch)
        if stop < requests_per_case and delay_between_batches_ms:
            await asyncio.sleep(delay_between_batches_ms / 1000)
    return rows, summarize(spec.name, rows)
