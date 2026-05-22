import json
import boto3
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3', region_name='ap-south-1')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to save GAMMAP document to S3.
    
    Args:
        event: Contains the GAMMAP document and metadata
        context: AWS Lambda context
    
    Returns:
        Success status with S3 path
    """
    try:
        logger.info(f"Saving GAMMAP document at {datetime.utcnow().isoformat()}")
        
        # Extract GAMMAP document and metadata
        if 'gammap_document' not in event:
            raise ValueError("Missing 'gammap_document' in event")
        
        gammap_document = event['gammap_document']
        metadata = event.get('metadata', {})
        
        # Extract capability ID for path construction
        capability_id = metadata.get('capability_id', 'unknown')
        
        # Generate timestamp for unique path
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Construct S3 path
        bucket_name = 'datawhistl'
        object_key = f'capabilities/output/{capability_id}/gamma/{timestamp}/gammap_document.json'
        
        # Save to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(gammap_document, indent=2),
            ContentType='application/json'
        )
        
        # Construct full S3 path
        s3_path = f's3://{bucket_name}/{object_key}'
        
        result = {
            'statusCode': 200,
            'message': 'GAMMAP document saved successfully',
            'output_path': s3_path,
            'metadata': {
                **metadata,
                'saved_at': datetime.utcnow().isoformat(),
                'bucket': bucket_name,
                'key': object_key,
                'document_size': len(json.dumps(gammap_document))
            }
        }
        
        logger.info(f"Successfully saved GAMMAP document to {s3_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error saving GAMMAP document: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e),
            'message': 'Failed to save GAMMAP document to S3'
        }