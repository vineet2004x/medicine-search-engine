import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import embeddings
import fuzzy_match
from utils.text_preprocess import clean_query as preprocess_query
from utils.intent_classifier import detect_intent, SearchIntent
from utils.symptom_corrector import correct_symptom
from utils.ranking import calculate_final_score
from utils.dosage_extractor import extract_dosage

# Minimum similarity score required
SIMILARITY_THRESHOLD = 0.45

def search_medicines(query: str) -> dict:
    """
    Hybrid Search Pipeline

    1. Detect Intent
    2. Correct spelling (Medicine search only)
    3. Clean query
    4. Generate embedding
    5. Semantic Search
    6. Return Top Results
    """

    if not embeddings.medicine_records or embeddings.medicine_embeddings is None:
        raise ValueError(
            "Embeddings cache is empty. Please initialize embeddings first."
        )

    # -------------------------------
    # Step 1 : Fuzzy Matching
    # -------------------------------

    medicine_names = [
        record["MedicineName"]
        for record in embeddings.medicine_records
    ]

    composition_names = [
        record["Composition"]
        for record in embeddings.medicine_records
    ]

    manufacturer_names = [
        record["Manufacturer"]
        for record in embeddings.medicine_records
    ]

    # Combine everything searchable
    search_terms = list(
        set(
        medicine_names
        + composition_names
        + manufacturer_names
        )
    )

    # Correct spelling first
    corrected_query = fuzzy_match.correct_spelling(
        query,
        embeddings.search_terms
    )
    corrected_query = correct_symptom(corrected_query)

    # -------------------------------
    # Step 2 : Detect Intent
    # -------------------------------

    intent = detect_intent(corrected_query)

    logging.info(f"Detected Intent : {intent.value}")
    # -------------------------------
    # Step 3 : Clean Query
    # -------------------------------
    clean_query = preprocess_query(corrected_query)
    query_dosage = extract_dosage(corrected_query)

    logging.info(f"Dosage : {query_dosage}")

    logging.info(f"Original Query : {query}")
    logging.info(f"Corrected Query : {corrected_query}")
    logging.info(f"Clean Query : {clean_query}")

    # If query becomes empty after preprocessing
    if not clean_query.strip():
        return {
            "Query": query,
            "Intent": intent.value,
            "CorrectedQuery": corrected_query,
            "CleanQuery": clean_query,
            "Message": "Please enter a more specific search query.",
            "TopMatches": []
        }

    # -------------------------------
    # Step 4 : Generate Query Embedding
    # -------------------------------

    query_vector = embeddings.get_query_embedding(clean_query)

    # -------------------------------
    # Step 5 : Select Embedding Index
    # -------------------------------

    if intent == SearchIntent.SYMPTOM:

        search_embeddings = embeddings.uses_embeddings

    elif intent == SearchIntent.COMPOSITION:

        search_embeddings = embeddings.composition_embeddings

    elif intent == SearchIntent.MANUFACTURER:

        search_embeddings = embeddings.manufacturer_embeddings

    else:

        search_embeddings = embeddings.medicine_embeddings

    # -------------------------------
    # Step 6 : Cosine Similarity
    # -------------------------------

    similarity_scores = cosine_similarity(
        query_vector.reshape(1, -1),
        search_embeddings
    )[0]

    # Top 5 Highest Scores
    top_indices = np.argsort(similarity_scores)[::-1][:20]

    results = []

    for idx in top_indices:

        semantic_score = float(
            similarity_scores[idx]
        )

        medicine = embeddings.medicine_records[idx]
        score = calculate_final_score(
            corrected_query,
            medicine,
            semantic_score,
            query_dosage
        )
        if query_dosage:

            medicine_text = (
                medicine["MedicineName"]
                + " "
                + medicine["Composition"]
            ).lower()

            if query_dosage in medicine_text:
                score += 0.30

        if score < SIMILARITY_THRESHOLD:
            continue

        results.append({
            "MedicineName": medicine["MedicineName"],
            "Composition": medicine["Composition"],
            "Uses": medicine["Uses"],
            "SideEffects": medicine["SideEffects"],
            "Manufacturer": medicine["Manufacturer"],
            "SimilarityScore": score
        })

    # Sort by similarity score
    results.sort(
        key=lambda x: x["SimilarityScore"],
        reverse=True
    )
    results = results[:5]

    logging.info(f"Intent: {intent.value}")
    logging.info(f"Returned {len(results)} medicines")

    for medicine in results:
        logging.info(
            f"{medicine['MedicineName']} "
            f"({medicine['SimilarityScore']})"
        )

    # -------------------------------
    # No Results Found
    # -------------------------------
    if not results:
        return {
            "Query": query,
            "Intent": intent.value,
            "CorrectedQuery": corrected_query,
            "CleanQuery": clean_query,
            "Message": "No relevant medicines found.",
            "TopMatches": []
        }

    # -------------------------------
    # Success Response
    # -------------------------------
    return {
        "Query": query,
        "Intent": intent.value,
        "CorrectedQuery": corrected_query,
        "CleanQuery": clean_query,
        "TopMatches": results
    }