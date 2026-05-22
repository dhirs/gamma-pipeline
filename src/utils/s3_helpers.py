import boto3
import json
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def parse_s3_path(s3_path: str) -> Tuple[str, str]:
    """
    Parse S3 path into bucket and key.
    
    Args:
        s3_path: S3 path in format 's3://bucket/key' or 'bucket/key'
    
    Returns:
        Tuple of (bucket_name, object_key)
    
    Raises:
        ValueError: If path format is invalid
    """
    if s3_path.startswith('s3://'):
        path_parts = s3_path.replace('s3://', '').split('/', 1)
    else:
        path_parts = s3_path.split('/', 1)
    
    if len(path_parts) != 2:
        raise ValueError(f"Invalid S3 path format: {s3_path}")
    
    return path_parts[0], path_parts[1]


def read_json_from_s3(bucket: str, key: str, region: str = 'ap-south-1') -> Dict[str, Any]:
    """
    Read JSON file from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        region: AWS region
    
    Returns:
        Parsed JSON data
    """
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read())
        logger.info(f"Successfully read JSON from s3://{bucket}/{key}")
        return data
    except Exception as e:
        logger.error(f"Error reading from S3: {str(e)}")
        raise


def write_json_to_s3(data: Dict[str, Any], bucket: str, key: str, region: str = 'ap-south-1') -> str:
    """
    Write JSON data to S3.
    
    Args:
        data: Data to write
        bucket: S3 bucket name
        key: S3 object key
        region: AWS region
    
    Returns:
        Full S3 path of written object
    """
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json'
        )
        s3_path = f"s3://{bucket}/{key}"
        logger.info(f"Successfully wrote JSON to {s3_path}")
        return s3_path
    except Exception as e:
        logger.error(f"Error writing to S3: {str(e)}")
        raise


def check_s3_object_exists(bucket: str, key: str, region: str = 'ap-south-1') -> bool:
    """
    Check if an S3 object exists.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        region: AWS region
    
    Returns:
        True if object exists, False otherwise
    """
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except s3_client.exceptions.NoSuchKey:
        return False
    except Exception as e:
        logger.error(f"Error checking S3 object: {str(e)}")
        raise