import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to transform workbook JSON into GAMMAP document format.
    Each section becomes a separate card.
    
    Args:
        event: Contains the workbook data from previous step
        context: AWS Lambda context
    
    Returns:
        GAMMAP formatted document with cards for each section
    """
    try:
        logger.info(f"Starting GAMMAP transformation at {datetime.utcnow().isoformat()}")
        
        # Extract workbook data from the load_result
        if 'load_result' in event:
            workbook = event['load_result'].get('workbook')
            metadata = event['load_result'].get('metadata', {})
        else:
            # Fallback for direct invocation
            workbook = event.get('workbook')
            metadata = event.get('metadata', {})
        
        if not workbook:
            raise ValueError("Missing 'workbook' in event")
        
        # Transform workbook to GAMMAP format with separate cards
        gammap_document = transform_to_gammap_cards(workbook, metadata)
        
        result = {
            'statusCode': 200,
            'gammap_document': gammap_document,
            'metadata': {
                **metadata,
                'transformed_at': datetime.utcnow().isoformat(),
                'total_cards': len(gammap_document.get('cards', []))
            }
        }
        
        logger.info(f"Successfully transformed workbook to GAMMAP format with {result['metadata']['total_cards']} cards")
        return result
        
    except Exception as e:
        logger.error(f"Error transforming to GAMMAP: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e),
            'message': 'Failed to transform workbook to GAMMAP format'
        }


def transform_to_gammap_cards(workbook: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform workbook sections into GAMMAP document with separate cards for each section.
    """
    
    # Build GAMMAP document with cards
    gammap = {
        'metadata': {
            'capability_id': metadata.get('capability_id', workbook.get('capability_id', 'unknown')),
            'capability_name': workbook.get('capability_name', 'Unknown Capability'),
            'generated_at': datetime.utcnow().isoformat(),
            'workbook_source': metadata.get('source_path', ''),
            'version': '1.0',
            'document_type': 'GAMMAP',
            'layer': workbook.get('layer', 'Unknown')
        },
        
        'cards': [
            # Card 1: Executive Overview (Section 0a)
            create_executive_overview_card(workbook),
            
            # Card 2: Document Structure (Section 0b)
            create_document_structure_card(workbook),
            
            # Card 3: Strategic Purpose (Section 1)
            create_strategic_purpose_card(workbook),
            
            # Card 4: Assessment Dimensions (Section 2)
            create_assessment_dimensions_card(workbook),
            
            # Card 5: Architecture Best Practices (Section 3)
            create_architecture_dos_card(workbook),
            
            # Card 6: Architecture Anti-patterns (Section 4)
            create_architecture_donts_card(workbook),
            
            # Card 7: Knowledge Requirements (Section 5)
            create_knowledge_requirements_card(workbook),
            
            # Card 8: Configuration Parameters (Section 6)
            create_configuration_parameters_card(workbook),
            
            # Card 9: Due Diligence Questions (Section 7)
            create_due_diligence_card(workbook),
            
            # Card 10: Scoring Methodology (Section 8)
            create_scoring_methodology_card(workbook),
            
            # Card 11: Sample Scenario (Section 9)
            create_sample_scenario_card(workbook)
        ]
    }
    
    return gammap


def create_executive_overview_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 0a - Executive Overview"""
    section = workbook.get('section_0a', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'overview_items': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_0a'
    
    return {
        'card_id': 'card_01_executive_overview',
        'card_title': 'Executive Overview',
        'card_type': 'overview',
        'source_section': 'section_0a',
        'content': content
    }


def create_document_structure_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 0b - Document Structure"""
    section = workbook.get('section_0b', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'structure_items': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_0b'
    
    return {
        'card_id': 'card_02_document_structure',
        'card_title': 'Document Structure & Process',
        'card_type': 'guidance',
        'source_section': 'section_0b',
        'content': content
    }


def create_strategic_purpose_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 1 - Strategic Purpose"""
    section = workbook.get('section_1', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'strategic_items': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_1'
    
    return {
        'card_id': 'card_03_strategic_purpose',
        'card_title': 'Strategic Purpose & Success Criteria',
        'card_type': 'strategy',
        'source_section': 'section_1',
        'content': content
    }


def create_assessment_dimensions_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 2 - Assessment Dimensions"""
    section = workbook.get('section_2', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'dimensions': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_2'
    
    return {
        'card_id': 'card_04_assessment_dimensions',
        'card_title': 'Assessment Dimensions',
        'card_type': 'assessment',
        'source_section': 'section_2',
        'content': content
    }


def create_architecture_dos_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 3 - Architecture DO's"""
    section = workbook.get('section_3', [])
    
    # If section_3 is a list, use it directly, otherwise copy all content
    if isinstance(section, list):
        content = {'should_do': section}
    else:
        content = {k: v for k, v in section.items() if k != '_metadata'}
    # Add source section to content
    content['_source_section'] = 'section_3'
    
    return {
        'card_id': 'card_05_architecture_dos',
        'card_title': "Architecture DO's - Best Practices",
        'card_type': 'best_practices',
        'source_section': 'section_3',
        'content': content
    }


def create_architecture_donts_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 4 - Architecture DON'Ts"""
    section = workbook.get('section_4', [])
    
    # If section_4 is a list, use it directly, otherwise copy all content
    if isinstance(section, list):
        content = {'should_not_do': section}
    else:
        content = {k: v for k, v in section.items() if k != '_metadata'}
    # Add source section to content
    content['_source_section'] = 'section_4'
    
    return {
        'card_id': 'card_06_architecture_donts',
        'card_title': "Architecture DON'Ts - Anti-patterns",
        'card_type': 'anti_patterns',
        'source_section': 'section_4',
        'content': content
    }


def create_knowledge_requirements_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 5 - Knowledge Requirements"""
    section = workbook.get('section_5', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'knowledge_areas': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_5'
    
    return {
        'card_id': 'card_07_knowledge_requirements',
        'card_title': 'Knowledge & Certification Requirements',
        'card_type': 'knowledge',
        'source_section': 'section_5',
        'content': content
    }


def create_configuration_parameters_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 6 - Configuration Parameters"""
    section = workbook.get('section_6', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'parameters': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_6'
    
    return {
        'card_id': 'card_08_configuration_parameters',
        'card_title': 'Configuration Parameters',
        'card_type': 'configuration',
        'source_section': 'section_6',
        'content': content
    }


def create_due_diligence_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 7 - Due Diligence Questions"""
    section = workbook.get('section_7', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'questions': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_7'
    
    return {
        'card_id': 'card_09_due_diligence',
        'card_title': 'Due Diligence Questions',
        'card_type': 'due_diligence',
        'source_section': 'section_7',
        'content': content
    }


def create_scoring_methodology_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 8 - Scoring Methodology"""
    section = workbook.get('section_8', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'scoring_items': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_8'
    
    return {
        'card_id': 'card_10_scoring_methodology',
        'card_title': 'Scoring Methodology',
        'card_type': 'scoring',
        'source_section': 'section_8',
        'content': content
    }


def create_sample_scenario_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 9 - Sample Scenario"""
    section = workbook.get('section_9', {})
    
    # Handle both list and dict formats
    if isinstance(section, list):
        content = {'scenarios': section}
    elif isinstance(section, dict):
        content = {k: v for k, v in section.items() if k != '_metadata'}
    else:
        content = {}
    # Add source section to content
    content['_source_section'] = 'section_9'
    
    return {
        'card_id': 'card_11_sample_scenario',
        'card_title': 'Sample Implementation Scenario',
        'card_type': 'scenario',
        'source_section': 'section_9',
        'content': content
    }