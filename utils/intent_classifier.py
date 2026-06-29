import re
from enum import Enum


class SearchIntent(Enum):
    """
    Supported search intents.
    """

    MEDICINE = "Medicine Name"
    SYMPTOM = "Symptom"
    COMPOSITION = "Composition"
    MANUFACTURER = "Manufacturer"
    UNKNOWN = "Unknown"


# ---------------------------------------------------
# Keywords used to identify user intent
# ---------------------------------------------------

SYMPTOM_KEYWORDS = {
    "fever",
    "cold",
    "cough",
    "pain",
    "headache",
    "stomach",
    "acidity",
    "gas",
    "ulcer",
    "infection",
    "diabetes",
    "blood pressure",
    "hypertension",
    "heart",
    "cholesterol",
    "allergy",
    "vomiting",
    "nausea",
    "diarrhea",
    "constipation",
    "migraine",
    "flu",
    "asthma",
    "arthritis",
    "kidney",
    "liver",
    "cancer",
    "anxiety"
}


COMPOSITION_KEYWORDS = {
    "paracetamol",
    "ibuprofen",
    "diclofenac",
    "rabeprazole",
    "levosulpiride",
    "cetirizine",
    "azithromycin",
    "amoxicillin",
    "metformin",
    "atorvastatin",
    "pantoprazole",
    "omeprazole",
    "dicyclomine"
}


MANUFACTURER_KEYWORDS = {
    "sun pharma",
    "cipla",
    "mankind",
    "dr reddy",
    "dr reddys",
    "torrent",
    "abbott",
    "alkem",
    "zydus",
    "lupin",
    "glenmark",
    "intas",
    "pfizer",
    "fdc"
}


def detect_intent(query: str) -> SearchIntent:
    """
    Detect the user's search intent.

    Priority:
    1. Manufacturer
    2. Composition
    3. Symptom
    4. Medicine Name
    5. Unknown
    """

    query = query.lower().strip()

    # Manufacturer search
    if any(manufacturer in query for manufacturer in MANUFACTURER_KEYWORDS):
        return SearchIntent.MANUFACTURER

    # Composition search
    if any(composition in query for composition in COMPOSITION_KEYWORDS):
        return SearchIntent.COMPOSITION

    if any(
        phrase in query
        for phrase in [
            "medicine for",
            "medicines for",
            "tablet for",
            "tablets for",
            "drug for",
            "drugs for",
            "treatment for",
            "used for",
            "good for",
            "best medicine for",
            "which medicine for"
        ]
    ):
        return SearchIntent.SYMPTOM

    # Symptom keyword detection
    if any(
        re.search(rf"\b{re.escape(symptom)}\b", query)
        for symptom in SYMPTOM_KEYWORDS
):
        return SearchIntent.SYMPTOM

    # Medicine search
    words = query.split()

    if len(words) <= 3:
        return SearchIntent.MEDICINE

    return SearchIntent.UNKNOWN