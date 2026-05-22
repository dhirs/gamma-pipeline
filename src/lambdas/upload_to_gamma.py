import json
import boto3
import logging
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3', region_name='ap-south-1')
ssm_client = boto3.client('ssm', region_name='ap-south-1')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to upload GAMMAP document to Gamma.
    Creates new or updates existing based on meta.json.
    
    Args:
        event: Contains output_path from save_gammap and metadata
        context: AWS Lambda context
    
    Returns:
        Upload status with Gamma workbook details
    """
    try:
        logger.info(f"Starting Gamma upload at {datetime.utcnow().isoformat()}")
        
        # Extract info from save_result
        if 'save_result' in event:
            output_path = event['save_result'].get('output_path')
            metadata = event['save_result'].get('metadata', {})
        else:
            output_path = event.get('output_path')
            metadata = event.get('metadata', {})
        
        if not output_path:
            raise ValueError("Missing 'output_path' in event")
        
        capability_id = metadata.get('capability_id', 'unknown')
        
        # Parse S3 path to get bucket and key
        if output_path.startswith('s3://'):
            path_parts = output_path.replace('s3://', '').split('/', 1)
        else:
            path_parts = output_path.split('/', 1)
        
        bucket_name = path_parts[0]
        object_key = path_parts[1]
        
        # Extract timestamp from path (e.g., gamma/20260522_095211/gammap_document.json)
        timestamp_folder = object_key.split('/')[-2]  # Get the timestamp folder
        
        # Load the GAMMAP document from S3
        logger.info(f"Loading GAMMAP document from {output_path}")
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        gammap_document = json.loads(response['Body'].read())
        logger.info(f"Loaded GAMMAP document with keys: {list(gammap_document.keys()) if isinstance(gammap_document, dict) else 'Not a dict'}")
        
        # Check for existing meta.json
        meta_key = f'capabilities/output/{capability_id}/gamma/meta.json'
        existing_meta = load_meta_file(bucket_name, meta_key)
        
        # Get Gamma API credentials
        gamma_api_key = get_gamma_api_key()
        gamma_api_url = get_gamma_api_url()
        
        # Upload to Gamma
        if existing_meta and existing_meta.get('gamma_document_id'):
            # Update existing Gamma document
            logger.info(f"Updating existing Gamma document: {existing_meta['gamma_document_id']}")
            gamma_result = update_gamma_document(
                gamma_api_url,
                gamma_api_key,
                existing_meta['gamma_document_id'],
                existing_meta.get('gamma_folder_id'),
                gammap_document,
                capability_id
            )
            operation = 'updated'
        else:
            # Create new Gamma document (and folder if needed)
            logger.info("Creating new Gamma document")
            gamma_result = create_gamma_document(
                gamma_api_url,
                gamma_api_key,
                gammap_document,
                capability_id
            )
            operation = 'created'
        
        # Update meta.json with latest info
        operation_history = existing_meta.get('operation_history', []) if existing_meta else []
        
        meta_data = {
            'gamma_document_id': gamma_result['document_id'],
            'gamma_folder_id': gamma_result.get('folder_id'),
            'gamma_url': gamma_result['document_url'],
            'capability_id': capability_id,
            'last_uploaded_timestamp': timestamp_folder,
            'last_uploaded_path': output_path,
            'last_updated': datetime.utcnow().isoformat(),
            'operation_history': operation_history + [{
                'timestamp': datetime.utcnow().isoformat(),
                'operation': operation,
                'source_path': output_path,
                'folder': timestamp_folder
            }]
        }
        
        # Save meta.json
        logger.info(f"Saving meta.json to s3://{bucket_name}/{meta_key}")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=meta_key,
            Body=json.dumps(meta_data, indent=2),
            ContentType='application/json'
        )
        
        result = {
            'statusCode': 200,
            'message': f'Successfully {operation} Gamma document',
            'gamma_document_id': gamma_result['document_id'],
            'gamma_url': gamma_result['document_url'],
            'operation': operation,
            'metadata': {
                **metadata,
                'uploaded_at': datetime.utcnow().isoformat(),
                'meta_file': f's3://{bucket_name}/{meta_key}'
            }
        }
        
        logger.info(f"Successfully {operation} Gamma document: {gamma_result['document_id']}")
        return result
        
    except Exception as e:
        logger.error(f"Error uploading to Gamma: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e),
            'message': 'Failed to upload to Gamma'
        }


def load_meta_file(bucket: str, key: str) -> Optional[Dict[str, Any]]:
    """
    Load meta.json file from S3 if it exists.
    
    Returns:
        Dictionary with meta data or None if doesn't exist
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        meta_data = json.loads(response['Body'].read())
        logger.info(f"Found existing meta.json with document_id: {meta_data.get('gamma_document_id')}")
        return meta_data
    except s3_client.exceptions.NoSuchKey:
        logger.info("No existing meta.json found - will create new Gamma document")
        return None
    except Exception as e:
        logger.warning(f"Error reading meta.json: {str(e)}")
        return None


