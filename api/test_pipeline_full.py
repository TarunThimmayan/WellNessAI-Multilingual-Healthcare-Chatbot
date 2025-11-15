#!/usr/bin/env python3
"""
Test the complete multilingual healthcare chatbot pipeline
Shows detailed output at each stage
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Fix import path issues
api_dir = Path(__file__).parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

# Change to api directory for imports
original_cwd = os.getcwd()
os.chdir(str(api_dir))

try:
    # Import pipeline functions
    import pipeline_functions
    from pipeline_functions import (
        detect_and_translate_to_english,
        generate_final_answer,
        translate_to_user_language,
    )
    
    # Import other modules (with error handling)
    try:
        from rag.retriever import retrieve
    except ImportError as e:
        print(f"[WARN] Could not import rag.retriever: {e}")
        retrieve = lambda q, k=4: []
    
    try:
        from router import is_graph_intent, extract_city
    except ImportError as e:
        print(f"[WARN] Could not import router: {e}")
        is_graph_intent = lambda x: False
        extract_city = lambda x: None
    
    try:
        from safety import detect_red_flags, extract_symptoms, detect_mental_health_crisis, detect_pregnancy_emergency
    except ImportError as e:
        print(f"[WARN] Could not import safety: {e}")
        detect_red_flags = lambda x, y: {"red_flag": False, "matched": []}
        extract_symptoms = lambda x: []
        detect_mental_health_crisis = lambda x, y: {"crisis": False, "matched": [], "first_aid": []}
        detect_pregnancy_emergency = lambda x: {"concern": False, "matched": []}
    
    try:
        from graph.cypher import (
            get_red_flags as neo4j_get_red_flags,
            get_contraindications as neo4j_get_contraindications,
            get_providers_in_city as neo4j_get_providers_in_city,
            get_safe_actions_for_metabolic_conditions as neo4j_get_safe_actions,
        )
    except ImportError as e:
        print(f"[WARN] Could not import graph.cypher: {e}")
        neo4j_get_red_flags = lambda x: []
        neo4j_get_contraindications = lambda x: []
        neo4j_get_providers_in_city = lambda x: []
        neo4j_get_safe_actions = lambda x: []
    
    try:
        from models import Profile, ChatRequest
    except ImportError as e:
        print(f"[ERROR] Could not import models: {e}")
        raise
    
finally:
    # Restore original working directory
    os.chdir(original_cwd)

# Language names
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
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


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    print("\n" + char * 80)
    print(f"  {title}")
    print(char * 80)


def print_step(step_num: int, step_name: str):
    """Print a step header"""
    print(f"\n{'-' * 80}")
    print(f"STEP {step_num}: {step_name}")
    print(f"{'-' * 80}")


def test_pipeline(user_text: str, profile: Profile = None):
    """Test the complete pipeline with detailed output"""
    
    print_section("MULTILINGUAL HEALTHCARE CHATBOT PIPELINE TEST", "=")
    print(f"\n[INPUT] User Input: {user_text}")
    print(f"[INPUT] Input Length: {len(user_text)} characters")
    
    if profile:
        print(f"\n[PROFILE] User Profile:")
        if profile.age:
            print(f"   Age: {profile.age}")
        if profile.sex:
            print(f"   Sex: {profile.sex}")
        conditions = []
        if profile.diabetes:
            conditions.append("Diabetes")
        if profile.hypertension:
            conditions.append("Hypertension")
        if profile.pregnancy:
            conditions.append("Pregnancy")
        if conditions:
            print(f"   Conditions: {', '.join(conditions)}")
        if profile.city:
            print(f"   City: {profile.city}")
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[ERROR] OPENAI_API_KEY not found!")
        return
    
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    print(f"\n[MODEL] Using Model: {model}")
    
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] OpenAI client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}")
        return
    
    timings = {}
    total_start = time.perf_counter()
    
    # ============================================================
    # STEP 1: Language Detection (Separate Stage)
    # ============================================================
    print_step(1, "Language Detection")
    step1_start = time.perf_counter()
    
    print(f"\n[DETECT] Detecting language...")
    print(f"   Input text: '{user_text}'")
    
    try:
        from pipeline_functions import detect_language_only
        detected_lang = detect_language_only(
            client=client,
            model=model,
            user_text=user_text
        )
        
        timings["step1_language_detection"] = time.perf_counter() - step1_start
        
        print(f"\n[OK] Step 1 Complete!")
        print(f"   Detected Language: {detected_lang} ({LANGUAGE_NAMES.get(detected_lang, 'Unknown')})")
        if detected_lang == "en":
            print(f"   [OPTIMIZATION] English detected - translation steps will be skipped!")
        print(f"   Time taken: {timings['step1_language_detection']:.2f}s")
        
    except Exception as e:
        print(f"\n[ERROR] Step 1 Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # STEP 1.5: Translation to English (SKIP if English detected)
    # ============================================================
    step1_5_start = time.perf_counter()
    
    if detected_lang == "en":
        # Skip translation - optimization
        english_text = user_text
        print(f"\n[SKIP] Translation to English skipped (English detected)")
        timings["step1_5_translation_to_english"] = 0.0
    else:
        print(f"\n[TRANSLATE] Translating to English...")
        print(f"   Source Language: {detected_lang} ({LANGUAGE_NAMES.get(detected_lang, 'Unknown')})")
        print(f"   Target Language: English")
        
        try:
            from pipeline_functions import translate_to_english
            english_text = translate_to_english(
                client=client,
                model=model,
                user_text=user_text,
                source_language=detected_lang
            )
            
            timings["step1_5_translation_to_english"] = time.perf_counter() - step1_5_start
            
            print(f"\n[OK] Translation Complete!")
            print(f"   English Translation: '{english_text}'")
            print(f"   Time taken: {timings['step1_5_translation_to_english']:.2f}s")
            
        except Exception as e:
            print(f"\n[ERROR] Translation Failed: {e}")
            import traceback
            traceback.print_exc()
            english_text = user_text
            timings["step1_5_translation_to_english"] = time.perf_counter() - step1_5_start
    
    # ============================================================
    # STEP 2: ChromaDB RAG Retrieval
    # ============================================================
    print_step(2, "ChromaDB RAG Retrieval")
    step2_start = time.perf_counter()
    
    print(f"\n[RAG] Retrieving relevant medical knowledge from ChromaDB...")
    print(f"   Query (English): '{english_text}'")
    
    try:
        rag_results = retrieve(english_text, k=4)
        timings["step2_rag_retrieval"] = time.perf_counter() - step2_start
        
        print(f"\n[OK] Step 2 Complete!")
        print(f"   Retrieved {len(rag_results)} relevant chunks")
        
        if rag_results:
            print(f"\n   Top Results:")
            for i, result in enumerate(rag_results[:3], 1):
                print(f"\n   {i}. Source: {result.get('source', 'Unknown')}")
                print(f"      Topic: {result.get('topic', 'Unknown')}")
                chunk_preview = result.get('chunk', '')[:150]
                print(f"      Preview: {chunk_preview}...")
        else:
            print(f"   [WARN] No results retrieved from ChromaDB")
        
        print(f"   Time taken: {timings['step2_rag_retrieval']:.2f}s")
        
    except Exception as e:
        print(f"\n[ERROR] Step 2 Failed: {e}")
        import traceback
        traceback.print_exc()
        rag_results = []
        timings["step2_rag_retrieval"] = time.perf_counter() - step2_start
    
    # ============================================================
    # STEP 3: Neo4j Graph Database (with fallback)
    # ============================================================
    print_step(3, "Neo4j Graph Database Queries")
    step3_start = time.perf_counter()
    
    print(f"\n[NEO4J] Querying Neo4j graph database...")
    print(f"   Query (English): '{english_text}'")
    
    facts = []
    
    # Safety detection
    try:
        safety_result = detect_red_flags(english_text, "en")
        mental_health = detect_mental_health_crisis(english_text, "en")
        pregnancy_alert = detect_pregnancy_emergency(english_text)
        
        print(f"\n   Safety Analysis:")
        print(f"      Red Flags: {'Yes' if safety_result.get('red_flag') else 'No'}")
        print(f"      Mental Health Crisis: {'Yes' if mental_health.get('crisis') else 'No'}")
        print(f"      Pregnancy Alert: {'Yes' if pregnancy_alert.get('concern') else 'No'}")
        
        if safety_result.get("red_flag"):
            symptoms = extract_symptoms(english_text)
            print(f"      Extracted Symptoms: {symptoms}")
            
            try:
                red_flag_results = neo4j_get_red_flags(symptoms)
                if red_flag_results:
                    facts.append({"type": "red_flags", "data": red_flag_results})
                    print(f"      [OK] Found {len(red_flag_results)} red flag conditions")
                else:
                    print(f"      [INFO] No red flag conditions found in graph")
            except Exception as e:
                print(f"      [WARN] Neo4j query failed (using fallback): {e}")
        
        if mental_health.get("crisis"):
            facts.append({
                "type": "mental_health_crisis",
                "data": {
                    "matched": mental_health.get("matched"),
                    "actions": mental_health.get("first_aid"),
                },
            })
            print(f"      [OK] Mental health crisis detected")
        
        if pregnancy_alert.get("concern"):
            facts.append({
                "type": "pregnancy_alert",
                "data": {
                    "matched": pregnancy_alert.get("matched"),
                    "guidance": ["Severe pregnancy symptoms need urgent medical review."],
                },
            })
            print(f"      [OK] Pregnancy alert detected")
        
    except Exception as e:
        print(f"      [WARN] Safety detection error: {e}")
    
    # Graph intent check
    try:
        use_graph = is_graph_intent(english_text)
        print(f"\n   Graph Intent: {'Yes' if use_graph else 'No'}")
        
        if use_graph:
            print(f"   [QUERY] Querying graph database for structured data...")
            
            # Get user conditions from profile
            user_conditions = []
            if profile:
                if profile.diabetes:
                    user_conditions.append("Diabetes")
                if profile.hypertension:
                    user_conditions.append("Hypertension")
                if profile.pregnancy:
                    user_conditions.append("Pregnancy")
            
            if user_conditions:
                print(f"      User Conditions: {', '.join(user_conditions)}")
                
                try:
                    # Contraindications
                    contras = neo4j_get_contraindications(user_conditions)
                    if contras:
                        print(f"      [OK] Found {len(contras)} contraindications")
                        facts.append({"type": "contraindications", "data": contras})
                    else:
                        print(f"      [INFO] No contraindications found")
                except Exception as e:
                    print(f"      [WARN] Contraindications query failed: {e}")
                
                try:
                    # Safe actions
                    for condition in user_conditions:
                        safe_actions = neo4j_get_safe_actions([condition])
                        if safe_actions:
                            print(f"      [OK] Found {len(safe_actions)} safe actions for {condition}")
                            facts.append({
                                "type": "safe_actions",
                                "data": [{"condition": condition, "actions": [a.get("safeAction") for a in safe_actions[:5]]}]
                            })
                except Exception as e:
                    print(f"      [WARN] Safe actions query failed: {e}")
            
            # City/providers
            city = None
            if profile and profile.city:
                city = profile.city
            else:
                city = extract_city(english_text)
            
            if city:
                print(f"      City: {city}")
                try:
                    providers = neo4j_get_providers_in_city(city)
                    if providers:
                        print(f"      [OK] Found {len(providers)} healthcare providers in {city}")
                        facts.append({"type": "providers", "data": providers})
                    else:
                        print(f"      [INFO] No providers found in {city}")
                except Exception as e:
                    print(f"      [WARN] Providers query failed: {e}")
        
    except Exception as e:
        print(f"      [WARN] Graph query error: {e}")
    
    timings["step3_neo4j"] = time.perf_counter() - step3_start
    
    print(f"\n[OK] Step 3 Complete!")
    print(f"   Total Facts Found: {len(facts)}")
    for fact in facts:
        print(f"      - {fact.get('type', 'unknown')}: {len(fact.get('data', []))} items")
    print(f"   Time taken: {timings['step3_neo4j']:.2f}s")
    
    # ============================================================
    # STEP 4: Generate Final Answer in English
    # ============================================================
    print_step(4, "Generate Final Answer in English")
    step4_start = time.perf_counter()
    
    print(f"\n[GENERATE] Generating final answer using GPT-4o-mini...")
    print(f"   User Question (English): '{english_text}'")
    print(f"   RAG Context: {len(rag_results)} chunks")
    print(f"   Facts: {len(facts)} fact groups")
    
    # Build context
    context = "\n\n".join([r.get("chunk", "") for r in rag_results]) if rag_results else "No additional context available."
    
    try:
        answer_en = generate_final_answer(
            client=client,
            model=model,
            user_question=english_text,
            rag_context=context,
            facts=facts,
            profile=profile or Profile(),
        )
        
        timings["step4_answer_generation"] = time.perf_counter() - step4_start
        
        print(f"\n[OK] Step 4 Complete!")
        print(f"   Answer (English):")
        print(f"   {'-' * 76}")
        # Print answer with proper formatting
        for line in answer_en.split('\n'):
            print(f"   {line}")
        print(f"   {'-' * 76}")
        print(f"   Answer Length: {len(answer_en)} characters")
        print(f"   Time taken: {timings['step4_answer_generation']:.2f}s")
        
    except Exception as e:
        print(f"\n[ERROR] Step 4 Failed: {e}")
        import traceback
        traceback.print_exc()
        answer_en = "I apologize, but I encountered an error generating the answer."
        timings["step4_answer_generation"] = time.perf_counter() - step4_start
    
    # ============================================================
    # STEP 5: Translate Answer Back to User's Language
    # ============================================================
    print_step(5, "Translate Answer Back to User's Language")
    step5_start = time.perf_counter()
    
    # Skip translation back if English was detected (optimization)
    if detected_lang == "en":
        final_answer = answer_en
        print(f"\n[SKIP] Translation back to user's language skipped (English detected)")
        print(f"   Final answer will be in English (no translation needed)")
        timings["step5_translation"] = 0.0
    elif detected_lang != "en":
        print(f"\n[TRANSLATE] Translating answer back to {LANGUAGE_NAMES.get(detected_lang, detected_lang)}...")
        print(f"   Source Language: English")
        print(f"   Target Language: {detected_lang} ({LANGUAGE_NAMES.get(detected_lang, 'Unknown')})")
        print(f"   Output Format: Native Script (always native script, not romanized)")
        
        try:
            final_answer = translate_to_user_language(
                client=client,
                model=model,
                english_text=answer_en,
                target_language=detected_lang,
            )
            
            timings["step5_translation"] = time.perf_counter() - step5_start
            
            print(f"\n[OK] Step 5 Complete!")
            print(f"   Final Answer ({LANGUAGE_NAMES.get(detected_lang, detected_lang)} - Native Script):")
            print(f"   {'-' * 76}")
            for line in final_answer.split('\n'):
                print(f"   {line}")
            print(f"   {'-' * 76}")
            print(f"   Answer Length: {len(final_answer)} characters")
            print(f"   Time taken: {timings['step5_translation']:.2f}s")
            
        except Exception as e:
            print(f"\n[ERROR] Step 5 Failed: {e}")
            import traceback
            traceback.print_exc()
            final_answer = answer_en  # Fallback to English
            timings["step5_translation"] = time.perf_counter() - step5_start
    else:
        print(f"\n[OK] Step 5 Complete!")
        print(f"   Language is English, no translation needed")
        final_answer = answer_en
        timings["step5_translation"] = 0
    
    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    timings["total"] = time.perf_counter() - total_start
    
    print_section("PIPELINE TEST SUMMARY", "=")
    
    print(f"\n[METRICS] Performance Metrics:")
    print(f"   Total Time: {timings['total']:.2f}s")
    print(f"   Step 1 (Language Detection): {timings.get('step1_language_detection', 0):.2f}s")
    print(f"   Step 1.5 (Translation to English): {timings.get('step1_5_translation_to_english', 0):.2f}s {'(SKIPPED)' if detected_lang == 'en' else ''}")
    print(f"   Step 2 (RAG Retrieval): {timings.get('step2_rag_retrieval', 0):.2f}s")
    print(f"   Step 3 (Neo4j Queries): {timings.get('step3_neo4j', 0):.2f}s")
    print(f"   Step 4 (Answer Generation): {timings.get('step4_answer_generation', 0):.2f}s")
    print(f"   Step 5 (Translation Back): {timings.get('step5_translation', 0):.2f}s {'(SKIPPED)' if detected_lang == 'en' else ''}")
    
    print(f"\n[RESULTS] Pipeline Results:")
    print(f"   Detected Language: {detected_lang} ({LANGUAGE_NAMES.get(detected_lang, 'Unknown')})")
    print(f"   RAG Chunks Retrieved: {len(rag_results)}")
    print(f"   Facts from Graph: {len(facts)}")
    print(f"   Final Answer Length: {len(final_answer)} characters")
    
    print(f"\n[SUCCESS] Pipeline Test Complete!")
    print(f"\n{'=' * 80}\n")
    
    return {
        "detected_language": detected_lang,
        "english_text": english_text,
        "rag_results": rag_results,
        "facts": facts,
        "answer_english": answer_en,
        "final_answer": final_answer,
        "timings": timings,
    }


def main():
    """Main test function - accepts text input directly"""
    print("\n" + "=" * 80)
    print("  MULTILINGUAL HEALTHCARE CHATBOT - PIPELINE TEST")
    print("=" * 80)
    
    # Load environment
    load_environment()
    
    # Get text input from command line arguments or user input
    if len(sys.argv) > 1:
        # Text provided as command line argument
        user_text = " ".join(sys.argv[1:])
        print(f"\n[INPUT] Input Text: '{user_text}'")
    else:
        # Get text input from user
        print("\n[INPUT] Enter your question:")
        user_text = input("> ").strip()
        
        if not user_text:
            print("\n[WARN] No text provided. Using default test case...")
            user_text = "enakku pasikuduthu"  # Tamil: I am hungry
            print(f"  Using: '{user_text}'")
    
    # Use default profile (can be customized if needed)
    profile = Profile(
        age=None,
        sex=None,
        diabetes=False,
        hypertension=False,
        pregnancy=False,
        city=None,
    )
    
    print("\n" + "=" * 80)
    print("  STARTING PIPELINE TEST")
    print("=" * 80)
    
    # Run pipeline test
    try:
        results = test_pipeline(user_text, profile)
        
        if results:
            print("\n[SUCCESS] Test completed successfully!")
            print(f"\n[SUMMARY] Final Result Summary:")
            print(f"   Detected Language: {results['detected_language']} ({LANGUAGE_NAMES.get(results['detected_language'], 'Unknown')})")
            print(f"   RAG Chunks: {len(results['rag_results'])}")
            print(f"   Facts: {len(results['facts'])}")
            print(f"   Final Answer ({LANGUAGE_NAMES.get(results['detected_language'], 'Unknown')}):")
            print(f"   {'-' * 76}")
            # Show first few lines of answer
            answer_lines = results['final_answer'].split('\n')[:5]
            for line in answer_lines:
                print(f"   {line}")
            if len(results['final_answer'].split('\n')) > 5:
                print(f"   ... ({len(results['final_answer'].split('\n')) - 5} more lines)")
            print(f"   {'-' * 76}")
        else:
            print("\n[WARN] Test completed with errors")
            
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

