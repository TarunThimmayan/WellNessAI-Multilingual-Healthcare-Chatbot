"""
Intent router to determine if query should use Graph or Vector RAG
"""
import re


# Patterns that indicate graph-suitable queries
GRAPH_PATTERNS = [
    r'\b(which|what|list|count|how many|any)\b.*\b(avoid|contraindication|should not|shouldn\'t|unsafe)\b',
    r'\b(which|what|list|count|how many)\b.*\b(provider|hospital|doctor|clinic|specialist|helpline)\b',
    r'\b(count|how many)\b.*\b(red flag|symptom|match|warning)\b',
    r'\b(near|in|at)\b.*\b(mumbai|delhi|bangalore|bengaluru|gurgaon|gurugram|chennai|kolkata|pune|hyderabad|ahmedabad|city)\b',
    r'\b(avoid|contraindicated)\b.*\b(if i|if you|for)\b',
    r'\b(any|what)\b.*\b(red flag|warning signs|danger signs)\b',
    r'\b(pregnan(t|cy)|fetal|baby)\b.*\b(red flag|danger|movement|kick count|warning)\b',
    r'\b(mental health|suicidal|self harm|depression)\b.*\b(help|helpline|resources|emergency)\b',
    r'\b(should i go to|when to go to)\b.*\b(hospital|emergency|casualty)\b',
    r'\b(list|what)\b.*\b(safe|unsafe|avoid)\b.*\b(for|during)\b.*\b(pregnancy|diabetes|hypertension|kidney disease)\b',
]

# Known symptom terms that suggest graph query
SYMPTOM_TERMS = {
    "chest pain", "shortness of breath", "headache", "fever", "diarrhea",
    "vomiting", "nausea", "dizziness", "confusion", "seizure",
    "bleeding", "abdominal pain", "cold sweats", "stiff neck",
    "weakness", "fainting", "numbness", "reduced fetal movements",
    "baby not moving", "severe swelling face pregnancy", "suicidal thoughts",
    "self harm", "panic attack", "severe anxiety"
}

CONDITION_TERMS = {
    "diabetes", "hypertension", "asthma", "heart disease", "kidney disease", "pregnancy",
    "mental health", "depression", "anxiety", "ptsd", "postpartum"
}

PREGNANCY_TERMS = {"pregnancy", "pregnant", "fetal", "baby", "kick count", "labour", "labour", "contractions"}
MENTAL_TERMS = {"suicide", "suicidal", "self harm", "hurt myself", "end my life", "mental health", "depression", "panic attack", "anxiety", "helpline"}
RESOURCE_KEYWORDS = {"helpline", "emergency number", "hotline", "nearest hospital", "provider", "clinic", "doctor", "specialist"}


def is_graph_intent(text: str) -> bool:
    """
    Determine if query should use graph database
    
    Args:
        text: User query
        
    Returns:
        True if graph query is appropriate
    """
    text_lower = text.lower()
    
    # Check for graph-specific regex patterns
    for pattern in GRAPH_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    # Check for multiple symptoms (suggests counting/listing or red-flag matching)
    symptom_count = sum(1 for term in SYMPTOM_TERMS if term in text_lower)
    if symptom_count >= 2:
        return True
    
    # Pregnancy-specific combinations (red flags, movements, safe/avoid instructions)
    if any(term in text_lower for term in PREGNANCY_TERMS):
        if any(trigger in text_lower for trigger in ["red flag", "danger", "movement", "avoid", "safe", "warning", "kick"]):
            return True
        if any(keyword in text_lower for keyword in RESOURCE_KEYWORDS):
            return True

    # Mental health crisis phrases asking for help/resources
    if any(term in text_lower for term in MENTAL_TERMS):
        if any(keyword in text_lower for keyword in RESOURCE_KEYWORDS | {"support", "help", "what to do"}):
            return True

    # Queries combining multiple conditions (e.g., diabetes and hypertension)
    if " and " in text_lower or " with " in text_lower:
        mentioned_conditions = {term for term in CONDITION_TERMS if term in text_lower}
        if len(mentioned_conditions) >= 2:
            return True
    
    # Check for specific keywords
    graph_keywords = [
        "list", "count", "which", "any", "avoid", "contraindication",
        "provider", "hospital", "doctors near", "how many red flags", "is it safe for",
        "should i go to", "hotline", "helpline", "nearby clinic",
    ]
    if any(keyword in text_lower for keyword in graph_keywords):
        return True
    
    return False


def extract_city(text: str) -> str:
    """
    Extract city name from text
    
    Args:
        text: User query
        
    Returns:
        City name or None
    """
    cities = ["Mumbai", "Delhi", "Bangalore", "Bengaluru", "Gurgaon", "Gurugram", "Chennai", "Kolkata", "Pune", "Hyderabad", "Ahmedabad"]
    text_lower = text.lower()
    
    for city in cities:
        if city.lower() in text_lower:
            # Normalise spelling variants (Bangalore/Bengaluru etc.)
            if city.lower() in {"bengaluru"}:
                return "Bangalore"
            if city.lower() in {"gurugram"}:
                return "Gurgaon"
            return city
    
    return None