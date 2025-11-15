"""
Prompt templates for the multilingual healthcare chatbot pipeline
"""

# Language detection + translation prompt
LANGUAGE_DETECTION_TRANSLATION_PROMPT = """You are a language detection and translation expert for a healthcare chatbot.

Your task:
1. Detect the language of the user's text
2. Translate it to English if it's not already in English

IMPORTANT: Respond ONLY with a JSON object in this exact format:
{{
    "detected_language": "language_code",
    "english_text": "translated text in English"
}}

Language codes to use:
- "en" for English
- "hi" for Hindi
- "ta" for Tamil
- "te" for Telugu
- "kn" for Kannada
- "ml" for Malayalam

If the text is already in English, return the same text in "english_text".
If the text is in a supported Indic language (Hindi, Tamil, Telugu, Kannada, Malayalam), translate it to English accurately.
Preserve medical terms and maintain the meaning precisely.

User's text: {user_text}

Respond with ONLY the JSON object, no additional text or explanation."""

# Final reasoning + answer generation prompt
REASONING_ANSWER_PROMPT = """You are a helpful healthcare assistant. Your role is to provide accurate, safe, and empathetic medical information based on the provided context.

Context from knowledge base:
{rag_context}

{facts_context}

User's question: {user_question}

User profile:
{user_profile}

Instructions:
1. Provide a clear, accurate answer based on the context provided
2. If the context doesn't fully answer the question, say so honestly
3. Always emphasize that this is general information, not medical advice
4. For emergencies or serious symptoms, recommend consulting a healthcare professional immediately
5. Be empathetic and supportive
6. Use simple, clear language
7. If there are specific precautions based on user's conditions (diabetes, hypertension, pregnancy), mention them

Respond ONLY with the answer text in English. Do not include any explanations, metadata, or JSON formatting. Just provide the direct answer."""

# Translation back to user language prompt
TRANSLATION_BACK_PROMPT = """You are a professional medical translator. Translate the following English medical response to {target_language}.

IMPORTANT:
- Translate accurately while maintaining medical accuracy
- Keep medical terms clear and understandable
- Maintain the same tone and structure
- Do NOT add any explanations, metadata, or formatting
- Respond ONLY with the translated text

English text to translate:
{english_text}

Target language: {target_language}

Respond with ONLY the translated text, nothing else."""

# Helper function to format facts context
def format_facts_context(facts: list) -> str:
    """Format facts from Neo4j/Graph database into context string"""
    if not facts:
        return ""
    
    context_parts = []
    for fact in facts:
        fact_type = fact.get("type", "")
        fact_data = fact.get("data", [])
        
        if fact_type == "red_flags":
            context_parts.append("⚠️ RED FLAGS DETECTED:")
            for entry in fact_data:
                symptom = entry.get("symptom", "")
                conditions = entry.get("conditions", [])
                if conditions:
                    context_parts.append(f"- {symptom}: Associated with {', '.join(conditions)}")
        
        elif fact_type == "contraindications":
            context_parts.append("⛔ CONTRAINDICATIONS:")
            for entry in fact_data:
                condition = entry.get("condition", "")
                avoid_items = entry.get("avoid", [])
                if avoid_items:
                    context_parts.append(f"- {condition}: Avoid {', '.join(avoid_items)}")
        
        elif fact_type == "safe_actions":
            context_parts.append("✅ SAFE ACTIONS:")
            for entry in fact_data:
                condition = entry.get("condition", "")
                actions = entry.get("actions", [])
                if actions:
                    context_parts.append(f"- {condition}: Safe actions include {', '.join(actions[:5])}")
        
        elif fact_type == "providers":
            context_parts.append("🏥 HEALTHCARE PROVIDERS:")
            for provider in fact_data[:5]:  # Limit to 5 providers
                name = provider.get("provider", "")
                mode = provider.get("mode", "")
                phone = provider.get("phone", "")
                provider_info = f"- {name}"
                if mode:
                    provider_info += f" ({mode})"
                if phone:
                    provider_info += f" - Phone: {phone}"
                context_parts.append(provider_info)
    
    return "\n".join(context_parts) if context_parts else ""

# Helper function to format user profile
def format_user_profile(profile) -> str:
    """Format user profile into context string"""
    profile_parts = []
    
    if hasattr(profile, 'age') and profile.age:
        profile_parts.append(f"Age: {profile.age}")
    
    if hasattr(profile, 'sex') and profile.sex:
        profile_parts.append(f"Sex: {profile.sex}")
    
    conditions = []
    if hasattr(profile, 'diabetes') and profile.diabetes:
        conditions.append("Diabetes")
    if hasattr(profile, 'hypertension') and profile.hypertension:
        conditions.append("Hypertension")
    if hasattr(profile, 'pregnancy') and profile.pregnancy:
        conditions.append("Pregnancy")
    
    if hasattr(profile, 'medical_conditions') and profile.medical_conditions:
        for cond in profile.medical_conditions:
            cond_label = cond.capitalize().replace("_", " ")
            if cond_label not in conditions:
                conditions.append(cond_label)
    
    if conditions:
        profile_parts.append(f"Medical conditions: {', '.join(conditions)}")
    
    if hasattr(profile, 'city') and profile.city:
        profile_parts.append(f"Location: {profile.city}")
    
    return "\n".join(profile_parts) if profile_parts else "No specific profile information"

