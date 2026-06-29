from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

import database
import embeddings
import search


# --------------------------------------------------------
# Logging Configuration
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------
# Lifespan Events
# --------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Application Startup: Initializing database...")

    database.init_db()

    logger.info("Application Startup: Building in-memory embeddings cache...")

    db_session = database.SessionLocal()

    try:
        embeddings.initialize_embeddings(db_session)

    finally:
        db_session.close()

    logger.info("Application Startup Complete.")

    yield

    logger.info("Application Shutdown: Cleaning up...")


# --------------------------------------------------------
# FastAPI App
# --------------------------------------------------------

app = FastAPI(
    title="AI Medicine Search API",
    description="""
AI-powered Medicine Search Engine

Features:
- Semantic Search using Sentence Transformers
- Fuzzy Medicine Name Matching
- SQLite Database
- Embedding-based Retrieval
- Query Cleaning
""",
    version="1.0.0",
    lifespan=lifespan
)


# --------------------------------------------------------
# Request Models
# --------------------------------------------------------

class SearchRequest(BaseModel):
    query: str


# --------------------------------------------------------
# Health Check
# --------------------------------------------------------

@app.get("/", tags=["Health"])
def health_check():
    """
    Health Check Endpoint
    """

    return {
        "status": "running",
        "application": "AI Medicine Search API"
    }


# --------------------------------------------------------
# Get Medicines
# --------------------------------------------------------

@app.get("/medicines", tags=["Medicines"])
def get_medicines(db: Session = Depends(database.get_db)):
    """
    Return all medicines stored in the database.
    """

    try:

        medicines = db.query(database.Medicine).all()

        return medicines

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database retrieval failed: {str(e)}"
        )


# --------------------------------------------------------
# Regenerate Embeddings
# --------------------------------------------------------

@app.post("/embeddings/refresh", tags=["Embeddings"])
def regenerate_embeddings(
    db: Session = Depends(database.get_db)
):
    """
    Refresh all medicine embeddings.
    Useful after inserting new medicines.
    """

    try:

        embeddings.initialize_embeddings(db)

        return {
            "status": "success",
            "message": f"{len(embeddings.medicine_records)} medicines embedded successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding generation failed: {str(e)}"
        )


# --------------------------------------------------------
# Search Medicines
# --------------------------------------------------------

@app.post("/search", tags=["Search"])
def search_medicine(request: SearchRequest):
    """
    Intelligent Medicine Search

    Pipeline:
    1. Correct spelling mistakes
    2. Remove stop words
    3. Generate query embedding
    4. Compare with medicine embeddings
    5. Return Top Matches
    """

    query_text = request.query.strip()

    # Empty query validation
    if not query_text:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty."
        )

    # Maximum query length
    if len(query_text) > 200:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query is too long. Maximum length is 200 characters."
        )

    logger.info(f"Incoming Search Query: {query_text}")

    try:

        result = search.search_medicines(query_text)

        logger.info("Search completed successfully.")

        return result

    except ValueError as e:

        logger.error(str(e))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:

        logger.exception("Unexpected search error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# --------------------------------------------------------
# Run Server
# --------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
