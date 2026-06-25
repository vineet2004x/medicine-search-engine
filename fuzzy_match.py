import re
from rapidfuzz import process, fuzz

COMMON_MEDICAL_WORDS = {
    "medicine", "tablet", "capsule", "syrup", "injection",
    "fever", "pain", "infection", "diabetes", "allergy",
    "stomach", "headache", "cough", "cold", "acid",
    "blood", "pressure", "cholesterol", "heart",
    "kidney", "liver", "cancer", "bacterial", "viral",
    "treatment", "for", "with", "and", "of"
}

def correct_spelling(query, medicine_names, threshold=90):

    words = re.findall(r'\b[a-zA-Z]+\b', query)

    corrected_query = query

    for word in words:

        if len(word) < 4:
            continue

        if word.lower() in COMMON_MEDICAL_WORDS:
            continue

        match = process.extractOne(
            word,
            medicine_names,
            scorer=fuzz.WRatio
        )

        if match and match[1] >= threshold:

            print(
                f"Corrected '{word}' -> '{match[0]}' "
                f"(score={match[1]:.2f})"
            )

            corrected_query = corrected_query.replace(
                word,
                match[0]
            )

    return corrected_query