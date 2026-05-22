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
    Lambda function to load workbook from S3 and validate all sections.
    
    Args:
        event: Should contain 'workbook_path' - S3 path to the workbook JSON
        context: AWS Lambda context
    
    Returns:
        Loaded workbook data with validation status
    """
    try:
        logger.info(f"Loading workbook at {datetime.utcnow().isoformat()}")
        
        # Extract S3 path from event
        if 'workbook_path' not in event:
            raise ValueError("Missing 'workbook_path' in event")
        
        workbook_path = event['workbook_path']
        
        # Parse S3 path (handle both s3://bucket/key and bucket/key formats)
        if workbook_path.startswith('s3://'):
            path_parts = workbook_path.replace('s3://', '').split('/', 1)
        else:
            path_parts = workbook_path.split('/', 1)
        
        if len(path_parts) != 2:
            raise ValueError(f"Invalid S3 path format: {workbook_path}")
        
        bucket_name = path_parts[0]
        object_key = path_parts[1]
        
        logger.info(f"Loading from bucket: {bucket_name}, key: {object_key}")
        
        # Load the JSON from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        full_data = json.loads(response['Body'].read())
        
        # Extract the workbook node
        if 'workbook' not in full_data:
            raise ValueError("Missing 'workbook' node in the JSON file")
        
        workbook_data = full_data['workbook']
        
        # Define required sections
        required_sections = [
            'section_0a',
            'section_0b', 
            'section_1',
            'section_2',
            'section_3',
            'section_4',
            'section_5',
            'section_6',
            'section_7',
            'section_8',
            'section_9'
        ]
        
        # Validate all sections are present
        missing_sections = []
        sections_status = {}
        
        for section in required_sections:
            if section in workbook_data:
                sections_status[section] = 'present'
                logger.info(f"✓ Section {section} found")
            else:
                sections_status[section] = 'missing'
                missing_sections.append(section)
                logger.warning(f"✗ Section {section} is missing")
        
        # Extract capability metadata
        capability_id = event.get('capability_id', 'unknown')
        
        # If capability_id not provided, try to extract from workbook data
        if capability_id == 'unknown' and 'capability_id' in workbook_data:
            capability_id = workbook_data['capability_id']
        
        # If still unknown, try to extract from path
        if capability_id == 'unknown' and 'capabilities/output/' in object_key:
            path_parts = object_key.split('/')
            if len(path_parts) > 2:
                capability_id = path_parts[2]
        
        # Prepare result
        validation_passed = len(missing_sections) == 0
        
        result = {
            'statusCode': 200 if validation_passed else 400,
            'validation': {
                'passed': validation_passed,
                'sections_status': sections_status,
                'missing_sections': missing_sections,
                'total_sections': len(required_sections),
                'found_sections': len(required_sections) - len(missing_sections)
            },
            'workbook': workbook_data if validation_passed else None,
            'metadata': {
                'capability_id': capability_id,
                'capability_name': workbook_data.get('capability_name', 'Unknown'),
                'source_path': workbook_path,
                'loaded_at': datetime.utcnow().isoformat(),
                'bucket': bucket_name,
                'key': object_key
            }
        }
        
        if validation_passed:
            logger.info(f"✅ All sections validated successfully for capability: {capability_id}")
        else:
            logger.error(f"❌ Validation failed. Missing sections: {', '.join(missing_sections)}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error loading workbook: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e),
            'message': 'Failed to load workbook from S3'
        }