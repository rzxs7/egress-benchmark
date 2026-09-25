from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import yaml


@dataclass(slots=True)
class TargetConfig:
    url: str
    allowed_hosts: list[str]


@dataclass(slots=True)
class BenchmarkConfig:
    requests_per_case: int = 20
    concurrency: int = 4
    timeout_seconds: float = 10.0
    delay_between_batches_ms: int = 100
    success_status_min: int = 200
    success_status_max: int = 399
    max_requests_per_case: int = 500
    max_concurrency: int = 20


@dataclass(slots=True)
class CaseConfig:
    baseline: dict = field(default_factory=dict)
    aws_gateway: dict = field(default_factory=dict)
    mobile_proxy: dict = field(default_factory=dict)
    ipv6: dict = field(default_factory=dict)


@dataclass(slots=True)
class AppConfig:
    target: TargetConfig
    benchmark: BenchmarkConfig
    cases: CaseConfig


def load_config(path: str | Path) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    target_raw = raw.get("target") or {}
    bench_raw = raw.get("benchmark") or {}
    cases_raw = raw.get("cases") or {}

    cfg = AppConfig(
        target=TargetConfig(
            url=str(target_raw.get("url", "")),
            allowed_hosts=list(target_raw.get("allowed_hosts") or []),
        ),
        benchmark=BenchmarkConfig(**bench_raw),
        cases=CaseConfig(
            baseline=dict(cases_raw.get("baseline") or {}),
            aws_gateway=dict(cases_raw.get("aws_gateway") or {}),
            mobile_proxy=dict(cases_raw.get("mobile_proxy") or {}),
            ipv6=dict(cases_raw.get("ipv6") or {}),
        ),
    )
    validate_config(cfg)
    return cfg


def validate_config(cfg: AppConfig) -> None:
    parsed = urlparse(cfg.target.url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("target.url must be a valid http(s) URL")
    if not cfg.target.allowed_hosts:
        raise ValueError("target.allowed_hosts must contain at least one explicitly authorized host")
    allowed = {h.strip().lower() for h in cfg.target.allowed_hosts if h.strip()}
    if parsed.hostname.lower() not in allowed:
        raise ValueError(
            f"Target host {parsed.hostname!r} is not in target.allowed_hosts. "
            "Add only systems you own or are explicitly authorized to test."
        )

    b = cfg.benchmark
    if not (1 <= b.requests_per_case <= b.max_requests_per_case <= 500):
        raise ValueError("requests_per_case/max_requests_per_case exceed benchmark safety limits")
    if not (1 <= b.concurrency <= b.max_concurrency <= 20):
        raise ValueError("concurrency/max_concurrency exceed benchmark safety limits")
    if b.timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be > 0")
    if b.delay_between_batches_ms < 0:
        raise ValueError("delay_between_batches_ms must be >= 0")