def get_gamma_api_key() -> str:
    """
    Get Gamma API key from SSM Parameter Store.
    """
    try:
        response = ssm_client.get_parameter(
            Name='/cap-pipeline/gamma-api-key',
            WithDecryption=True
        )
        logger.info("Retrieved Gamma API key from SSM")
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Failed to get Gamma API key from SSM: {str(e)}")
        raise


def get_gamma_api_url() -> str:
    """
    Get Gamma API URL.
    """
    return "https://public-api.gamma.app/v1.0"


def format_gammap_for_gamma(gammap_document: Dict[str, Any], capability_id: str) -> str:
    """
    Format GAMMAP document as text input for Gamma API.
    """
    lines = []
    
    # Title
    capability_name = gammap_document.get('metadata', {}).get('capability_name', 'Unknown Capability')
    lines.append(f"# {capability_name} - GAMMAP Assessment Methodology")
    lines.append("")
    
    # Get cards and log for debugging
    cards = gammap_document.get('cards', [])
    logger.info(f"Processing {len(cards)} cards for Gamma formatting")
    
    # Map source sections to more readable names
    section_names = {
        'section_0a': 'Section 0a: Executive Overview',
        'section_0b': 'Section 0b: Document Structure',
        'section_1': 'Section 1: Strategic Purpose',
        'section_2': 'Section 2: Assessment Dimensions',
        'section_3': 'Section 3: Architecture Best Practices',
        'section_4': 'Section 4: Architecture Anti-patterns',
        'section_5': 'Section 5: Knowledge Requirements',
        'section_6': 'Section 6: Configuration Parameters',
        'section_7': 'Section 7: Due Diligence',
        'section_8': 'Section 8: Scoring Methodology',
        'section_9': 'Section 9: Sample Scenario'
    }
    
    # Process each card as a section
    for i, card in enumerate(cards, 1):
        card_title = card.get('card_title', 'Untitled')
        source_section = card.get('source_section', '')
        card_id = card.get('card_id', f'card_{i:02d}')
        
        # Add source section label to card title
        section_label = section_names.get(source_section, source_section)
        if section_label:
            lines.append(f"## {card_title} [Source: {section_label}]")
        else:
            lines.append(f"## {card_title}")
        
        logger.info(f"Processing card {i}/{len(cards)}: {card_id} - {card_title} from {source_section}")
        lines.append("")
        
        # Process card content
        content = card.get('content', {})
        for key, value in content.items():
            if value:  # Skip empty values
                # Format key as readable heading
                formatted_key = key.replace('_', ' ').title()
                
                if isinstance(value, list):
                    if value:  # Only if list is not empty
                        lines.append(f"### {formatted_key}")
                        for item in value:
                            if isinstance(item, dict):
                                for sub_key, sub_value in item.items():
                                    if sub_value:
                                        lines.append(f"- **{sub_key}**: {sub_value}")
                            else:
                                lines.append(f"- {item}")
                        lines.append("")
                elif isinstance(value, dict):
                    if value:  # Only if dict is not empty
                        lines.append(f"### {formatted_key}")
                        for sub_key, sub_value in value.items():
                            if sub_value:
                                lines.append(f"**{sub_key}**: {sub_value}")
                        lines.append("")
                elif isinstance(value, str) and value:
                    lines.append(f"### {formatted_key}")
                    lines.append(value)
                    lines.append("")
    
    logger.info(f"Formatted {len(cards)} cards into {len(lines)} lines of text")
    return "\n".join(lines)


