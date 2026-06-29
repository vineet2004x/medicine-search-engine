import numpy as np
from sentence_transformers import SentenceTransformer
from database import Medicine

search_terms = []

# ---------------------------------------------------
# Load Sentence Transformer Model
# ---------------------------------------------------

print("Initializing SentenceTransformer model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    local_files_only=True
)

# ---------------------------------------------------
# Global In-Memory Cache
# ---------------------------------------------------

medicine_records = []

medicine_embeddings = None
uses_embeddings = None
composition_embeddings = None
manufacturer_embeddings = None


# ---------------------------------------------------
# Build Embeddings
# ---------------------------------------------------

def initialize_embeddings(db):
    """
    Load all medicines from the database and build
    multiple embedding indexes.

    1. Medicine Name + Composition
    2. Uses
    3. Composition
    4. Manufacturer
    """

    global medicine_records
    global medicine_embeddings
    global uses_embeddings
    global composition_embeddings
    global manufacturer_embeddings
    global search_terms

    print("Loading medicines from database...")

    records = db.query(Medicine).all()

    if not records:
        print("No medicines found.")

        medicine_records = []

        medicine_embeddings = None
        uses_embeddings = None
        composition_embeddings = None
        manufacturer_embeddings = None

        return

    # ---------------------------------------------------
    # Cache Database Records
    # ---------------------------------------------------

    medicine_records = [
        {
            "MedicineID": record.MedicineID,
            "MedicineName": record.MedicineName,
            "Composition": record.Composition,
            "Uses": record.Uses,
            "SideEffects": record.SideEffects,
            "Manufacturer": record.Manufacturer
        }
        for record in records
    ]

    # ---------------------------------------------------
    # Create Documents
    # ---------------------------------------------------

    medicine_documents = [
        (
            f"Medicine: {record.MedicineName or ''}. "
            f"Composition: {record.Composition or ''}. "
            f"Uses: {record.Uses or ''}. "
            f"Manufacturer: {record.Manufacturer or ''}"
        )
        for record in records
    ]

    uses_documents = [
        record.Uses or ""
        for record in records
    ]

    composition_documents = [
        record.Composition or ""
        for record in records
    ]

    manufacturer_documents = [
        record.Manufacturer or ""
        for record in records
    ]
    search_terms = list(
        set(
            [r.MedicineName for r in records if r.MedicineName] +
            [r.Composition for r in records if r.Composition] +
            [r.Manufacturer for r in records if r.Manufacturer]
        )
    )

    # ---------------------------------------------------
    # Generate Medicine Embeddings
    # ---------------------------------------------------

    print("Generating Medicine embeddings...")

    medicine_embeddings = np.array(
        model.encode(
            medicine_documents,
            show_progress_bar=True,
            batch_size=64
        )
    )

    # ---------------------------------------------------
    # Generate Uses Embeddings
    # ---------------------------------------------------

    print("Generating Uses embeddings...")

    uses_embeddings = np.array(
        model.encode(
            uses_documents,
            show_progress_bar=True,
            batch_size=64
        )
    )

    # ---------------------------------------------------
    # Generate Composition Embeddings
    # ---------------------------------------------------

    print("Generating Composition embeddings...")

    composition_embeddings = np.array(
        model.encode(
            composition_documents,
            show_progress_bar=True,
            batch_size=64
        )
    )

    # ---------------------------------------------------
    # Generate Manufacturer Embeddings
    # ---------------------------------------------------

    print("Generating Manufacturer embeddings...")

    manufacturer_embeddings = np.array(
        model.encode(
            manufacturer_documents,
            show_progress_bar=True,
            batch_size=64
        )
    )

    # ---------------------------------------------------
    # Done
    # ---------------------------------------------------

    print("=" * 50)
    print(f"Loaded {len(medicine_records)} medicines.")
    print("Medicine Embeddings       ✓")
    print("Uses Embeddings           ✓")
    print("Composition Embeddings    ✓")
    print("Manufacturer Embeddings   ✓")
    print("Embedding cache ready.")
    print("=" * 50)


# ---------------------------------------------------
# Query Embedding
# ---------------------------------------------------

def get_query_embedding(query: str):
    """
    Convert a user query into a vector embedding.
    """

    return model.encode(
        query,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )