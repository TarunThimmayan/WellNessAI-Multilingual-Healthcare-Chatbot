#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test OpenAI Model for Multilingual Detection and Translation
Tests language detection and translation from 5 Indic languages to English
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIError, AuthenticationError, RateLimitError

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from tabulate import tabulate as tabulate_func
except ImportError:
    print("[ERROR] 'tabulate' package is required. Install with: pip install tabulate")
    sys.exit(1)

# Test data: {language_code: [(input_text, expected_english), ...]}
TEST_DATA = {
    "ta": [  # Tamil
        ("naa toongitan", "I slept"),
        ("enakku pasikuduthu", "I am hungry"),
        ("nee epdi iruka?", "How are you?"),
        ("naan velaila poren", "I am going to work"),
        ("indha paatu romba nalla iruku", "This song is really good"),
    ],
    "ml": [  # Malayalam
        ("njan kazhichu", "I ate"),
        ("ninakku sukhamano?", "Are you fine?"),
        ("ente peru anu rahul", "My name is Rahul"),
        ("njan veettil aanu", "I am at home"),
        ("ithu nalla pusthakam aanu", "This is a good book"),
    ],
    "hi": [  # Hindi
        ("main thak gaya hoon", "I am tired"),
        ("tum kahan ja rahe ho?", "Where are you going?"),
        ("mujhe bhook lagi hai", "I am hungry"),
        ("aaj mausam bahut accha hai", "The weather is very nice today"),
        ("mujhe yeh pasand hai", "I like this"),
    ],
    "kn": [  # Kannada
        ("nanu oota maadide", "I have eaten"),
        ("neenu hegiddiya?", "How are you?"),
        ("nan hesaru praveen", "My name is Praveen"),
        ("nanu kelasa ge hogtha idini", "I am going to work"),
        ("ee haadu tumba chennagide", "This song is very nice"),
    ],
    "te": [  # Telugu
        ("nenu tinanu", "I ate"),
        ("nee peru emiti?", "What is your name?"),
        ("nenu baagunnanu", "I am fine"),
        ("idi chala manchidi", "This is very good"),
        ("nenu intiki veltunna", "I am going home"),
    ],
}

# Language names mapping (using English names to avoid Unicode issues in Windows console)
LANGUAGE_NAMES = {
    "ta": "Tamil",
    "ml": "Malayalam",
    "hi": "Hindi",
    "kn": "Kannada",
    "te": "Telugu",
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


def detect_language(client: OpenAI, model: str, text: str, retry_count: int = 3) -> str:
    """Detect the language of the given text with rate limiting."""
    for attempt in range(retry_count):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection expert. Identify the language of the given text. "
                        "Respond with ONLY the ISO 639-1 language code (e.g., 'ta' for Tamil, 'ml' for Malayalam, "
                        "'hi' for Hindi, 'kn' for Kannada, 'te' for Telugu, 'en' for English). "
                        "Do not include any explanation, just the language code."
                    },
                    {
                        "role": "user",
                        "content": f"Detect the language of this text: {text}"
                    }
                ],
                max_tokens=10,
                temperature=0.1,
            )
            
            detected = response.choices[0].message.content.strip().lower()
            # Clean up response (remove quotes, periods, etc.)
            detected = detected.replace('"', '').replace("'", '').replace('.', '').strip()
            return detected
        except RateLimitError as e:
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                print(f"    [Rate limit hit, waiting {wait_time}s before retry...]")
                time.sleep(wait_time)
            else:
                return f"RATE_LIMIT_ERROR"
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(1)
            else:
                return f"ERROR: {str(e)[:30]}"
    
    return "ERROR: Max retries exceeded"


def translate_to_english(client: OpenAI, model: str, text: str, detected_lang: str, retry_count: int = 3) -> str:
    """Translate the given text to English with rate limiting."""
    for attempt in range(retry_count):
        try:
            # Map language codes to full names for better context
            lang_names = {
                "ta": "Tamil",
                "ml": "Malayalam",
                "hi": "Hindi",
                "kn": "Kannada",
                "te": "Telugu",
            }
            
            lang_name = lang_names.get(detected_lang, detected_lang)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following {lang_name} text to English. "
                        "Provide only the translation, no explanations. Keep it natural and accurate."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=100,
                temperature=0.3,
            )
            
            translated = response.choices[0].message.content.strip()
            return translated
        except RateLimitError as e:
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                print(f"    [Rate limit hit, waiting {wait_time}s before retry...]")
                time.sleep(wait_time)
            else:
                return f"RATE_LIMIT_ERROR"
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(1)
            else:
                return f"ERROR: {str(e)[:30]}"
    
    return "ERROR: Max retries exceeded"


