import io
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError, ClientError

from app.core.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )


def upload_bytes(key: str, data: bytes, content_type: str = "text/plain") -> Optional[str]:
    try:
        client = _client()
        client.put_object(Bucket=settings.s3_bucket, Key=key, Body=io.BytesIO(data), ContentType=content_type)
        return key
    except (BotoCoreError, NoCredentialsError, ClientError):
        return None


def presign_get(key: str, expires: int = 3600) -> Optional[str]:
    try:
        client = _client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=expires,
        )
    except (BotoCoreError, NoCredentialsError, ClientError):
        return None
