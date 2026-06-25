from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

import database
import embeddings
import search

# 1. Define the Lifespan Context Manager
# This handles the startup and shutdown tasks.
# On startup, we initialize the DB, seed data if empty, and load/generate embeddings in memory.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup: Initializing database...")
    # Initialize and seed the SQLite database
    database.init_db()
    
    print("Application Startup: Building in-memory embeddings cache...")
    db_session = database.SessionLocal()
    try:
        # Load records and pre-compute embeddings
        embeddings.initialize_embeddings(db_session)
    finally:
        db_session.close()
        
    yield
    
    print("Application Shutdown: Cleaning up...")

# 2. Instantiate FastAPI
app = FastAPI(
    title="AI Medicine Search API",
    description=(
        "A simple, lightweight API demonstrating semantic search and fuzzy spelling correction "
        "on medicine records using SQLite, SQLAlchemy, Sentence Transformers, and RapidFuzz."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# 3. Define Pydantic Request Models
class SearchRequest(BaseModel):
    query: str

# 4. Define Endpoints

@app.get("/medicines", tags=["Medicines"])
def get_medicines(db: Session = Depends(database.get_db)):
    """
    Fetch all medicine records currently stored in the SQLite database.
    """
    try:
        records = db.query(database.Medicine).all()
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database retrieval failed: {str(e)}"
        )

@app.post("/generate_embeddings", tags=["Embeddings"])
def generate_embeddings(db: Session = Depends(database.get_db)):
    """
    Manually trigger regeneration of embeddings and refresh the in-memory cache.
    Use this if you add new medicine records directly to the database.
    """
    try:
        embeddings.initialize_embeddings(db)
        return {
            "status": "success",
            "message": f"Successfully regenerated embeddings for {len(embeddings.medicine_records)} medicine records."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate embeddings: {str(e)}"
        )

@app.post("/search", tags=["Search"])
def search_medicine(request: SearchRequest, db: Session = Depends(database.get_db)):
    """
    Perform a medicine search using:
    1. RapidFuzz to correct spelling mistakes of any medicine names in the query.
    2. Sentence Transformers to create an embedding of the query.
    3. Cosine similarity to compare the query vector with cached medicine vectors.
    
    Returns the single best matching medicine record and its similarity score.
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty."
        )

    try:
        # Run search orchestration
        search_result = search.search_medicines(query_text)
        return search_result
    except ValueError as val_err:
        # Raised if embeddings are not initialized
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

# Optional entry point for direct script execution
if __name__ == "__main__":
    import uvicorn
    # Start the Uvicorn server on port 8000
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
