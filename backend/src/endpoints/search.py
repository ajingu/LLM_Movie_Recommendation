from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the query function from your database script
from backend.src.database.query_vector_db import query_vector_database

# Create a router
router = APIRouter()

# --- Pydantic Models for Request and Response ---
class SearchQuery(BaseModel):
    query_text: str = Field(..., example="space movie with aliens")
    n_results: Optional[int] = Field(5, ge=1, le=20, example=5)

class SearchResultItem(BaseModel):
    id: str
    title: Optional[str] = None
    release_date: Optional[str] = None
    genres: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResultItem]

# --- API Endpoint Definition ---
@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_movies(search_query: SearchQuery = Body(...)):
    """Receives a text query and returns the most similar movies from the vector database."""
    try:
        # Call the existing query function
        results = query_vector_database(
            query_text=search_query.query_text,
            n_results=search_query.n_results
        )

        if results is None:
            # query_vector_database prints errors, raise a generic server error
            raise HTTPException(status_code=500, detail="Failed to query the vector database.")
        
        if not results:
            return SearchResponse(results=[]) # Return empty list if no results found
        
        # Format results according to the response model
        formatted_results = [SearchResultItem(**item) for item in results]
        return SearchResponse(results=formatted_results)

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error during search: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the search.") 