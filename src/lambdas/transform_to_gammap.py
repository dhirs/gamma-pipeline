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
    
    return {
        'card_id': 'card_01_executive_overview',
        'card_title': 'Executive Overview',
        'card_type': 'overview',
        'source_section': 'section_0a',
        'content': {
            'what_this_is': section.get('what_this_workbook_is', ''),
            'who_this_is_for': section.get('who_this_is_for', []),
            'what_you_will_get': section.get('what_you_will_get', []),
            'why': section.get('why', {}),
            'what': section.get('what', {}),
            'who': section.get('who', {}),
            'when': section.get('when', {}),
            'where': section.get('where', {}),
            'how': section.get('how', {})
        }
    }


def create_document_structure_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 0b - Document Structure"""
    section = workbook.get('section_0b', {})
    
    return {
        'card_id': 'card_02_document_structure',
        'card_title': 'Document Structure & Process',
        'card_type': 'guidance',
        'source_section': 'section_0b',
        'content': {
            'four_step_process': section.get('four_step_process', []),
            'overview': section.get('overview', ''),
            'layout': section.get('layout', {}),
            'how_to_use': section.get('how_to_use', [])
        }
    }


def create_strategic_purpose_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 1 - Strategic Purpose"""
    section = workbook.get('section_1', {})
    
    return {
        'card_id': 'card_03_strategic_purpose',
        'card_title': 'Strategic Purpose & Success Criteria',
        'card_type': 'strategy',
        'source_section': 'section_1',
        'content': {
            'strategic_purpose': section.get('strategic_purpose', ''),
            'success_criteria': section.get('success_criteria', []),
            'evaluation_points': section.get('evaluation_points', []),
            'key_outcomes': section.get('key_outcomes', []),
            'business_value': section.get('business_value', '')
        }
    }


def create_assessment_dimensions_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 2 - Assessment Dimensions"""
    section = workbook.get('section_2', {})
    
    dimensions = []
    if 'dimensions' in section:
        for dim in section['dimensions']:
            if isinstance(dim, dict):
                dimensions.append({
                    'dimension_name': dim.get('dimension_name', ''),
                    'description': dim.get('description', ''),
                    'weight': dim.get('weight', 0),
                    'test_questions': dim.get('test_questions', []),
                    'evaluation_criteria': dim.get('criteria', [])
                })
    
    return {
        'card_id': 'card_04_assessment_dimensions',
        'card_title': 'Assessment Dimensions',
        'card_type': 'assessment',
        'source_section': 'section_2',
        'content': {
            'dimensions': dimensions,
            'total_dimensions': len(dimensions),
            'assessment_approach': section.get('assessment_approach', '')
        }
    }


def create_architecture_dos_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 3 - Architecture DO's"""
    section = workbook.get('section_3', [])
    
    # Handle if section_3 is a list directly (list of DO's)
    if isinstance(section, list):
        should_do = section
    else:
        should_do = section.get('should_do', [])
    
    return {
        'card_id': 'card_05_architecture_dos',
        'card_title': "Architecture DO's - Best Practices",
        'card_type': 'best_practices',
        'source_section': 'section_3',
        'content': {
            'should_do': should_do,
            'best_practices': section.get('best_practices', []) if isinstance(section, dict) else [],
            'recommended_patterns': section.get('patterns', []) if isinstance(section, dict) else [],
            'implementation_guidelines': section.get('guidelines', []) if isinstance(section, dict) else []
        }
    }


def create_architecture_donts_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 4 - Architecture DON'Ts"""
    section = workbook.get('section_4', [])
    
    # Handle if section_4 is a list directly (list of DON'Ts)
    if isinstance(section, list):
        should_not_do = section
    else:
        should_not_do = section.get('should_not_do', [])
    
    return {
        'card_id': 'card_06_architecture_donts',
        'card_title': "Architecture DON'Ts - Anti-patterns",
        'card_type': 'anti_patterns',
        'source_section': 'section_4',
        'content': {
            'should_not_do': should_not_do,
            'anti_patterns': section.get('anti_patterns', []) if isinstance(section, dict) else [],
            'common_mistakes': section.get('mistakes', []) if isinstance(section, dict) else [],
            'risks_to_avoid': section.get('risks', []) if isinstance(section, dict) else []
        }
    }


