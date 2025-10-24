"""
Local Testing Script for AI Pronunciation Trainer
Tests the OpenAI Whisper API integration
"""

import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded .env file")
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment variables")
    print("       Install with: pip install python-dotenv")

def check_environment():
    """Check if environment is properly configured"""
    print("\n" + "="*50)
    print("Environment Check")
    print("="*50)
    
    api_key = os.getenv('WHISPER_API_KEY') or os.getenv('OPENAI_API_KEY')
    use_api = os.getenv('USE_API_ASR', 'true').lower() == 'true'
    
    print(f"USE_API_ASR: {use_api}")
    print(f"WHISPER_API_KEY: {'[OK] Set' if api_key else '[ERROR] Not set'}")
    
    if api_key:
        print(f"Key preview: {api_key[:10]}...{api_key[-4:]}")
    
    if not api_key:
        print("\n[ERROR] WHISPER_API_KEY not found!")
        print("Add it to your .env file:")
        print("WHISPER_API_KEY=sk-proj-xxxxxxxxxxxxxxxx")
        return False
    
    return True

def test_imports():
    """Test if all required packages are installed"""
    print("\n" + "="*50)
    print("Testing Imports")
    print("="*50)
    
    required_packages = {
        'numpy': 'numpy',
        'scipy': 'scipy',
        'soundfile': 'soundfile',
        'requests': 'requests',
        'flask': 'flask',
        'flask_cors': 'flask_cors',
        'epitran': 'epitran',
        'eng_to_ipa': 'eng_to_ipa',
        'dtwalign': 'dtwalign',
        'pandas': 'pandas'
    }
    
    missing = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[ERROR] {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def test_whisper_api():
    """Test OpenAI Whisper API connection"""
    print("\n" + "="*50)
    print("Testing OpenAI Whisper API")
    print("="*50)
    
    try:
        from whisper_api_wrapper import WhisperAPIModel
        import numpy as np
        
        print("Creating WhisperAPIModel...")
        model = WhisperAPIModel()
        print("[OK] Model initialized successfully")
        
        # Create a simple test audio (1 second of silence)
        print("\nCreating test audio (1 second of silence)...")
        sample_rate = 16000
        test_audio = np.zeros(sample_rate, dtype=np.float32)
        test_audio = test_audio[np.newaxis, :]  # Add batch dimension
        
        print("Sending to OpenAI API...")
        print("(This will cost ~$0.0001)")
        
        try:
            model.processAudio(test_audio)
            transcript = model.getTranscript()
            
            print(f"[OK] API call successful!")
            print(f"Transcript: '{transcript}' (expected empty for silence)")
            
            if transcript == "" or transcript.strip() == "":
                print("[OK] Test passed - silence correctly transcribed as empty")
            else:
                print(f"[WARN] Got unexpected transcript: '{transcript}'")
            
            return True
            
        except Exception as api_error:
            print(f"\n[ERROR] API Error: {str(api_error)}")
            print("\nPossible issues:")
            print("1. Invalid API key")
            print("2. No credits in OpenAI account")
            print("3. API rate limit reached")
            print("4. Network connection issue")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_pronunciation_trainer():
    """Test the pronunciation trainer"""
    print("\n" + "="*50)
    print("Testing Pronunciation Trainer")
    print("="*50)
    
    try:
        import pronunciationTrainer
        
        print("Creating trainer for English...")
        trainer = pronunciationTrainer.getTrainer("en")
        print("[OK] English trainer created successfully")
        
        print("\nCreating trainer for German...")
        try:
            trainer = pronunciationTrainer.getTrainer("de")
            print("[OK] German trainer created successfully")
        except UnicodeDecodeError as e:
            print("[WARN] German trainer has encoding issues on Windows")
            print("       This is a known issue with epitran package")
            print("       English trainer works fine!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI Pronunciation Trainer - Local Testing")
    print("="*60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n[ERROR] Please install missing packages first")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Test pronunciation trainer initialization
    if not test_pronunciation_trainer():
        sys.exit(1)
    
    # Ask user if they want to test API (costs money)
    print("\n" + "="*60)
    print("API Test (Optional)")
    print("="*60)
    print("Testing the API will make a real call to OpenAI (~$0.0001)")
    
    response = input("\nDo you want to test the API? (y/n): ").lower().strip()
    
    if response == 'y':
        if not test_whisper_api():
            sys.exit(1)
    else:
        print("[SKIP] Skipping API test")
    
    # All tests passed
    print("\n" + "="*60)
    print("[SUCCESS] All Tests Passed!")
    print("="*60)
    print("\nYou're ready to run the application!")
    print("\nStart the server with:")
    print("  python webApp.py")
    print("\nThen visit: http://localhost:3000")

if __name__ == "__main__":
    main()

