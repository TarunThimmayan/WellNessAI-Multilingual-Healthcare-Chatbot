"""
Safety detection utilities for red flags, mental health crisis cues, and symptom extraction.
"""
from typing import Dict, Iterable, List, Set

# Red flag keywords in English and Hindi (transliterated)
RED_FLAGS: Set[str] = {
    # Cardiac/Chest
    "chest pain", "chest pressure", "crushing chest", "seene mein dard",
    "cold sweats", "thandi pasina",
    "tightness in chest", "pressure in chest",
    "left arm pain", "left arm numb", "bahin mein dard",
    "jaw pain", "mandibular pain", "jabde mein dard",
    "sudden heart racing", "heart beating very fast",
    "unconscious with chest pain",

    # Respiratory
    "shortness of breath", "can't breathe", "difficulty breathing",
    "saans nahi aa rahi", "saans lene mein takleef",
    "saans ruk raha", "breathlessness", "gasping for air",
    "bluish lips", "blue face", "honth neele",
    "wheezing not improving", "severe wheeze",
    "oxygen below 90", "spo2 below 90",
    "swelling face with breathing trouble", "throat closing", "gale mein soojan",

    # Neurological
    "severe headache", "worst headache", "sudden headache", "thunderclap headache",
    "one-side weakness", "weakness one side", "ek taraf kamzori", "one sided weakness",
    "body numb one side", "haath pair sunn",
    "difficulty speaking", "slurred speech", "bolne mein dikkat",
    "vision changes", "sudden vision loss", "dekhne mein dikkat", "double vision",
    "confusion", "disoriented", "behoshi",
    "seizure", "convulsion", "daura",
    "stiff neck", "gardan akad",
    "face drooping", "munh tedha",
    "sudden loss of consciousness", "passed out suddenly",
    "sudden severe dizziness", "giddiness too much",

    # Bleeding/Trauma
    "heavy bleeding", "severe bleeding", "khoon beh raha", "uncontrolled bleeding",
    "blood in stool", "black stool", "pakhana mein khoon",
    "blood in vomit", "ulti mein khoon",
    "pregnancy bleeding", "garbhavastha mein khoon", "pregnancy heavy bleeding",
    "pregnancy severe pain", "garbhavastha mein tez dard",
    "open fracture", "bone out", "haddi bahar aa gayi",
    "head injury with vomiting", "sir mein chot aur ulti",
    "spine injury", "peeth ki haddi mein chot",
    "hit on head unconscious", "sir par chot behoshi",

    # Abdominal
    "severe abdominal pain", "severe stomach pain", "pet mein bahut dard", "pet mein tez dard",
    "vomiting blood", "persistent vomiting", "ulati ruk nahi rahi",
    "severe back pain with urine issues",

    # Fever/Infection
    "high fever child", "infant fever", "bacche ko tez bukhar", "baby fever high",
    "fever not reducing", "uncontrolled fever",
    "fever with rash", "bukhar aur daane",
    "neck stiffness with fever", "bukhar ke saath gardan akad",
    "fever with confusion",

    # Mental Health
    "suicidal thoughts", "want to die", "khudkushi",
    "self harm", "hurt myself", "end my life", "khud ko nuksan",
    "life not worth living", "give up on life",
    "voices telling me to hurt myself", "main khud ko chot pohchana chahta hun",

    # Diabetic Emergency
    "very high sugar", "sugar 300", "sugar 400",
    "fruity breath", "rapid breathing with diabetes",
    "ketone", "ketones", "ketoacidosis",
    "cannot wake diabetic", "diabetic unconscious",

    # Dehydration / Shock
    "severe dehydration", "pani ki bahut kami", "bahut zyada pani ki kami",
    "no urine", "passing very little urine",
    "sunken eyes", "aankhen dhans gayi",
    "dry mouth baby", "bacche ka muh sukha",
    "no wet diapers", "baby not passing urine",

    # Pregnancy specific
    "reduced fetal movements", "baby not moving", "pet mein bachha nahi hil raha",
    "water broke early", "pani tut gaya jaldi",
    "severe swelling face pregnancy", "pregnancy blurred vision",
    "less fetal movement", "kick count low", "pregnant severe headache",

    # Pediatric
    "baby not feeding", "newborn not feeding", "baccha doodh nahi pi raha",
    "persistent crying with fever", "infant difficult to wake",

    # Allergy / Anaphylaxis
    "throat swelling", "throat is swelling", "tongue swelling", "jeebh sooj gayi",
    "rash with breathing issue", "allergic reaction severe",

    # Poisoning / Toxic
    "consumed poison", "zehar kha liya", "chemical ingestion",
    "snake bite with swelling", "saap ne kata aur soojan",
}

MENTAL_HEALTH_CRISIS_TERMS: Set[str] = {
    "suicidal thoughts", "i want to die", "i want to kill myself", "kill myself",
    "i plan to hurt myself", "hurt myself", "self harm", "cut myself",
    "end my life", "life not worth living", "want to disappear",
    "voices telling me to hurt myself", "hearing voices to die",
    "thoughts of suicide", "thinking of suicide", "khudkushi", "apni jaan",
    "i cannot go on", "give up on life", "want to sleep forever",
}

MENTAL_HEALTH_FIRST_AID_EN = [
    "If you or someone with you is in immediate danger, call your local emergency number right away.",
    "Reach out to trusted family or friends and do not stay alone.",
    "Contact a mental health helpline or crisis service (e.g. KIRAN Helpline 1800-599-0019 in India).",
    "Remove access to anything that could be used for self-harm while you seek help.",
]

