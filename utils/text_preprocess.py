import re
from utils.stopwords import STOP_WORDS


def clean_query(query: str) -> str:
    """
    Clean user's query before generating embeddings.

    Examples

    medicine for stomach pain
    -> stomach pain

    paracetamol 500 mg
    -> paracetamol 500mg

    metformin 1000 mg
    -> metformin 1000mg
    """

    query = query.lower().strip()

    # Normalize spaces
    query = re.sub(r"\s+", " ", query)

    # Convert "500 mg" -> "500mg"
    query = re.sub(
        r"(\d+)\s*mg",
        r"\1mg",
        query
    )

    # Keep letters + numbers
    words = re.findall(
        r"[a-zA-Z0-9]+",
        query
    )

    cleaned_words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    return " ".join(cleaned_words)