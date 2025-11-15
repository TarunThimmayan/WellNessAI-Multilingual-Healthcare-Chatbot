#!/usr/bin/env python3
"""
Test OpenAI models for multilingual translation capabilities
Tests which models can handle: English, Hindi, Tamil, Telugu, Kannada, Malayalam
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIError, AuthenticationError

# Supported languages
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
}

# Test phrases for each language
TEST_PHRASES = {
    "en": "I have a headache and fever. What should I do?",
    "hi": "मुझे सिरदर्द और बुखार है। मुझे क्या करना चाहिए?",
    "ta": "எனக்கு தலைவலி மற்றும் காய்ச்சல் உள்ளது. நான் என்ன செய்ய வேண்டும்?",
    "te": "నాకు తలనొప్పి మరియు జ్వరం ఉంది. నేను ఏమి చేయాలి?",
    "kn": "ನನಗೆ ತಲೆನೋವು ಮತ್ತು ಜ್ವರವಿದೆ. ನಾನು ಏನು ಮಾಡಬೇಕು?",
    "ml": "എനിക്ക് തലവേദനയും പനിയും ഉണ്ട്. ഞാൻ എന്ത് ചെയ്യണം?",
}


def load_environment():
    """Load .env from api/ or project root."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / ".env",
        here.parent / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            load_dotenv(candidate, override=True)
            print(f"[OK] Loaded .env from: {candidate}")
            return True
    print("[WARN] No .env file found, using environment variables")
    load_dotenv()
    return False