def create_knowledge_requirements_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 5 - Knowledge Requirements"""
    section = workbook.get('section_5', {})
    
    knowledge_areas = []
    
    # Process certification paths
    if 'certification_paths' in section:
        for cert in section['certification_paths']:
            if isinstance(cert, dict):
                knowledge_areas.append({
                    'type': 'certification',
                    'name': cert.get('certification_name', ''),
                    'provider': cert.get('provider', ''),
                    'relevance': cert.get('relevance', ''),
                    'level': cert.get('level', '')
                })
    
    # Process learning paths
    if 'learning_paths' in section:
        for path in section['learning_paths']:
            if isinstance(path, dict):
                knowledge_areas.append({
                    'type': 'learning_path',
                    'name': path.get('path_name', ''),
                    'topics': path.get('topics', []),
                    'duration': path.get('estimated_duration', ''),
                    'resources': path.get('resources', [])
                })
    
    return {
        'card_id': 'card_07_knowledge_requirements',
        'card_title': 'Knowledge & Certification Requirements',
        'card_type': 'knowledge',
        'source_section': 'section_5',
        'content': {
            'knowledge_areas': knowledge_areas,
            'certification_paths': section.get('certification_paths', []),
            'learning_paths': section.get('learning_paths', []),
            'skill_requirements': section.get('skill_requirements', [])
        }
    }


def create_configuration_parameters_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 6 - Configuration Parameters"""
    section = workbook.get('section_6', {})
    
    parameters = []
    if 'parameters' in section:
        for param in section['parameters']:
            if isinstance(param, dict):
                parameters.append({
                    'parameter_name': param.get('parameter_name', ''),
                    'description': param.get('description', ''),
                    'type': param.get('type', 'string'),
                    'required': param.get('required', False),
                    'default_value': param.get('default', ''),
                    'validation_rules': param.get('validation', []),
                    'example_values': param.get('examples', [])
                })
    
    return {
        'card_id': 'card_08_configuration_parameters',
        'card_title': 'Configuration Parameters',
        'card_type': 'configuration',
        'source_section': 'section_6',
        'content': {
            'parameters': parameters,
            'total_parameters': len(parameters),
            'required_parameters': [p for p in parameters if p.get('required')],
            'optional_parameters': [p for p in parameters if not p.get('required')]
        }
    }


def create_due_diligence_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 7 - Due Diligence Questions"""
    section = workbook.get('section_7', {})
    
    questions = []
    if 'questions' in section:
        for question in section['questions']:
            if isinstance(question, dict):
                questions.append({
                    'category': question.get('category', 'General'),
                    'question': question.get('question', ''),
                    'rationale': question.get('why_important', ''),
                    'expected_evidence': question.get('expected_response', ''),
                    'risk_level': question.get('risk_level', 'Medium'),
                    'evaluation_criteria': question.get('evaluation_criteria', [])
                })
    
    return {
        'card_id': 'card_09_due_diligence',
        'card_title': 'Due Diligence Questions',
        'card_type': 'due_diligence',
        'source_section': 'section_7',
        'content': {
            'questions': questions,
            'total_questions': len(questions),
            'categories': list(set([q['category'] for q in questions])),
            'assessment_approach': section.get('assessment_approach', '')
        }
    }


def create_scoring_methodology_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 8 - Scoring Methodology"""
    section = workbook.get('section_8', {})
    
    return {
        'card_id': 'card_10_scoring_methodology',
        'card_title': 'Scoring Methodology',
        'card_type': 'scoring',
        'source_section': 'section_8',
        'content': {
            'methodology': section.get('methodology', ''),
            'dimension_weights': section.get('dimension_weights', {}),
            'scoring_thresholds': section.get('scoring_thresholds', {}),
            'scoring_scale': section.get('scoring_scale', {}),
            'calculation_approach': section.get('calculation_approach', ''),
            'interpretation_guide': section.get('interpretation_guide', {})
        }
    }


def create_sample_scenario_card(workbook: Dict[str, Any]) -> Dict[str, Any]:
    """Create card for Section 9 - Sample Scenario"""
    section = workbook.get('section_9', {})
    
    return {
        'card_id': 'card_11_sample_scenario',
        'card_title': 'Sample Implementation Scenario',
        'card_type': 'scenario',
        'source_section': 'section_9',
        'content': {
            'scenario_name': section.get('scenario_name', 'Sample Scenario'),
            'description': section.get('description', ''),
            'context': section.get('context', {}),
            'requirements': section.get('requirements', []),
            'solution_approach': section.get('solution', ''),
            'implementation_steps': section.get('implementation_steps', []),
            'evaluation_criteria': section.get('evaluation_criteria', []),
            'expected_outcomes': section.get('expected_outcomes', []),
            'lessons_learned': section.get('lessons_learned', [])
        }
    }