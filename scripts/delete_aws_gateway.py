import argparse
import boto3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-id", required=True)
    ap.add_argument("--region", default="eu-central-1")
    args = ap.parse_args()
    boto3.client("apigateway", region_name=args.region).delete_rest_api(restApiId=args.api_id)
    print(f"Deleted API Gateway {args.api_id} in {args.region}")


if __name__ == "__main__":
    main()
