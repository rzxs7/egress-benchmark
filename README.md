# Egress Benchmark

A reproducible benchmark for comparing four **authorized** network egress paths:

1. `baseline` — direct connection
2. `aws_gateway` — one fixed-target AWS API Gateway reverse proxy
3. `mobile_proxy` — a SOCKS/HTTP proxy you control (for example a lab mobile uplink)
4. `ipv6[...]` — one or more IPv6 source addresses already configured on your own host

The project measures raw transport behavior. It **does not** rotate identity after 403/429 responses, bypass CAPTCHAs, spoof browser/TLS fingerprints, or randomize an IPv6 prefix to evade target controls.

## Metrics

For every case it records:

- success rate
- HTTP status distribution
- request-level latency
- p50 / p95 / mean latency
- connection/transport errors
- CSV request log
- JSON summary
- Markdown comparison table

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item config.example.yaml config.yaml
```

### 1. Start the included lab target

Open terminal A:

```powershell
python scripts\lab_server.py
```

It exposes:

- `http://127.0.0.1:8787/ok`
- `http://127.0.0.1:8787/slow`
- `http://127.0.0.1:8787/rate-limit` (every fifth request returns a simulated 429)
- `http://127.0.0.1:8787/forbidden`

### 2. Run the baseline benchmark

Terminal B:

```powershell
egress-bench --config config.yaml --output results
```

### 3. Enable mobile egress

Run a proxy you control, then set:

```yaml
mobile_proxy:
  enabled: true
  proxy_url: "socks5://127.0.0.1:1080"
```

The benchmark does **not** toggle airplane mode or rotate IPs automatically. This keeps the comparison repeatable and avoids converting a network benchmark into a control-bypass system.

### 4. Enable IPv6 egress

Add IPv6 source addresses that are actually assigned/configured on your test host:

```yaml
ipv6:
  enabled: true
  source_addresses:
    - "2001:db8:1234::10"
    - "2001:db8:1234::11"
```

Each address becomes a separate benchmark case. The runner does not manufacture random `/64` addresses.

### 5. Deploy a fixed AWS Gateway case

AWS credentials must already be configured (`aws configure` or environment/role credentials).

```powershell
python scripts\deploy_fixed_aws_gateway.py `
  --target-base-url "https://YOUR-AUTHORIZED-TARGET.example" `
  --region eu-central-1 `
  --confirm I_HAVE_AUTHORIZATION
```

The command prints `gateway_base_url` and an `api_id`. Put the gateway URL in `config.yaml`:

```yaml
aws_gateway:
  enabled: true
  gateway_base_url: "https://abc123.execute-api.eu-central-1.amazonaws.com/prod"
```

When finished:

```powershell
python scripts\delete_aws_gateway.py --api-id YOUR_API_ID --region eu-central-1
```

The AWS helper intentionally creates **one fixed target gateway**, not a multi-region IP rotator.

## Safety / repeatability guardrails

The benchmark requires the target hostname to appear explicitly in `allowed_hosts`, caps requests per case at 500, and caps concurrency at 20. Those limits are intentionally conservative so results remain interpretable and the tool is suitable for your own staging environments, test endpoints, or explicitly authorized targets.
