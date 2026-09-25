from __future__ import annotations

import argparse
import json
from urllib.parse import urlparse

import boto3


def require_authorized_target(url: str, confirmation: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise SystemExit("Invalid --target-base-url")
    if confirmation != "I_HAVE_AUTHORIZATION":
        raise SystemExit(
            "Refusing to deploy without --confirm I_HAVE_AUTHORIZATION. "
            "Use only for systems you own or are explicitly permitted to test."
        )


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Deploy ONE fixed-target API Gateway reverse proxy for authorized egress benchmarking."
    )
    ap.add_argument("--target-base-url", required=True)
    ap.add_argument("--region", default="eu-central-1")
    ap.add_argument("--name", default="egress-bench-fixed")
    ap.add_argument("--confirm", required=True)
    args = ap.parse_args()

    require_authorized_target(args.target_base_url, args.confirm)
    client = boto3.client("apigateway", region_name=args.region)
    created_api_id = None
    try:
        api = client.create_rest_api(
            name=args.name,
            description="Fixed-target authorized egress benchmark gateway",
            endpointConfiguration={"types": ["REGIONAL"]},
        )
        created_api_id = api["id"]
        resources = client.get_resources(restApiId=created_api_id)["items"]
        root_id = next(x["id"] for x in resources if x["path"] == "/")

        proxy = client.create_resource(
            restApiId=created_api_id,
            parentId=root_id,
            pathPart="{proxy+}",
        )
        proxy_id = proxy["id"]
        client.put_method(
            restApiId=created_api_id,
            resourceId=proxy_id,
            httpMethod="ANY",
            authorizationType="NONE",
            requestParameters={"method.request.path.proxy": True},
        )
        uri = args.target_base_url.rstrip("/") + "/{proxy}"
        client.put_integration(
            restApiId=created_api_id,
            resourceId=proxy_id,
            httpMethod="ANY",
            type="HTTP_PROXY",
            integrationHttpMethod="ANY",
            uri=uri,
            requestParameters={"integration.request.path.proxy": "method.request.path.proxy"},
        )
        client.create_deployment(restApiId=created_api_id, stageName="prod")
        endpoint = f"https://{created_api_id}.execute-api.{args.region}.amazonaws.com/prod"
        print(json.dumps({"api_id": created_api_id, "region": args.region, "gateway_base_url": endpoint}, indent=2))
        print("\nSave api_id. Delete the gateway when testing is finished.")
    except Exception:
        if created_api_id:
            try:
                client.delete_rest_api(restApiId=created_api_id)
            except Exception:
                pass
        raise


if __name__ == "__main__":
    main()
