# CLAUDE.md - Project Instructions for AI Assistant

## Project Overview
This is a GAMMAP Document Generation Pipeline that transforms CDP Capability Workbook JSON documents into professional GAMMAP assessment methodology documents using AWS Step Functions and Lambda.

## Current Implementation Status
✅ Basic pipeline structure created
✅ Three Lambda functions for load, transform, and save operations
✅ Step Functions state machine definition
✅ No AI/ML components - pure JSON transformation

## Project Structure
```
gamma-pipeline/
├── src/
│   ├── lambdas/         # Lambda functions
│   │   ├── load_workbook.py
│   │   ├── transform_to_gammap.py
│   │   └── save_gammap.py
│   └── utils/           # Utilities
│       └── s3_helpers.py
├── stepfunctions/       # State machine definitions
│   └── state_machine.json
├── sample_data/         # Test data
├── scripts/            # Deployment scripts
└── tests/              # Test files
```

## Key AWS Resources
- **Region**: ap-south-1
- **S3 Bucket**: datawhistl
- **Lambda Role**: arn:aws:iam::863372932275:role/lambda-execution-role
- **Lambda Layer**: arn:aws:lambda:ap-south-1:863372932275:layer:classifier-complete-deps:1

## Lambda Functions

### 1. load_workbook.py
- Loads workbook JSON from S3
- Handles both `s3://bucket/key` and `bucket/key` formats
- Extracts capability_id from path or event

### 2. transform_to_gammap.py
- Core transformation logic
- Maps workbook sections to GAMMAP structure:
  - section_0a/0b → executive_summary
  - section_1/2/8 → assessment_framework
  - section_3_4/6/7 → implementation_guide
  - section_5/9 → appendices

### 3. save_gammap.py
- Saves GAMMAP document to S3
- Path: `s3://datawhistl/gammap/output/{capability_id}/{timestamp}/gammap_document.json`

## Testing Instructions
```bash
# Run local test
python scripts/local_test.py

# Test individual Lambda locally
python -c "from src.lambdas.load_workbook import lambda_handler; print(lambda_handler({'workbook_path': 's3://...'}, None))"
```

## Deployment Instructions
```bash
# Package Lambda functions
cd src/lambdas
zip -r ../../load_workbook.zip load_workbook.py
zip -r ../../transform_to_gammap.zip transform_to_gammap.py
zip -r ../../save_gammap.zip save_gammap.py

# Deploy to AWS Lambda
aws lambda create-function \
  --function-name dw-cap-load-workbook \
  --runtime python3.11 \
  --role arn:aws:iam::863372932275:role/lambda-execution-role \
  --handler load_workbook.lambda_handler \
  --zip-file fileb://load_workbook.zip \
  --region ap-south-1

# Create Step Functions state machine
aws stepfunctions create-state-machine \
  --name gammap-generation-pipeline \
  --definition file://stepfunctions/state_machine.json \
  --role-arn arn:aws:iam::863372932275:role/step-functions-role \
  --region ap-south-1
```

## Future Enhancements (Not Yet Implemented)
- [ ] LangGraph integration for AI-powered generation
- [ ] PDF generation
- [ ] HTML formatting
- [ ] Email delivery
- [ ] Version tracking
- [ ] Diff generation between versions

## Important Notes
1. **No AI Components**: Current implementation is pure JSON transformation
2. **Error Handling**: All Lambda functions include retry logic and error handling
3. **Logging**: Uses AWS CloudWatch for logging
4. **S3 Paths**: Supports both `s3://` and plain bucket/key formats

## Common Commands
```bash
# View Step Functions execution
aws stepfunctions describe-execution \
  --execution-arn arn:aws:states:ap-south-1:863372932275:execution:gammap-generation-pipeline:exec-id

# Check Lambda logs
aws logs tail /aws/lambda/dw-cap-load-workbook --follow

# List generated GAMMAP documents
aws s3 ls s3://datawhistl/gammap/output/ --recursive
```

## Troubleshooting
1. **S3 Access Issues**: Ensure Lambda role has S3 read/write permissions
2. **Missing Sections**: Transform function handles missing sections gracefully
3. **Path Parsing**: Both S3 URL formats are supported

## Contact
For issues or questions about the original workbook generator pipeline, refer to the CDP Capability Workbook Generator documentation.