def create_gamma_document(api_url: str, api_key: str, gammap_document: Dict[str, Any], capability_id: str) -> Dict[str, Any]:
    """
    Create a new Gamma document.
    
    Returns:
        Dictionary with document_id, folder_id, and document_url
    """
    if not gammap_document or not isinstance(gammap_document, dict):
        logger.error(f"Invalid GAMMAP document format: {type(gammap_document)}")
        raise ValueError("Invalid GAMMAP document format")
    
    # Format GAMMAP document as text for Gamma
    input_text = format_gammap_for_gamma(gammap_document, capability_id)
    capability_name = gammap_document.get('metadata', {}).get('capability_name', 'Unknown Capability')
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Create Gamma generation request
    gamma_payload = {
        'inputText': input_text,
        'format': 'document',  # Document format, not presentation
        'textMode': 'preserve',  # Preserve our formatted text
        'title': f"{capability_name} - GAMMAP Assessment",
        'additionalInstructions': f"IMPORTANT: Use the provided text EXACTLY AS-IS. Do NOT modify, rewrite, or reorganize the content. Each section header already includes [Source: Section X] labels that MUST be preserved. This is a GAMMAP assessment methodology document for {capability_id}. Create cards based on the ## headers provided in the text.",
        'textOptions': {
            'tone': 'professional',
            'audience': 'technical stakeholders'
        }
    }
    
    # Create generation
    logger.info(f"Creating Gamma generation for {capability_id}")
    logger.info(f"Payload being sent: title={gamma_payload.get('title')}, format={gamma_payload.get('format')}, textMode={gamma_payload.get('textMode')}")
    logger.info(f"Input text length: {len(input_text)} characters")
    
    response = requests.post(
        f"{api_url}/generations", 
        json=gamma_payload, 
        headers=headers,
        timeout=30
    )
    
    # Log response details for debugging
    if response.status_code != 200:
        logger.error(f"Gamma API error: Status {response.status_code}, Response: {response.text}")
    
    response.raise_for_status()
    result_data = response.json()
    
    generation_id = result_data.get('generationId')
    logger.info(f"Created generation with ID: {generation_id}")
    logger.info(f"Full response: {result_data}")
    
    # Poll for completion (max 2 minutes)
    document_data = poll_generation_status(api_url, api_key, generation_id)
    
    # TODO: Create folder structure in Gamma if API supports it
    # For now, we'll track the document ID and URL
    result = {
        'document_id': document_data.get('gammaId', generation_id),  # Use gammaId if available
        'folder_id': f'folder_{capability_id}',  # Placeholder - update when folder creation is available
        'document_url': document_data.get('document_url', f'https://gamma.app/docs/{generation_id}')
    }
    
    return result


def update_gamma_document(api_url: str, api_key: str, document_id: str, folder_id: str, gammap_document: Dict[str, Any], capability_id: str) -> Dict[str, Any]:
    """
    Update an existing Gamma document.
    
    Returns:
        Dictionary with document_id and document_url
    """
    if not gammap_document or not isinstance(gammap_document, dict):
        logger.error(f"Invalid GAMMAP document format: {type(gammap_document)}")
        raise ValueError("Invalid GAMMAP document format")
    
    # For updates, create a new generation and reference the old one
    # Gamma API doesn't support direct updates, so we create a new version
    logger.info(f"Creating new version for document {document_id}")
    
    # Format GAMMAP document as text for Gamma
    input_text = format_gammap_for_gamma(gammap_document, capability_id)
    capability_name = gammap_document.get('metadata', {}).get('capability_name', 'Unknown Capability')
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Create new generation as update
    gamma_payload = {
        'inputText': input_text,
        'format': 'document',
        'textMode': 'preserve',
        'title': f"{capability_name} - GAMMAP Assessment (Updated)",
        'additionalInstructions': f"IMPORTANT: Use the provided text EXACTLY AS-IS. Do NOT modify, rewrite, or reorganize the content. Each section header already includes [Source: Section X] labels that MUST be preserved. Updated GAMMAP assessment methodology document for {capability_id}. This is an update to document {document_id}.",
        'textOptions': {
            'tone': 'professional',
            'audience': 'technical stakeholders'
        }
    }
    
    response = requests.post(
        f"{api_url}/generations", 
        json=gamma_payload, 
        headers=headers,
        timeout=30
    )
    
    # Log response details for debugging
    if response.status_code != 200:
        logger.error(f"Gamma API error: Status {response.status_code}, Response: {response.text}")
    
    response.raise_for_status()
    result_data = response.json()
    
    generation_id = result_data.get('generationId')
    logger.info(f"Created updated generation with ID: {generation_id}")
    
    # Poll for completion
    document_url = poll_generation_status(api_url, api_key, generation_id)
    
    result = {
        'document_id': generation_id,  # New generation ID becomes the document ID
        'folder_id': folder_id,
        'document_url': document_url
    }
    
    return result


def poll_generation_status(api_url: str, api_key: str, generation_id: str, max_wait: int = 120) -> str:
    """
    Poll for generation completion.
    
    Returns:
        Document URL when completed
    """
    headers = {
        'X-API-KEY': api_key
    }
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(
            f"{api_url}/generations/{generation_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        status_data = response.json()
        
        status = status_data.get('status')
        logger.info(f"Generation {generation_id} status: {status}")
        
        if status == 'completed':
            # Get the actual document URL from gammaUrl field
            document_url = status_data.get('gammaUrl') or status_data.get('url', f'https://gamma.app/docs/{generation_id}')
            logger.info(f"Generation completed: {document_url}")
            logger.info(f"Full status response: {status_data}")
            return document_url
        elif status == 'failed':
            error_msg = status_data.get('error', 'Generation failed')
            raise Exception(f"Gamma generation failed: {error_msg}")
        
        # Wait before next poll
        time.sleep(5)
    
    raise Exception(f"Generation timed out after {max_wait} seconds")