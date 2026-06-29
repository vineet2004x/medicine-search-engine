import re


def calculate_final_score(
    query: str,
    medicine: dict,
    semantic_score: float,
    query_dosage=None
):

    score = semantic_score

    query = query.lower()

    medicine_name = medicine["MedicineName"].lower()
    composition = medicine["Composition"].lower()
    manufacturer = medicine["Manufacturer"].lower()

    medicine_text = medicine_name + " " + composition

    # Exact Match
    if query == medicine_text:
        score += 1.0

    # Partial Match
    elif query in medicine_text:
        score += 0.30

    # Ignore dosage while keyword matching
    words = [
        word
        for word in query.split()
        if not word.isdigit() and word != "mg"
    ]

    # Medicine keyword match
    matched = sum(
        word in medicine_name
        for word in words
    )

    score += matched * 0.08

    # Composition keyword match
    matched = sum(
        word in composition
        for word in words
    )

    score += matched * 0.10

    # Manufacturer keyword match
    matched = sum(
        word in manufacturer
        for word in words
    )

    score += matched * 0.10

    # Dosage Match
    if query_dosage:

        medicine_numbers = re.findall(
            r"\d+",
            medicine_text
        )

        if query_dosage in medicine_numbers:
            score += 1.0
        else:
            score -= 0.40

    return round(score, 4)