import numpy as np
from sentence_transformers import SentenceTransformer
from database import Medicine

# 1. Initialize the SentenceTransformer model globally.
# The 'all-MiniLM-L6-v2' model converts text into 384-dimensional vector embeddings.
print("Initializing SentenceTransformer model ('all-MiniLM-L6-v2')...")
model = SentenceTransformer(
    'all-MiniLM-L6-v2',
    local_files_only=True
)

# 2. In-memory cache for loaded medicine records and their corresponding embeddings.
# Storing these in memory allows for very fast similarity calculations.
medicine_records = []
medicine_embeddings = None  # Will be a numpy array of shape (N, 384)

def convert_to_document(medicine):
    return (
        f"Medicine Name: {medicine.MedicineName or ''}. "
        f"Used For: {medicine.Uses or ''}. "
        f"Treatment: {medicine.Uses or ''}. "
        f"Indication: {medicine.Uses or ''}. "
        f"Composition: {medicine.Composition or ''}. "
        f"Manufacturer: {medicine.Manufacturer or ''}. "
        f"Side Effects: {medicine.SideEffects or ''}."
    )

def initialize_embeddings(db):
    """
    Retrieves all medicines from the database, converts them to text documents,
    generates their embeddings, and caches the results in memory.
    """
    global medicine_records, medicine_embeddings

    print("Querying medicines from database...")
    records = db.query(Medicine).all()

    if not records:
        print("Warning: No medicines found in database to generate embeddings.")
        medicine_records = []
        medicine_embeddings = None
        return

    # Transform database models into a list of serialized dictionaries
    medicine_records = [
        {
            "MedicineID": r.MedicineID,
            "MedicineName": r.MedicineName,
            "Composition": r.Composition,
            "Uses": r.Uses,
            "SideEffects": r.SideEffects,
            "Manufacturer": r.Manufacturer
        }
        for r in records
    ]

    # Generate text documents for each medicine
    documents = [convert_to_document(r) for r in records]

    print(f"Generating embeddings for {len(documents)} medicines...")

    embeddings = model.encode(
        documents,
        show_progress_bar=True,
        batch_size=64
    )

    # Store in memory
    medicine_embeddings = np.array(embeddings)

    print("In-memory embeddings cache successfully updated.")

def get_query_embedding(query: str):
    """
    Generates a 384-dimensional vector embedding for a user's search query.
    """
    return model.encode(query, show_progress_bar=False)
