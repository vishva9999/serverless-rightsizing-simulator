# Phase 7 — AWS Production Deployment Guide

## 1. Overview
This document describes the complete AWS Serverless production deployment architecture for the **Serverless Cost & Performance Rightsizing Simulator**.

```
                           ┌───────────────────────────────┐
                           │    React / Vite SPA Client    │
                           │   (S3 Static Web / CloudFront)│
                           └───────────────┬───────────────┘
                                           │
                       ┌───────────────────┴───────────────────┐
                       │                                       │
                       ▼                                       ▼
          ┌─────────────────────────┐             ┌─────────────────────────┐
          │   Amazon Cognito Pool   │             │   Amazon API Gateway    │
          │  (Auth & JWT Issuance)  │             │   (HTTPS, CORS, Proxy)  │
          └─────────────────────────┘             └────────────┬────────────┘
                                                               │
                                                               ▼
                                                  ┌─────────────────────────┐
                                                  │       AWS Lambda        │
                                                  │ (FastAPI App + Mangum)  │
                                                  └────────────┬────────────┘
                                                               │
                              ┌────────────────────────────────┼────────────────────────────────┐
                              ▼                                ▼                                ▼
                  ┌────────────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
                  │   Amazon DynamoDB      │       │       Amazon S3        │       │   Amazon CloudWatch    │
                  │ - Scenarios Table      │       │ - Simulation Artifacts │       │ - Lambda Logs & Errors │
                  │ - History Table        │       │   (Private, Encrypted) │       │ - Metrics & Retention  │
                  └────────────────────────┘       └────────────────────────┘       └────────────────────────┘
```

---

## 2. Prerequisites & Tooling
Before deploying to AWS, ensure the following CLI tools and credentials are configured:
- **AWS CLI** (configured via `aws configure` with valid access keys)
- **AWS SAM CLI** (`sam --version`)
- **Node.js** (v18+ or v22+) & **npm**
- **Python** (3.11, 3.12, or 3.13)

---

## 3. Infrastructure as Code (AWS SAM)
The production infrastructure is defined in [`infrastructure/template.yaml`](file:///e:/Ralle%20Project/serverless-rightsizing-simulator/infrastructure/template.yaml).

### Core Resources:
1. **API Gateway (`RightsizingApiGateway`)**: `AWS::Serverless::Api` with CORS, HTTPS, and Cognito UserPool Authorizer.
2. **Lambda Function (`RightsizingApiFunction`)**: `AWS::Serverless::Function` executing `app.lambda_handler.handler` using the `Mangum` ASGI adapter.
3. **Amazon Cognito (`CognitoUserPool` & `CognitoUserPoolClient`)**: Public SPA client, email-based sign-in, secure password policy.
4. **DynamoDB Tables (`ScenariosTable` & `HistoryTable`)**: `PAY_PER_REQUEST` billing with partition keys and secondary indexes.
5. **Amazon S3 (`SimulationArtifactsBucket`)**: Block Public Access enabled, AES256 server-side encryption.
6. **CloudWatch Logs (`ApiFunctionLogGroup`)**: 30-day retention log group for Lambda.
7. **IAM Execution Role (`SimulatorAppRole`)**: Least-privilege resource policies for DynamoDB, S3, and CloudWatch.

---

## 4. Deployment Steps

### Step A: Build Backend SAM Artifacts
```bash
cd infrastructure
sam build
```

### Step B: Guided SAM Deployment
```bash
sam deploy --guided
```
Prompt responses:
- **Stack Name**: `serverless-rightsizing-simulator`
- **AWS Region**: `ap-south-1` (or your preferred region)
- **Parameter Stage**: `prod`
- **Confirm changes before deploy**: `Y`
- **Allow SAM CLI IAM role creation**: `Y`

### Step C: Note CloudFormation Outputs
After deployment succeeds, note down:
- `ApiUrl`
- `CognitoUserPoolId`
- `CognitoClientId`
- `ScenariosTableName`
- `HistoryTableName`
- `ArtifactsBucketName`

---

## 5. Frontend Production Deployment (S3 + CloudFront)

### Step A: Configure Frontend Environment Variables
In `frontend/.env`:
```env
VITE_AUTH_MODE=cognito
VITE_API_BASE_URL=https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/prod
VITE_COGNITO_USER_POOL_ID=ap-south-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_COGNITO_REGION=ap-south-1
```

### Step B: Build Frontend
```bash
cd frontend
npm run build
```

### Step C: Sync Build to S3 / CloudFront
```bash
aws s3 sync dist/ s3://your-frontend-bucket/ --delete
```

---

## 6. Estimated AWS Cost Considerations
- **Lambda**: Pay-per-use (~$0.20 per 1M invocations, within AWS Free Tier).
- **DynamoDB**: `PAY_PER_REQUEST` (~$0.25 per 1M read units, within AWS Free Tier).
- **Cognito**: 50,000 monthly active users (MAUs) free tier.
- **S3**: Standard storage (~$0.023/GB-month).
- **CloudWatch**: 5GB free ingestion per month.

*Total estimated cost for college/development usage: $0.00 / month (100% Free Tier eligible).*

---

## 7. Cleanup & Resource Teardown
To remove deployed AWS resources when no longer needed:
```bash
sam delete --stack-name serverless-rightsizing-simulator
```
*(Note: Empty the S3 artifacts bucket first before stack deletion).*
