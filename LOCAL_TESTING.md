# Local Testing Guide

## Quick Start

### 1. Create your `.env` file

Create a file named `.env` in the project root with the following content:

```bash
# Required: Your OpenAI API key
WHISPER_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Use API mode (default is true)
USE_API_ASR=true
```

**Get your OpenAI API key at:** https://platform.openai.com/api-keys

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

-   Core packages (numpy, scipy, soundfile, etc.)
-   API tools (requests)
-   Web framework (Flask)
-   **python-dotenv** (for loading .env files)

### 3. Test Your Setup

Run the test script to verify everything is configured correctly:

```bash
python test_local.py
```

This will:

-   ✅ Check if .env file is loaded
-   ✅ Verify API key is set
-   ✅ Test all package imports
-   ✅ Initialize pronunciation trainers
-   ✅ Optionally test OpenAI API connection (~$0.0001 cost)

### 4. Run the Application

#### Option A: Using the helper script (recommended)

```bash
python run_local.py
```

#### Option B: Direct run

```bash
python webApp.py
```

Both methods will:

-   Load your .env file automatically
-   Start the Flask server on http://localhost:3000
-   Open your default browser

### 5. Test the Application

Visit **http://localhost:3000** and:

1. Select a language (English or German)
2. Click to get a sample sentence
3. Record your pronunciation
4. Get instant feedback!

## Troubleshooting

### Error: "WHISPER_API_KEY not found"

**Solution:** Make sure your `.env` file exists and contains:

```bash
WHISPER_API_KEY=sk-proj-your-key-here
```

### Error: "No module named 'dotenv'"

**Solution:** Install python-dotenv:

```bash
pip install python-dotenv
```

### Error: "Import could not be resolved"

**Solution:** Install all requirements:

```bash
pip install -r requirements.txt
```

### Error: "OpenAI API Error: 401"

**Causes:**

1. Invalid API key - Check your key at https://platform.openai.com/api-keys
2. Expired key - Create a new one
3. No credits - Add credits at https://platform.openai.com/account/billing

**Solution:** Update your .env file with a valid key.

### Error: "OpenAI API Error: 429"

**Cause:** Rate limit reached

**Solution:** Wait a moment and try again, or upgrade your OpenAI plan.

### Port 3000 already in use

**Solution:** The app will show an error. Either:

1. Stop the other application using port 3000, or
2. Edit `webApp.py` and change the port number:
    ```python
    app.run(host="0.0.0.0", port=3001)  # Use 3001 instead
    ```

## Testing Components Individually

### Test API Connection Only

```python
from whisper_api_wrapper import WhisperAPIModel
import numpy as np

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Create model
model = WhisperAPIModel()

# Test with silence
audio = np.zeros((1, 16000), dtype=np.float32)
model.processAudio(audio)
print(f"Transcript: '{model.getTranscript()}'")
```

### Test Pronunciation Trainer Only

```python
import pronunciationTrainer
from dotenv import load_dotenv
load_dotenv()

# Create trainer
trainer = pronunciationTrainer.getTrainer("en", use_api=True)
print("✅ Trainer created successfully")
```

### Test Full Pipeline

```python
import numpy as np
import pronunciationTrainer
from dotenv import load_dotenv
load_dotenv()

# Create trainer
trainer = pronunciationTrainer.getTrainer("en", use_api=True)

# Create test audio (1 second of silence)
audio = np.zeros((1, 16000), dtype=np.float32)

# Process
result = trainer.processAudioForGivenText(audio, "hello world")
print(f"Accuracy: {result['pronunciation_accuracy']}%")
```

## Environment Variables Reference

| Variable          | Required | Default                     | Description                     |
| ----------------- | -------- | --------------------------- | ------------------------------- |
| `WHISPER_API_KEY` | ✅ Yes   | None                        | Your OpenAI API key             |
| `USE_API_ASR`     | No       | `true`                      | Use API mode (vs local PyTorch) |
| `OPENAI_API_KEY`  | No       | None                        | Alternative name for API key    |
| `OPENAI_API_BASE` | No       | `https://api.openai.com/v1` | Custom API endpoint             |

## Cost Tracking

Each pronunciation evaluation:

-   ~30 seconds of audio
-   Cost: ~$0.003 (0.5 minutes × $0.006/min)

To track your usage:

1. Visit: https://platform.openai.com/usage
2. Filter by "Whisper API"
3. Monitor daily spend

## Performance Expectations (Local)

| Metric               | Value                    |
| -------------------- | ------------------------ |
| Server startup       | 1-2 seconds              |
| First API call       | 2-4 seconds (cold start) |
| Subsequent calls     | 1-2 seconds              |
| Audio processing     | 0.5-1 second             |
| Total per evaluation | 2-5 seconds              |

## Development Tips

### 1. Enable Debug Mode

Edit `webApp.py`:

```python
app.run(host="0.0.0.0", port=3000, debug=True)
```

This enables:

-   Auto-reload on code changes
-   Better error messages
-   Debug toolbar

### 2. Test with Different Audio Files

```python
import soundfile as sf
import pronunciationTrainer
from dotenv import load_dotenv
load_dotenv()

# Load your audio file
audio, sr = sf.read('your_audio.wav')

# Resample if needed
if sr != 16000:
    from scipy import signal
    audio = signal.resample(audio, int(len(audio) * 16000 / sr))

# Process
trainer = pronunciationTrainer.getTrainer("en", use_api=True)
audio = audio[np.newaxis, :]  # Add batch dimension
result = trainer.processAudioForGivenText(audio, "your expected text")
print(result)
```

### 3. Mock API for Testing (No Cost)

Create a mock for testing without API calls:

```python
# test_mock.py
import os
os.environ['USE_API_ASR'] = 'false'  # Use local model instead

# Now import and test
import pronunciationTrainer
trainer = pronunciationTrainer.getTrainer("en", use_api=False)
```

Note: This requires PyTorch to be installed (see requirements.txt comments).

## Next Steps

Once local testing works:

1. **Deploy to AWS Lambda:**

    ```bash
    sam build
    sam deploy --guided
    ```

2. **Set up CI/CD** for automatic deployments

3. **Add custom domain** to your API Gateway

4. **Monitor costs** in AWS Billing Dashboard

## Need Help?

1. Check `DEPLOYMENT.md` for deployment guide
2. Check `QUICK_START.md` for 5-minute setup
3. Review `SERVERLESS_CHANGES.md` for architecture details
4. Open an issue on GitHub

---

**Happy Testing! 🎉**
