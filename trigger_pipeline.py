#!/usr/bin/env python3
"""
Script to trigger the GAMMAP generation pipeline with a workbook file.
Usage: python trigger_pipeline.py <workbook_s3_path>
"""
import sys
import json
import boto3
from datetime import datetime

def trigger_pipeline(workbook_path):
    """Trigger the GAMMAP generation pipeline with the given workbook."""
    
    # Initialize AWS clients
    stepfunctions = boto3.client('stepfunctions', region_name='ap-south-1')
    
    # State machine ARN
    state_machine_arn = 'arn:aws:states:ap-south-1:863372932275:stateMachine:gammap-generation-pipeline'
    
    # Extract capability_id from the path
    # Expected format: s3://datawhistl/capabilities/output/{capability_id}/{timestamp}/filename.json
    path_parts = workbook_path.replace('s3://', '').split('/')
    capability_id = None
    if len(path_parts) >= 5 and path_parts[2] == 'output':
        capability_id = path_parts[3]  # This will be like 'Data.C4'
    
    # Prepare input
    input_data = {
        "workbook_path": workbook_path,
        "capability_id": capability_id or "unknown"
    }
    
    # Start execution
    execution_name = f"gammap-gen-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"Starting pipeline execution: {execution_name}")
    print(f"Input workbook: {workbook_path}")
    print(f"Capability ID: {input_data['capability_id']}")
    
    response = stepfunctions.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(input_data)
    )
    
    print(f"Execution started successfully!")
    print(f"Execution ARN: {response['executionArn']}")
    print(f"Started at: {response['startDate']}")
    
    # Return execution ARN for tracking
    return response['executionArn']

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to the file you specified
        workbook_path = "s3://datawhistl/capabilities/output/Data.C4/20260522_083141/workbook_with_section_9_with_section_9_with_section_9.json"
        print(f"No workbook path provided. Using default: {workbook_path}")
    else:
        workbook_path = sys.argv[1]
    
    try:
        execution_arn = trigger_pipeline(workbook_path)
        print("\n✓ Pipeline triggered successfully!")
        print(f"\nTo check status, run:")
        print(f"aws stepfunctions describe-execution --execution-arn {execution_arn} --region ap-south-1")
    except Exception as e:
        print(f"\n✗ Error triggering pipeline: {str(e)}")
        sys.exit(1)