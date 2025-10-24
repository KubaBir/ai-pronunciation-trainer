# Serverless Deployment Guide

## Overview

This AI Pronunciation Trainer has been refactored for serverless deployment, specifically optimized for AWS Lambda. The key changes enable:

-   ✅ **No PyTorch** - Removed 800MB+ of dependencies
-   ✅ **API-based Whisper** - Uses external ASR API instead of local models
-   ✅ **Lightweight** - Package size reduced from 1GB+ to ~30-50MB
-   ✅ **Fast Cold Starts** - 1-3 seconds instead of 30+ seconds
-   ✅ **Cost Effective** - Pay only for actual usage

## Architecture

```
API Gateway
    ↓
Lambda: GetAccuracyFromRecordedAudio
    ├── Decode base64 audio
    ├── Resample audio (scipy)
    ├── Call Whisper API (OpenAI/Groq/Deepgram)
    ├── Match words (dtwalign)
    ├── Calculate accuracy (numpy/epitran)
    └── Return pronunciation feedback
```

## Prerequisites

1. **API Key** for one of these providers:

    - [Groq](https://console.groq.com/keys) - Recommended (fastest, cheapest)
    - [OpenAI](https://platform.openai.com/api-keys)
    - [Deepgram](https://console.deepgram.com/)
    - [AssemblyAI](https://www.assemblyai.com/dashboard/)

2. **AWS Account** (for Lambda deployment)

3. **Python 3.9+**

## Local Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# On Linux/Mac
export USE_API_ASR=true
export WHISPER_API_PROVIDER=groq
export WHISPER_API_KEY=your_api_key_here

# On Windows PowerShell
$env:USE_API_ASR="true"
$env:WHISPER_API_PROVIDER="groq"
$env:WHISPER_API_KEY="your_api_key_here"
```

### 3. Run Locally

```bash
python webApp.py
```

Visit http://localhost:3000 to test the application.

## AWS Lambda Deployment

### Option 1: Using AWS SAM (Recommended)

Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: AI Pronunciation Trainer

Globals:
    Function:
        Timeout: 30
        MemorySize: 1024
        Runtime: python3.11

Resources:
    PronunciationTrainerApi:
        Type: AWS::Serverless::Api
        Properties:
            StageName: prod
            Cors:
                AllowMethods: "'GET,POST,OPTIONS'"
                AllowHeaders: "'*'"
                AllowOrigin: "'*'"

    SpeechToScoreFunction:
        Type: AWS::Serverless::Function
        Properties:
            CodeUri: .
            Handler: lambdaSpeechToScore.lambda_handler
            Description: Evaluates pronunciation accuracy
            Environment:
                Variables:
                    USE_API_ASR: true
                    WHISPER_API_PROVIDER: groq
                    WHISPER_API_KEY: !Ref WhisperApiKey
            Events:
                ApiEvent:
                    Type: Api
                    Properties:
                        RestApiId: !Ref PronunciationTrainerApi
                        Path: /GetAccuracyFromRecordedAudio
                        Method: POST

Parameters:
    WhisperApiKey:
        Type: String
        NoEcho: true
        Description: API key for Whisper service

Outputs:
    ApiUrl:
        Description: API Gateway endpoint URL
        Value: !Sub 'https://${PronunciationTrainerApi}.execute-api.${AWS::Region}.amazonaws.com/prod/'
```

Deploy:

```bash
sam build
sam deploy --guided --parameter-overrides WhisperApiKey=your_api_key_here
```

### Option 2: Using AWS Console

1. **Create Lambda Function:**

    - Runtime: Python 3.11
    - Architecture: x86_64
    - Memory: 1024 MB
    - Timeout: 30 seconds

2. **Package and Upload Code:**

```bash
# Create deployment package
pip install -r requirements.txt -t package/
cp *.py package/
cp -r databases package/
cd package
zip -r ../deployment-package.zip .
cd ..
```

3. **Upload** `deployment-package.zip` to Lambda

4. **Set Environment Variables** in Lambda console:

    - `USE_API_ASR`: `true`
    - `WHISPER_API_PROVIDER`: `groq` (or your choice)
    - `WHISPER_API_KEY`: Your actual API key

5. **Create API Gateway** trigger with POST method

### Option 3: Using Serverless Framework

Create `serverless.yml`:

```yaml
service: pronunciation-trainer

provider:
    name: aws
    runtime: python3.11
    stage: prod
    region: us-east-1
    memorySize: 1024
    timeout: 30
    environment:
        USE_API_ASR: true
        WHISPER_API_PROVIDER: groq
        WHISPER_API_KEY: ${env:WHISPER_API_KEY}

functions:
    speechToScore:
        handler: lambdaSpeechToScore.lambda_handler
        events:
            - http:
                  path: GetAccuracyFromRecordedAudio
                  method: post
                  cors: true

plugins:
    - serverless-python-requirements

custom:
    pythonRequirements:
        dockerizePip: true
        zip: true
```

Deploy:

```bash
npm install -g serverless
npm install --save-dev serverless-python-requirements
serverless deploy
```

## Configuration

### API Provider Selection

Choose based on your needs:

| Provider       | Speed       | Cost/min | Accuracy  | Best For                 |
| -------------- | ----------- | -------- | --------- | ------------------------ |
| **Groq**       | ⚡⚡⚡ Fast | $0.0001  | Very Good | Production (recommended) |
| **OpenAI**     | ⚡⚡ Medium | $0.006   | Excellent | High accuracy needed     |
| **Deepgram**   | ⚡⚡⚡ Fast | $0.0043  | Very Good | Real-time applications   |
| **AssemblyAI** | ⚡⚡ Medium | $0.015   | Very Good | Feature-rich needs       |

### Memory & Timeout Settings

Recommended Lambda configuration:

-   **Memory**: 1024 MB (minimum 512 MB)
-   **Timeout**: 30 seconds (typical: 5-15s for 30s audio)
-   **Architecture**: x86_64
-   **Runtime**: Python 3.11 or 3.9

### Cost Estimation

For 10,000 requests/month with 30-second audio clips:

**Lambda Costs:**

-   Compute: ~$2-3/month (1024MB, 10s avg execution)
-   Requests: ~$0.20/month

**API Costs (for 5,000 minutes of audio):**

-   Groq: $0.50/month ⭐ **Cheapest**
-   OpenAI: $30/month
-   Deepgram: $21.50/month
-   AssemblyAI: $75/month

**Total**: $2.50-$78/month depending on provider

## Testing the API

### Using curl:

```bash
curl -X POST https://your-api-gateway-url/GetAccuracyFromRecordedAudio \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello world",
    "base64Audio": "data:audio/ogg;base64,T2dnUw...",
    "language": "en"
  }'
```

### Expected Response:

```json
{
    "real_transcript": "Hello world",
    "ipa_transcript": "həˈloʊ wɜrld",
    "pronunciation_accuracy": "95",
    "real_transcripts": "Hello world",
    "matched_transcripts": "Hello world",
    "pair_accuracy_category": "0 0",
    "start_time": "0.0 0.5",
    "end_time": "0.4 0.9"
}
```

## Monitoring

### CloudWatch Metrics to Watch:

-   **Duration**: Should be 3-15 seconds typically
-   **Memory Used**: Should be 200-500 MB
-   **Errors**: API timeout, API key issues
-   **Cold Starts**: Should be <3 seconds

### Common Errors:

1. **"WHISPER_API_KEY environment variable must be set"**

    - Solution: Set the environment variable in Lambda

2. **"API Error: 401"**

    - Solution: Check your API key is valid

3. **"Timeout after 30 seconds"**

    - Solution: Increase Lambda timeout or optimize audio length

4. **Import errors for torch/torchaudio**
    - Solution: Make sure you're using the new requirements.txt

## Reverting to Local Models

If you need to run with local PyTorch models:

1. Uncomment PyTorch dependencies in `requirements.txt`
2. Set `USE_API_ASR=false` in environment
3. Note: Not suitable for Lambda (exceeds size limits)

## Frontend Integration

Update your frontend JavaScript to point to the new Lambda URL:

```javascript
const API_URL = 'https://your-api-gateway-url.amazonaws.com/prod';

async function evaluatePronunciation(audioBlob, text, language) {
    const base64Audio = await blobToBase64(audioBlob);

    const response = await fetch(`${API_URL}/GetAccuracyFromRecordedAudio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: text,
            base64Audio: base64Audio,
            language: language,
        }),
    });

    return await response.json();
}
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use AWS Secrets Manager** for production API keys
3. **Enable API Gateway rate limiting** to prevent abuse
4. **Add authentication** to your API Gateway
5. **Enable CloudWatch logging** for debugging

## Troubleshooting

### Issue: Package too large for Lambda

**Solution**: Make sure you're using the new lightweight `requirements.txt` without PyTorch.

### Issue: Cold starts are slow

**Solutions**:

-   Use Lambda provisioned concurrency
-   Choose Groq API (fastest)
-   Reduce memory if <200MB is being used

### Issue: API rate limits hit

**Solutions**:

-   Implement request queuing
-   Add retry logic with exponential backoff
-   Contact provider for higher limits

## Support

For issues or questions:

1. Check CloudWatch logs for errors
2. Verify environment variables are set correctly
3. Test API key with provider's documentation
4. Review this guide's troubleshooting section

## Next Steps

-   [ ] Deploy to Lambda using one of the methods above
-   [ ] Test with your actual audio files
-   [ ] Set up CloudWatch alarms for errors
-   [ ] Configure API Gateway custom domain
-   [ ] Add authentication/authorization
-   [ ] Set up CI/CD pipeline for updates
