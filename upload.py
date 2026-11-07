import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

ACCESS_KEY = os.environ["AWS_ACCESS_KEY_ID"]
SECRET_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
BUCKET     = os.environ["BUCKET"]
REGION     = os.environ["AWS_REGION"]


def connect_S3(bucket, region, access_key, secret_key):
    s3 = boto3.client("s3", aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key, region_name=region)
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as err:
        raise ConnectionError(f"Cannot reach bucket '{bucket}': {err.response['Error']['Code']}")

    print(f"Connected to S3 bucket '{bucket}'")
    return s3


def upload_S3(bucket, region, access_key, secret_key, local_path="access.log", s3_key="nginx-logs/access.log"):
    # connect to s3 using the s3 connection function above
    s3 = connect_S3(bucket, region, access_key, secret_key)

    # upload file
    s3.upload_file(local_path, bucket, s3_key)

    # check it arrived
    size = s3.head_object(Bucket=bucket, Key=s3_key)["ContentLength"]
    print(f"Completed upload from {local_path} to s3://{bucket}/{s3_key} ({size:,} bytes)")


if __name__ == "__main__":
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    upload_S3(BUCKET, REGION, ACCESS_KEY, SECRET_KEY, s3_key=f"nginx-logs/{now}/access.log")
