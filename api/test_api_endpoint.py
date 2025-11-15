#!/usr/bin/env python3
"""
Test the /chat API endpoint on a running server
This will ping your running FastAPI server and test the complete pipeline
"""

import sys
import requests
import json
from typing import Optional

# Default server URL
DEFAULT_SERVER_URL = "http://localhost:8000"


def test_chat_endpoint(
    text: str,
    lang: Optional[str] = None,
    server_url: str = DEFAULT_SERVER_URL,
    profile: Optional[dict] = None,
    auth_token: Optional[str] = None
):
    """
    Test the /chat API endpoint
    
    Args:
        text: User's question text
        lang: Language preference (optional)
        server_url: Server URL (default: http://localhost:8000)
        profile: User profile dict (optional)
        auth_token: JWT auth token (optional, required if auth is enabled)
    """
    print("=" * 80)
    print("  TESTING /chat API ENDPOINT")
    print("=" * 80)
    print(f"\n🌐 Server URL: {server_url}")
    print(f"📝 Input Text: '{text}'")
    if lang:
        print(f"🌐 Language: {lang}")
    if profile:
        print(f"👤 Profile: {profile}")
    print()
    
    # Prepare request payload
    payload = {
        "text": text,
        "profile": profile or {}
    }
    
    if lang:
        payload["lang"] = lang
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json"
    }
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    # Make API request
    print("📡 Sending request to /chat endpoint...")
    print(f"   URL: {server_url}/chat")
    print(f"   Method: POST")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{server_url}/chat",
            json=payload,
            headers=headers,
            timeout=60  # 60 second timeout for pipeline processing
        )
        
        print("=" * 80)
        print("  RESPONSE RECEIVED")
        print("=" * 80)
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Request Successful!")
            print("\n📋 Response Details:")
            print(f"   Route: {data.get('route', 'unknown')}")
            print(f"   Answer Length: {len(data.get('answer', ''))} characters")
            print(f"   Facts: {len(data.get('facts', []))}")
            print(f"   Citations: {len(data.get('citations', []))}")
            
            # Show answer
            answer = data.get('answer', '')
            print(f"\n💬 Answer:")
            print("   " + "-" * 76)
            for line in answer.split('\n'):
                if line.strip():
                    print(f"   {line}")
            print("   " + "-" * 76)
            
            # Show metadata if available
            metadata = data.get('metadata', {})
            if metadata:
                print(f"\n📊 Metadata:")
                timings = metadata.get('timings', {})
                if timings:
                    print(f"   Timings:")
                    for key, value in timings.items():
                        print(f"      {key}: {value:.2f}s")
                
                target_lang = metadata.get('target_language', 'unknown')
                detected_lang = metadata.get('detected_language', 'unknown')
                print(f"   Target Language: {target_lang}")
                print(f"   Detected Language: {detected_lang}")
                
                # Show debug info if available
                if metadata.get('debug'):
                    debug = metadata['debug']
                    print(f"\n🔍 Debug Info:")
                    print(f"   Pipeline: {debug.get('pipeline', 'unknown')}")
                    if 'rag_context_snippets' in debug:
                        print(f"   RAG Context Snippets: {len(debug['rag_context_snippets'])}")
                    if 'llm' in debug:
                        llm_info = debug['llm']
                        print(f"   LLM Provider: {llm_info.get('provider', 'unknown')}")
                        print(f"   LLM Model: {llm_info.get('model', 'unknown')}")
            
            # Show safety info
            safety = data.get('safety', {})
            if safety:
                print(f"\n⚠️  Safety Analysis:")
                print(f"   Red Flag: {safety.get('red_flag', False)}")
                if safety.get('mental_health', {}).get('crisis'):
                    print(f"   Mental Health Crisis: Yes")
                if safety.get('pregnancy', {}).get('concern'):
                    print(f"   Pregnancy Alert: Yes")
            
            # Show facts
            facts = data.get('facts', [])
            if facts:
                print(f"\n📚 Facts from Database:")
                for fact in facts:
                    fact_type = fact.get('type', 'unknown')
                    print(f"   - {fact_type}")
            
            # Show citations
            citations = data.get('citations', [])
            if citations:
                print(f"\n📖 Citations:")
                for i, citation in enumerate(citations[:3], 1):
                    source = citation.get('source', 'unknown')
                    topic = citation.get('topic', 'unknown')
                    print(f"   {i}. {source} - {topic}")
            
            print("\n" + "=" * 80)
            print("✅ TEST COMPLETE")
            print("=" * 80)
            
            return data
            
        else:
            print(f"\n❌ Request Failed!")
            print(f"   Status Code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}")
            
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error!")
        print(f"   Could not connect to {server_url}")
        print(f"   Make sure your server is running:")
        print(f"   python start_server.py")
        return None
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Request Timeout!")
        print(f"   The server took too long to respond (>60s)")
        return None
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("  HEALTHCARE CHATBOT API ENDPOINT TEST")
    print("=" * 80)
    print("\nThis test will call your running FastAPI server's /chat endpoint")
    print("Make sure your server is running: python start_server.py\n")
    
    # Get text input
    if len(sys.argv) > 1:
        user_text = " ".join(sys.argv[1:])
    else:
        print("📝 Enter your question:")
        user_text = input("> ").strip()
        
        if not user_text:
            print("\n⚠️  No text provided. Using default test case...")
            user_text = "enakku pasikuduthu"  # Tamil: I am hungry
            print(f"  Using: '{user_text}'")
    
    # Optional: Server URL
    server_url = os.getenv("API_SERVER_URL", DEFAULT_SERVER_URL)
    
    # Optional: Auth token (if auth is enabled)
    auth_token = os.getenv("AUTH_TOKEN", None)
    
    # Optional: Profile
    profile = {}
    
    # Run test
    result = test_chat_endpoint(
        text=user_text,
        server_url=server_url,
        profile=profile,
        auth_token=auth_token
    )
    
    if result:
        print("\n🎉 API test completed successfully!")
    else:
        print("\n⚠️  API test failed. Check server status and try again.")


if __name__ == "__main__":
    import os
    main()

