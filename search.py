import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import embeddings
import fuzzy_match

# Words that don't add meaning to medicine searches
STOP_WORDS = {
    "medicine",
    "tablet",
    "capsule",
    "syrup",
    "for",
    "with",
    "give",
    "need",
    "want",
    "best",
    "please",
    "suggest",
    "recommended"
}


def preprocess_query(query: str) -> str:
    """
    Remove generic words before generating embeddings.
    Example:
    'medicine for stomach pain'
    becomes
    'stomach pain'
    """
    words = query.lower().split()

    filtered_words = [
        word for word in words
        if word not in STOP_WORDS
    ]

    return " ".join(filtered_words)


def search_medicines(query: str) -> dict:
    """
    Hybrid Search:
    1. Fuzzy Matching -> Fix medicine name typos
    2. Query Cleaning -> Remove generic words
    3. Embeddings -> Semantic Search
    4. Return Top 5 Results
    """

    if not embeddings.medicine_records or embeddings.medicine_embeddings is None:
        raise ValueError(
            "Embeddings cache is empty. Please initialize embeddings first."
        )

    # Medicine names for fuzzy matching
    medicine_names = [
        record["MedicineName"]
        for record in embeddings.medicine_records
    ]

    # Step 1: Fix spelling mistakes
    corrected_query = fuzzy_match.correct_spelling(
        query,
        medicine_names
    )

    # Step 2: Remove stop words
    clean_query = preprocess_query(
        corrected_query
    )

    print(f"Original Query: {query}")
    print(f"Corrected Query: {corrected_query}")
    print(f"Clean Query: {clean_query}")

    # Step 3: Generate embedding
    query_vector = embeddings.get_query_embedding(
        clean_query
    )

    # Step 4: Cosine Similarity
    similarity_scores = cosine_similarity(
        query_vector.reshape(1, -1),
        embeddings.medicine_embeddings
    )[0]

    # Step 5: Get Top 5 Results
    top_indices = np.argsort(
        similarity_scores
    )[::-1][:5]

    results = []

    for idx in top_indices:

        score = float(similarity_scores[idx])

        # Ignore very weak matches
        if score < 0.40:
            continue

        medicine = embeddings.medicine_records[idx]

        results.append({
            "MedicineName": medicine["MedicineName"],
            "Composition": medicine["Composition"],
            "Uses": medicine["Uses"],
            "SideEffects": medicine["SideEffects"],
            "Manufacturer": medicine["Manufacturer"],
            "SimilarityScore": round(score, 4)
        })

    return {
        "Query": query,
        "CorrectedQuery": corrected_query,
        "CleanQuery": clean_query,
        "TopMatches": results
    }