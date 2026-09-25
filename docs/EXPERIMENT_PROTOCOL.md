# Experiment Protocol

Use this protocol if you want results that are actually comparable rather than anecdotal.

## Independent variable

Egress path:

- direct baseline
- one fixed AWS API Gateway
- one mobile proxy path you control
- one configured IPv6 source address

## Controlled variables

Keep these identical across cases:

- target URL/path
- request method and headers
- request count
- concurrency
- timeout
- geographic origin where practical
- client library/version

## Repeatability

Run at least three trials per egress path. Network performance changes over time, so a single run is weak evidence.

## Primary measurements

- success rate
- status-code distribution
- transport error distribution
- p50 latency
- p95 latency
- mean latency

## Interpretation

Do not interpret one 403/429 as proof that an egress path is categorically blocked. Compare distributions over repeated controlled runs. Likewise, a clean run against one target does not generalize to unrelated platforms.

## Authorized testing boundary

Use staging systems, your own endpoints, vendor sandboxes, or targets for which you have explicit authorization. The benchmark intentionally does not implement CAPTCHA bypass, browser fingerprint spoofing, automated IP rotation on rejection, or rate-limit circumvention logic.
