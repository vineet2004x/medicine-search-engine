from rapidfuzz import process

SYMPTOMS = [
    "fever",
    "cold",
    "cough",
    "headache",
    "body pain",
    "stomach pain",
    "diabetes",
    "hypertension",
    "acidity",
    "gas",
    "allergy",
    "vomiting",
    "nausea",
    "diarrhea",
    "constipation",
    "migraine",
    "asthma",
    "arthritis"
]


def correct_symptom(query: str):
    words = query.lower().split()

    corrected = []

    for word in words:

        match = process.extractOne(word, SYMPTOMS)

        if match and match[1] >= 80:
            corrected.append(match[0])
        else:
            corrected.append(word)

    return " ".join(corrected)  