def test_multilingual_capabilities():
    """Test language detection and translation for all test cases."""
    print("=" * 80)
    print("OpenAI Multilingual Detection & Translation Test")
    print("=" * 80)
    print()
    
    # Load environment
    load_environment()
    
    # Get API key and model
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables")
        return False
    
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
    print(f"[INFO] Using model: {model}")
    print(f"[INFO] API Key: {api_key[:7]}...{api_key[-4:]}")
    print()
    
    # Initialize client
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] OpenAI client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize client: {e}")
        return False
    
    # Prepare results table
    results = []
    test_number = 1
    total_tests = sum(len(cases) for cases in TEST_DATA.values())
    
    print(f"\n[INFO] Running {total_tests} test cases...")
    print(f"[INFO] Rate limiting: 0.5s delay between API calls to avoid rate limits")
    print(f"[INFO] Estimated time: ~{total_tests * 2 * 0.5 / 60:.1f} minutes")
    print("-" * 80)
    
    # Test each language
    for lang_code, test_cases in TEST_DATA.items():
        lang_name = LANGUAGE_NAMES[lang_code]
        print(f"\nTesting {lang_name} ({lang_code})...")
        
        for idx, (input_text, expected_english) in enumerate(test_cases, 1):
            print(f"  [{idx}/{len(test_cases)}] Testing: '{input_text}'")
            
            # Step 1: Detect language
            detected_lang = detect_language(client, model, input_text)
            
            # Add delay between API calls to avoid rate limiting (0.5 seconds)
            time.sleep(0.5)
            
            # Step 2: Translate to English
            translated_english = translate_to_english(client, model, input_text, detected_lang)
            
            # Add delay after translation (0.5 seconds)
            time.sleep(0.5)
            
            # Check if detection is correct
            detection_correct = (detected_lang == lang_code)
            
            # Check if translation matches (case-insensitive, allow minor variations)
            translation_match = False
            if translated_english and not translated_english.startswith("ERROR"):
                # Normalize for comparison (lowercase, remove punctuation)
                expected_norm = expected_english.lower().strip('.,!?')
                translated_norm = translated_english.lower().strip('.,!?')
                # Check if expected is contained in translated or vice versa
                translation_match = (
                    expected_norm in translated_norm or 
                    translated_norm in expected_norm or
                    expected_norm == translated_norm
                )
            
            # Add to results
            results.append({
                "sno": test_number,
                "expected_lang": lang_name,
                "input_text": input_text,
                "expected_english": expected_english,
                "detected_lang": detected_lang,
                "translated_english": translated_english,
                "detection_correct": detection_correct,
                "translation_match": translation_match,
            })
            
            test_number += 1
    
    # Display results in table format
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print()
    
    # Prepare table data
    table_data = []
    for result in results:
        table_data.append([
            result["sno"],
            result["expected_lang"],
            result["input_text"],
            result["expected_english"],
            result["detected_lang"],
            result["translated_english"],
        ])
    
    # Create table
    headers = [
        "S.No",
        "Expected Lang",
        "Input Text",
        "Expected English",
        "Detected Lang",
        "Translated English"
    ]
    
    print(tabulate_func(table_data, headers=headers, tablefmt="grid", maxcolwidths=[5, 25, 30, 30, 15, 30]))
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    total = len(results)
    correct_detections = sum(1 for r in results if r["detection_correct"])
    correct_translations = sum(1 for r in results if r["translation_match"])
    
    detection_accuracy = (correct_detections / total * 100) if total > 0 else 0
    translation_accuracy = (correct_translations / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tests: {total}")
    print(f"Language Detection Accuracy: {correct_detections}/{total} ({detection_accuracy:.1f}%)")
    print(f"Translation Accuracy: {correct_translations}/{total} ({translation_accuracy:.1f}%)")
    
    # Breakdown by language
    print("\nBreakdown by Language:")
    print("-" * 80)
    for lang_code, lang_name in LANGUAGE_NAMES.items():
        lang_results = [r for r in results if r["expected_lang"] == lang_name]
        if lang_results:
            lang_total = len(lang_results)
            lang_detections = sum(1 for r in lang_results if r["detection_correct"])
            lang_translations = sum(1 for r in lang_results if r["translation_match"])
            print(f"{lang_name}:")
            print(f"  Detection: {lang_detections}/{lang_total} ({lang_detections/lang_total*100:.1f}%)")
            print(f"  Translation: {lang_translations}/{lang_total} ({lang_translations/lang_total*100:.1f}%)")
    
    # Final verdict
    print("\n" + "=" * 80)
    if detection_accuracy >= 90 and translation_accuracy >= 80:
        print("[SUCCESS] Model shows EXCELLENT multilingual support!")
    elif detection_accuracy >= 70 and translation_accuracy >= 60:
        print("[GOOD] Model shows GOOD multilingual support.")
    else:
        print("[WARNING] Model has LIMITED multilingual support.")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        # Check if tabulate is installed
        try:
            import tabulate
        except ImportError:
            print("[ERROR] 'tabulate' package is required for table formatting")
            print("Install it with: pip install tabulate")
            sys.exit(1)
        
        success = test_multilingual_capabilities()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

