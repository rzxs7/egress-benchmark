from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


@dataclass(slots=True)
class ClientSpec:
    name: str
    client: httpx.AsyncClient
    request_url: str


async def build_clients(target_url: str, cases, timeout_seconds: float) -> list[ClientSpec]:
    specs: list[ClientSpec] = []
    timeout = httpx.Timeout(timeout_seconds)

    baseline = cases.baseline
    if baseline.get("enabled", True):
        specs.append(
            ClientSpec(
                name="baseline",
                client=httpx.AsyncClient(timeout=timeout, follow_redirects=True),
                request_url=target_url,
            )
        )

    aws = cases.aws_gateway
    if aws.get("enabled", False):
        base = str(aws.get("gateway_base_url", "")).rstrip("/")
        if not base:
            raise ValueError("aws_gateway.enabled=true but gateway_base_url is empty")
        parsed = urlparse(target_url)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        specs.append(
            ClientSpec(
                name="aws_gateway",
                client=httpx.AsyncClient(timeout=timeout, follow_redirects=True),
                request_url=f"{base}/{path.lstrip('/')}",
            )
        )

    mobile = cases.mobile_proxy
    if mobile.get("enabled", False):
        proxy_url = str(mobile.get("proxy_url", "")).strip()
        if not proxy_url:
            raise ValueError("mobile_proxy.enabled=true but proxy_url is empty")
        specs.append(
            ClientSpec(
                name="mobile_proxy",
                client=httpx.AsyncClient(proxy=proxy_url, timeout=timeout, follow_redirects=True),
                request_url=target_url,
            )
        )

    ipv6 = cases.ipv6
    if ipv6.get("enabled", False):
        addresses = list(ipv6.get("source_addresses") or [])
        if not addresses:
            raise ValueError("ipv6.enabled=true but source_addresses is empty")
        for addr in addresses:
            transport = httpx.AsyncHTTPTransport(local_address=str(addr))
            specs.append(
                ClientSpec(
                    name=f"ipv6[{addr}]",
                    client=httpx.AsyncClient(
                        transport=transport,
                        timeout=timeout,
                        follow_redirects=True,
                    ),
                    request_url=target_url,
                )
            )

    if not specs:
        raise ValueError("No benchmark cases are enabled")
    return specs


async def close_clients(specs: list[ClientSpec]) -> None:
    for spec in specs:
        await spec.client.aclose()