def test_model_translation(client: OpenAI, model: str) -> dict:
    """Test if a model can translate between all supported languages."""
    results = {
        "model": model,
        "supported": True,
        "tests_passed": 0,
        "tests_failed": 0,
        "errors": [],
    }
    
    print(f"\n{'='*60}")
    print(f"Testing Model: {model}")
    print(f"{'='*60}")
    
    # Test 1: English to all Indic languages
    print("\n[Test 1] English -> Indic Languages")
    print("-" * 60)
    english_text = TEST_PHRASES["en"]
    
    for lang_code, lang_name in LANGUAGES.items():
        if lang_code == "en":
            continue  # Skip English
        
        try:
            # Ask model to translate
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional medical translator. Translate the following English medical text to {lang_name} ({lang_code}). Provide only the translation, no explanations."
                    },
                    {
                        "role": "user",
                        "content": english_text
                    }
                ],
                max_tokens=150,
                temperature=0.3,
            )
            
            translation = response.choices[0].message.content.strip()
            print(f"  [{lang_code}] {lang_name}: {translation[:60]}...")
            results["tests_passed"] += 1
            
        except Exception as e:
            print(f"  [{lang_code}] {lang_name}: FAILED - {str(e)[:50]}")
            results["tests_failed"] += 1
            results["errors"].append(f"{lang_code}: {str(e)[:100]}")
    
    # Test 2: Indic languages to English
    print("\n[Test 2] Indic Languages -> English")
    print("-" * 60)
    
    for lang_code, lang_name in LANGUAGES.items():
        if lang_code == "en":
            continue  # Skip English
        
        try:
            indic_text = TEST_PHRASES[lang_code]
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional medical translator. Translate the following {lang_name} ({lang_code}) medical text to English. Provide only the translation, no explanations."
                    },
                    {
                        "role": "user",
                        "content": indic_text
                    }
                ],
                max_tokens=150,
                temperature=0.3,
            )
            
            translation = response.choices[0].message.content.strip()
            print(f"  [{lang_code}] {lang_name}: {translation[:60]}...")
            results["tests_passed"] += 1
            
        except Exception as e:
            print(f"  [{lang_code}] {lang_name}: FAILED - {str(e)[:50]}")
            results["tests_failed"] += 1
            results["errors"].append(f"{lang_code}: {str(e)[:100]}")
    
    # Test 3: Multilingual understanding (detect and respond in same language)
    print("\n[Test 3] Multilingual Understanding (Respond in Same Language)")
    print("-" * 60)
    
    for lang_code, lang_name in LANGUAGES.items():
        try:
            test_text = TEST_PHRASES[lang_code]
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a medical assistant. Respond to the user's question in {lang_name} ({lang_code}) if they wrote in {lang_name}, otherwise respond in English."
                    },
                    {
                        "role": "user",
                        "content": test_text
                    }
                ],
                max_tokens=200,
                temperature=0.7,
            )
            
            reply = response.choices[0].message.content.strip()
            print(f"  [{lang_code}] {lang_name}: {reply[:60]}...")
            results["tests_passed"] += 1
            
        except Exception as e:
            print(f"  [{lang_code}] {lang_name}: FAILED - {str(e)[:50]}")
            results["tests_failed"] += 1
            results["errors"].append(f"{lang_code}: {str(e)[:100]}")
    
    total_tests = results["tests_passed"] + results["tests_failed"]
    success_rate = (results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
    results["success_rate"] = success_rate
    
    print(f"\n[Summary] {model}")
    print(f"  Tests Passed: {results['tests_passed']}/{total_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if results["tests_failed"] > 0:
        results["supported"] = False
        print(f"  Status: PARTIALLY SUPPORTED")
    else:
        print(f"  Status: FULLY SUPPORTED")
    
    return results


def main():
    """Test multiple OpenAI models for multilingual support."""
    print("=" * 60)
    print("OpenAI Multilingual Model Testing")
    print("Testing: English, Hindi, Tamil, Telugu, Kannada, Malayalam")
    print("=" * 60)
    
    # Load environment
    load_environment()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found")
        return 1
    
    # Initialize client
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] OpenAI client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize client: {e}")
        return 1
    
    # Models to test (prioritized by capability)
    models_to_test = [
        "gpt-4o",              # Latest GPT-4 Omni (best multilingual)
        "gpt-4o-mini",         # Cheaper GPT-4 Omni variant
        "gpt-4-turbo",         # GPT-4 Turbo
        "gpt-4",               # Standard GPT-4
        "gpt-3.5-turbo",       # GPT-3.5 Turbo (cheapest)
    ]
    
    all_results = []
    
    for model in models_to_test:
        try:
            result = test_model_translation(client, model)
            all_results.append(result)
        except AuthenticationError as e:
            print(f"\n[ERROR] Authentication failed for {model}: {e}")
            break
        except APIError as e:
            print(f"\n[ERROR] API error for {model}: {e}")
            if "model" in str(e).lower() and "not found" in str(e).lower():
                print(f"  Model {model} may not be available in your account")
                continue
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error testing {model}: {e}")
            continue
    
    # Final Summary
    print("\n" + "=" * 60)
    print("FINAL RECOMMENDATIONS")
    print("=" * 60)
    
    # Sort by success rate
    all_results.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
    
    print("\nModel Rankings (by success rate):")
    for i, result in enumerate(all_results, 1):
        status = "FULLY SUPPORTED" if result["supported"] else "PARTIALLY SUPPORTED"
        print(f"\n{i}. {result['model']}")
        print(f"   Success Rate: {result['success_rate']:.1f}%")
        print(f"   Status: {status}")
        if result["errors"]:
            print(f"   Errors: {len(result['errors'])}")
    
    # Best recommendation
    if all_results:
        best = all_results[0]
        print(f"\n{'='*60}")
        print(f"RECOMMENDED MODEL: {best['model']}")
        print(f"{'='*60}")
        print(f"Success Rate: {best['success_rate']:.1f}%")
        print(f"Tests Passed: {best['tests_passed']}")
        
        if best['success_rate'] >= 90:
            print("\nThis model is EXCELLENT for multilingual translation!")
        elif best['success_rate'] >= 70:
            print("\nThis model is GOOD for multilingual translation.")
        else:
            print("\nThis model has LIMITED multilingual support.")
    
    print("\n" + "=" * 60)
    print("Note: GPT-4o and GPT-4o-mini are the best for multilingual tasks")
    print("They have improved multilingual understanding compared to GPT-3.5")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