MENTAL_HEALTH_FIRST_AID_HI = [
    "अगर आप या आपके साथ कोई तुरंत खतरे में है तो तुरंत अपने स्थानीय आपातकालीन नंबर पर कॉल करें।",
    "किसी भरोसेमंद परिवार सदस्य या मित्र से संपर्क करें और अकेले न रहें।",
    "मानसिक स्वास्थ्य हेल्पलाइन या संकट सेवा से संपर्क करें (जैसे भारत में किरण हेल्पलाइन 1800-599-0019)।",
    "सहायता लेते समय आत्म-हानि के किसी भी साधन को सुरक्षित स्थान पर रखें।",
]

PREGNANCY_CRISIS_TERMS: Set[str] = {
    "pregnancy bleeding", "pregnancy severe pain", "reduced fetal movements",
    "baby not moving", "baby is not moving", "my baby not moving", "my baby is not moving",
    "baby hasn't moved", "water broke early", "pani tut gaya", "severe swelling face pregnancy",
    "pregnancy blurred vision", "pregnant severe headache", "severe abdominal pain pregnancy",
    "kick count low", "less fetal movement",
}

SYMPTOM_SYNONYMS: Dict[str, Set[str]] = {
    "chest pain": {
        "chest pain", "chest pressure", "tightness in chest", "crushing chest",
        "seene mein dard", "heart hurting", "left arm pain", "left arm numb",
        "jaw pain", "jabde mein dard"
    },
    "shortness of breath": {
        "shortness of breath", "breathlessness", "can't breathe", "difficulty breathing",
        "saans nahi aa rahi", "saans lene mein takleef", "gasping for air", "saans ruk raha"
    },
    "high fever": {
        "high fever", "uncontrolled fever", "fever not reducing", "infant fever",
        "high fever child", "baby fever high", "fever with rash"
    },
    "stroke like symptoms": {
        "one-side weakness", "one sided weakness", "weakness one side", "face drooping",
        "difficulty speaking", "slurred speech", "vision changes", "sudden vision loss",
        "munh tedha"
    },
    "severe headache": {
        "severe headache", "worst headache", "sudden headache", "thunderclap headache",
        "pregnant severe headache"
    },
    "seizure": {
        "seizure", "convulsion", "daura", "fits", "jerking"
    },
    "heavy bleeding": {
        "heavy bleeding", "severe bleeding", "khoon beh raha", "bleeding won't stop",
        "pregnancy bleeding"
    },
    "vomiting": {
        "vomiting", "persistent vomiting", "vomiting blood", "ulti", "ulti mein khoon",
    },
    "diarrhea": {"diarrhea", "loose motion", "pet kharab", "watery stool"},
    "dehydration": {
        "dehydration", "no urine", "passing very little urine", "sunken eyes",
        "dry mouth", "bacche ka muh sukha", "no wet diapers"
    },
    "pregnancy emergency": set(PREGNANCY_CRISIS_TERMS),
    "mental health crisis": set(MENTAL_HEALTH_CRISIS_TERMS),
    "allergic reaction": {
        "throat swelling", "throat is swelling", "tongue swelling", "jeebh sooj gayi",
        "rash with breathing issue", "allergic reaction severe", "throat closing"
    },
    "poisoning": {
        "consumed poison", "zehar kha liya", "chemical ingestion", "poisoned",
        "snake bite with swelling", "saap ne kata", "overdose"
    },
    "infant feeding issue": {
        "baby not feeding", "newborn not feeding", "infant difficult to wake",
        "persistent crying with fever"
    },
}


def _match_phrases(text_lower: str, phrases: Iterable[str]) -> List[str]:
    return sorted({phrase for phrase in phrases if phrase in text_lower})


def detect_red_flags(text: str, lang: str = "en") -> dict:
    """
    Detect red flag symptoms in user text.

    Returns dict with keys:
        - red_flag: bool
        - matched: sorted list of matched phrases
    """
    text_lower = text.lower()
    matched_unique = _match_phrases(text_lower, RED_FLAGS)
    return {
        "red_flag": bool(matched_unique),
        "matched": matched_unique,
    }


def detect_mental_health_crisis(text: str, lang: str = "en") -> dict:
    """
    Identify urgent mental health crisis cues requiring escalation.
    """
    text_lower = text.lower()
    matched = _match_phrases(text_lower, MENTAL_HEALTH_CRISIS_TERMS)
    if lang == "hi":
        first_aid = MENTAL_HEALTH_FIRST_AID_HI
    else:
        first_aid = MENTAL_HEALTH_FIRST_AID_EN
    return {
        "crisis": bool(matched),
        "matched": matched,
        "first_aid": first_aid,
    }


def detect_pregnancy_emergency(text: str) -> dict:
    """
    Highlight pregnancy-specific emergencies for tailored messaging.
    """
    text_lower = text.lower()
    matched = _match_phrases(text_lower, PREGNANCY_CRISIS_TERMS)
    return {
        "concern": bool(matched),
        "matched": matched,
    }


def extract_symptoms(text: str) -> List[str]:
    """
    Extract canonical symptom names from free-text user messages.
    """
    text_lower = text.lower()
    found: Set[str] = set()

    for canonical, synonyms in SYMPTOM_SYNONYMS.items():
        for phrase in synonyms:
            if phrase in text_lower:
                found.add(canonical)
                break

    return sorted(found)