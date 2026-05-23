# GAMMAP Document Generation Pipeline

AWS Step Functions pipeline that transforms CDP Capability Workbook JSON into GAMMAP assessment methodology documents.

## Architecture

```
Step Functions State Machine:
1. LoadWorkbook → Load workbook from S3
2. TransformToGAMMAP → Transform to GAMMAP format
3. SaveGAMMAP → Save to S3
```

## AWS Resources

- **Region**: ap-south-1
- **S3 Bucket**: datawhistl
- **Lambda Role**: arn:aws:iam::863372932275:role/lambda-execution-role
- **Lambda Layer**: arn:aws:lambda:ap-south-1:863372932275:layer:classifier-complete-deps:1
- **Runtime**: Python 3.11

## Input/Output

### Input
- S3 path to completed workbook: `s3://datawhistl/capabilities/output/{capability_id}/{timestamp}/workbook_with_section_9.json`

### Output
- GAMMAP document: `s3://datawhistl/gammap/output/{capability_id}/{timestamp}/gammap_document.json`

## Lambda Functions

1. **dw-cap-load-workbook** - Loads workbook from S3
   - Validates workbook structure and checks for required sections
   - Handles both `s3://` URL format and plain bucket/key format
   - Returns validation status and workbook data

2. **dw-cap-transform-gammap** - Transforms workbook to GAMMAP format
   - Converts each workbook section into a separate GAMMAP card
   - Handles both list and dictionary formats for all sections
   - Creates 11 cards covering all assessment areas

3. **dw-cap-save-gammap** - Saves GAMMAP document to S3
   - Saves to `s3://datawhistl/gammap/output/{capability_id}/{timestamp}/gammap_document.json`
   - Includes metadata about transformation and source

4. **dw-cap-upload-gamma** - Uploads to Gamma.app (optional)
   - Pushes the GAMMAP document to Gamma.app for presentation generation

## Deployment

```bash
# Deploy Lambda functions
./scripts/deploy.sh

# Create Step Functions state machine
aws stepfunctions create-state-machine \
  --name gammap-generation-pipeline \
  --definition file://stepfunctions/state_machine.json \
  --role-arn arn:aws:iam::863372932275:role/step-functions-role
```

## Testing

```bash
# Test locally
python scripts/local_test.py

# Execute Step Functions using AWS CLI
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:ap-south-1:863372932275:stateMachine:gammap-generation-pipeline \
  --input '{"workbook_path": "s3://datawhistl/capabilities/output/Data.C4/20240522/workbook_with_section_9.json", "capability_id": "Data.C4"}'

# Or use the trigger script (recommended)
python trigger_pipeline.py s3://datawhistl/capabilities/output/Data.C4/20260523_220947/workbook_merged.json
```

### Using the Trigger Script

The `trigger_pipeline.py` script provides an easy way to trigger the pipeline:

```bash
# Usage
python trigger_pipeline.py <s3_workbook_path>

# Example
python trigger_pipeline.py s3://datawhistl/capabilities/output/Data.C4/20260523_220947/workbook_merged.json
```

The script will:
- Automatically extract the capability_id from the S3 path
- Start the Step Functions execution
- Display the execution ARN for tracking
- Show you the AWS CLI command to check status

## GAMMAP Document Structure

```json
{
  "metadata": {...},
  "executive_summary": {...},
  "assessment_framework": {
    "dimensions": [...],
    "scoring_methodology": {...},
    "evaluation_criteria": [...]
  },
  "implementation_guide": {
    "requirements": [...],
    "due_diligence": [...],
    "best_practices": [...],
    "anti_patterns": [...]
  },
  "appendices": {
    "knowledge_requirements": [...],
    "sample_scenarios": [...],
    "glossary": {...}
  }
}
```