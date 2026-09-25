from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(slots=True)
class RequestResult:
    case: str
    request_index: int
    ok: bool
    status_code: Optional[int]
    latency_ms: float
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class CaseSummary:
    case: str
    total: int
    successes: int
    failures: int
    success_rate: float
    p50_ms: float
    p95_ms: float
    mean_ms: float
    status_counts: dict[str, int]
    error_counts: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)
