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
2. **dw-cap-transform-gammap** - Transforms workbook to GAMMAP format
3. **dw-cap-save-gammap** - Saves GAMMAP document to S3

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

# Execute Step Functions
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:ap-south-1:863372932275:stateMachine:gammap-generation-pipeline \
  --input '{"workbook_path": "s3://datawhistl/capabilities/output/Data.C4/20240522/workbook_with_section_9.json", "capability_id": "Data.C4"}'
```

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