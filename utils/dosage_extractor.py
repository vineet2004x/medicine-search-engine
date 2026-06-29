import re


def extract_dosage(query: str):
    """
    Extract dosage from user query.

    Examples
    --------
    paracetamol 500 mg -> 500
    metformin 1000mg -> 1000
    dolo 650 -> 650
    """

    query = query.lower()

    # Match:
    # 500
    # 500mg
    # 500 mg
    # 650 MG

    match = re.search(r"(\d+)\s*(mg)?", query)

    if match:
        return match.group(1)

    return None