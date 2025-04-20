from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import openai
import os
import chromadb
import re
import datetime

# Import utility functions (assuming they handle API key loading and DB querying)
from backend.src.api import get_api_key
# Re-use or adapt the core query logic
from backend.src.database.query_vector_db import query_vector_database 
# Or potentially directly use chromadb client and embedding generation here
# import chromadb 

router = APIRouter()

MODEL = "text-embedding-3-small" # Same model for consistency
LLM_MODEL = "gpt-3.5-turbo"       # Conversation processing model

# --- Pydantic Models ---
class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant' (or 'system')
    content: str

class ChatSearchQuery(BaseModel):
    messages: List[ChatMessage] = Field(..., example=[
        {"role": "user", "content": "Suggest some sci-fi movies"},
        # {"role": "assistant", "content": "Okay, finding sci-fi..."} # Example history
    ])
    n_results: Optional[int] = Field(5, ge=1, le=20, example=5)

# Assuming SearchResultItem and SearchResponse are defined elsewhere or we redefine
# For simplicity, let's reuse the structure implicitly via query_vector_database return type
# Or define explicitly if needed:
class ChatSearchResultItem(BaseModel):
    id: str
    title: Optional[str] = None
    release_date: Optional[str] = None
    genres: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    distance: float

class ChatSearchResponse(BaseModel):
    results: List[ChatSearchResultItem]

class ChatSearchFilters(BaseModel):
    """Structure to hold extracted filters from conversation"""
    main_query: str = ""
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    include_genres: List[str] = []
    exclude_genres: List[str] = []

# --- Helper Function (Basic Conversation Embedding) ---
def create_embedding_from_conversation(messages: List[ChatMessage]) -> Optional[List[float]]:
    """Creates a single embedding representing the conversation context.
       Basic approach: Concatenate recent messages.
       A better approach would involve LLM summarization or prompt engineering.
    """
    # Combine the content of the messages into a single string
    # Consider using only the last few messages for context if history grows large
    conversation_text = " ".join([msg.content for msg in messages])
    
    if not conversation_text:
        return None
        
    try:
        openai.api_key = get_api_key("OPENAI_API_KEY")
        response = openai.embeddings.create(model=MODEL, input=[conversation_text])
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding from conversation: {e}")
        return None

# --- Process conversation with OpenAI ---
def process_conversation_with_llm(messages: List[ChatMessage]) -> ChatSearchFilters:
    """Use LLM to extract search parameters from conversation history"""
    
    try:
        openai.api_key = get_api_key("OPENAI_API_KEY")
        
        # Setup system prompt to instruct LLM how to interpret conversation
        system_prompt = """
        You are a movie recommendation system. Extract search filters from the conversation.
        Pay special attention to:
        1. Temporal constraints (e.g., "before 2015", "from the 90s")
        2. Regional cinema references (e.g., "Indian movies", "Bollywood")
        3. Genre preferences (both inclusion and exclusion)

        Important notes:
        - When users mention "Indian movies" or "Bollywood", add "indian" to the include_genres
        - When users mention time periods, extract specific year ranges
        - Focus on the full conversation context, not just the latest message

        Return a JSON object with these fields:
        {
          "main_query": "Main search topic, keywords or theme",
          "min_year": null or integer (minimum release year),
          "max_year": null or integer (maximum release year),
          "include_genres": ["Genre1", "Genre2", etc],
          "exclude_genres": ["Genre1", "Genre2", etc]
        }
        """
        
        # Create messages array for the OpenAI API
        api_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})
            
        # Request completion from OpenAI
        response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=api_messages,
            response_format={"type": "json_object"}
        )
        
        # Extract response
        llm_response = response.choices[0].message.content
        
        # Parse JSON response (with error handling)
        import json
        try:
            filters = json.loads(llm_response)
            return ChatSearchFilters(
                main_query=filters.get("main_query", ""),
                min_year=filters.get("min_year"),
                max_year=filters.get("max_year"),
                include_genres=filters.get("include_genres", []),
                exclude_genres=filters.get("exclude_genres", [])
            )
        except json.JSONDecodeError:
            print(f"Error decoding JSON from LLM response: {llm_response}")
            # Fallback to basic filters extraction
            return extract_filters_fallback(messages)
            
    except Exception as e:
        print(f"LLM processing error: {e}")
        # Fallback to basic filters extraction when API fails
        return extract_filters_fallback(messages)

# --- Basic Fallback Filter Extraction ---
def extract_filters_fallback(messages: List[ChatMessage]) -> ChatSearchFilters:
    """Extract filters using regex as a fallback when LLM API fails"""
    # Combine all user messages
    combined_text = " ".join([m.content for m in messages if m.role == "user"])
    
    # Initialize filters
    filters = ChatSearchFilters()
    
    # Extract main query (use the latest user message as a simple approach)
    filters.main_query = messages[-1].content if messages and messages[-1].role == "user" else combined_text
    
    # Extract year ranges with regex - more comprehensive patterns
    before_year_match = re.search(r'(?:before|prior to|earlier than|until|up to)\s+(\d{4})', combined_text, re.IGNORECASE)
    if before_year_match:
        filters.max_year = int(before_year_match.group(1))

    after_year_match = re.search(r'(?:after|since|from|later than|newer than)\s+(\d{4})', combined_text, re.IGNORECASE)
    if after_year_match:
        filters.min_year = int(after_year_match.group(1))
    
    # Look for "from YYYY to YYYY" pattern
    year_range_match = re.search(r'(?:from|between)\s+(\d{4})(?:\s+to|\s*-\s*|\s+and\s+)(\d{4})', combined_text, re.IGNORECASE)
    if year_range_match:
        filters.min_year = int(year_range_match.group(1))
        filters.max_year = int(year_range_match.group(2))
    
    # Look for "in the 70s/80s/90s" type patterns
    decade_match = re.search(r'(?:in\s+the\s+|from\s+the\s+|)(\d0)s', combined_text, re.IGNORECASE)
    if decade_match:
        decade = int(decade_match.group(1))
        filters.min_year = 1900 + decade
        filters.max_year = 1900 + decade + 9

    # Look for specific years mentioned 
    specific_year_match = re.search(r'(?:in|from|released\s+in)\s+(\d{4})\b', combined_text, re.IGNORECASE)
    if specific_year_match and not filters.min_year and not filters.max_year:
        year = int(specific_year_match.group(1))
        # Assuming we want movies from that year
        filters.min_year = year
        filters.max_year = year
    
    # Extract genres (very basic approach)
    # Common movie genres to scan for
    common_genres = [
        "action", "adventure", "animation", "comedy", "crime", "documentary", "drama", 
        "family", "fantasy", "history", "horror", "music", "mystery", "romance", 
        "science fiction", "sci-fi", "thriller", "war", "western", "indian", "bollywood"
    ]
    
    # Check for genre mentions
    for genre in common_genres:
        # Check for inclusion/exclusion keywords
        if re.search(rf'\b{genre}\b', combined_text, re.IGNORECASE):
            # Check for exclusion patterns like "not horror" or "except comedy"
            exclusion_pattern = rf'(not|except|don\'t\s+want|no)\s+{genre}'
            if re.search(exclusion_pattern, combined_text, re.IGNORECASE):
                filters.exclude_genres.append(genre)
            else:
                filters.include_genres.append(genre)
    
    return filters

# --- Apply filters to search results ---
def apply_filters(results: List[ChatSearchResultItem], filters: ChatSearchFilters) -> List[ChatSearchResultItem]:
    """Apply extracted filters to the search results"""
    filtered_results = []
    
    for item in results:
        # Skip if no release_date
        if not item.release_date:
            continue
            
        # Extract year from release_date (format: YYYY-MM-DD)
        try:
            release_year = int(item.release_date.split('-')[0])
        except (ValueError, IndexError):
            release_year = 0
            
        # Check year constraints
        if filters.min_year and release_year < filters.min_year:
            continue
            
        if filters.max_year and release_year > filters.max_year:
            continue
            
        # Convert genres to lowercase for case-insensitive matching
        item_genres_lower = item.genres.lower() if item.genres else ""
        
        # Check genre inclusion for special cases like "indian" which might not be in genres field
        include_match = True
        if filters.include_genres:
            # Special handling for "indian" genre which might be in title or overview
            if "indian" in filters.include_genres or "bollywood" in filters.include_genres:
                indian_match = False
                # Check if "indian" or related terms are in any fields
                if item.genres and any(term in item.genres.lower() for term in ["indian", "bollywood", "hindi"]):
                    indian_match = True
                elif item.title and any(term in item.title.lower() for term in ["indian", "bollywood", "hindi"]):
                    indian_match = True
                elif item.overview and any(term in item.overview.lower() for term in ["indian", "bollywood", "hindi"]):
                    indian_match = True
                    
                # If "indian" is requested but no other genres, only use indian_match
                if len(filters.include_genres) == 1 and ("indian" in filters.include_genres or "bollywood" in filters.include_genres):
                    include_match = indian_match
                else:
                    # Otherwise include indian matching with regular genre matching
                    other_genres = [g for g in filters.include_genres if g not in ["indian", "bollywood"]]
                    regular_match = not other_genres or any(genre.lower() in item_genres_lower for genre in other_genres)
                    include_match = indian_match or regular_match
            else:
                # Regular genre matching for non-indian specific searches
                include_match = any(genre.lower() in item_genres_lower for genre in filters.include_genres)
        
        # Check genre exclusion
        exclude_match = False
        if filters.exclude_genres:
            exclude_match = any(genre.lower() in item_genres_lower for genre in filters.exclude_genres)
            
        # Add item only if it matches inclusion criteria and doesn't match exclusion criteria
        if include_match and not exclude_match:
            filtered_results.append(item)
            
    return filtered_results

# --- Create embedding from main query ---
def create_embedding_from_query(query_text: str) -> Optional[List[float]]:
    """Creates a single embedding for the main query text"""
    
    if not query_text:
        return None
        
    try:
        openai.api_key = get_api_key("OPENAI_API_KEY")
        response = openai.embeddings.create(model=MODEL, input=[query_text])
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding from query: {e}")
        return None

# --- API Endpoint ---
@router.post("/chat_search", response_model=ChatSearchResponse, tags=["Chat Search"])
async def chat_search_movies(chat_query: ChatSearchQuery = Body(...)):
    """Receives conversation history and returns relevant movie recommendations."""
    if not chat_query.messages:
        raise HTTPException(status_code=400, detail="No messages provided in the chat query.")

    # 1. Process conversation to extract filters
    print("Processing conversation to extract search parameters...")
    filters = process_conversation_with_llm(chat_query.messages)
    print(f"Extracted filters: {filters}")
    
    # 2. Create embedding based on main query
    print(f"Generating embedding for main query: {filters.main_query}")
    query_embedding = create_embedding_from_query(filters.main_query)

    if query_embedding is None:
        raise HTTPException(status_code=500, detail="Failed to generate embedding for search query.")

    # 3. Query the vector database
    print(f"Querying vector database...")
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        db_dir = os.path.join(script_dir, "../../chroma_db") 
        collection_name = "movies"
        
        if not os.path.exists(db_dir):
             raise HTTPException(status_code=500, detail=f"ChromaDB directory not found at {db_dir}. Run setup first.")

        client = chromadb.PersistentClient(path=db_dir)
        collection = client.get_collection(name=collection_name)

        # Request extra results to have enough after filtering
        multiplier = 3 if (filters.min_year or filters.max_year or filters.include_genres or filters.exclude_genres) else 1
        n_results = chat_query.n_results * multiplier
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, 50),  # Cap at 50 to prevent excessive results
            include=['metadatas', 'distances'] 
        )
    except Exception as e:
        print(f"Error querying ChromaDB collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to query vector database.")

    # 4. Format initial results
    if not results or not results.get('ids') or not results['ids'][0]:
        return ChatSearchResponse(results=[]) 

    initial_results = []
    ids = results['ids'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for i in range(len(ids)):
        item = metadatas[i]
        item_dict = dict(item)  # Convert to dict for easier manipulation
        item_dict['distance'] = distances[i]
        item_dict['id'] = ids[i]
        initial_results.append(ChatSearchResultItem(**item_dict))
    
    # 5. Apply filters to results
    print(f"Applying filters to {len(initial_results)} initial results...")
    filtered_results = apply_filters(initial_results, filters)
    
    # 6. Limit to requested number and return
    final_results = filtered_results[:chat_query.n_results]
    print(f"Returning {len(final_results)} filtered results out of {len(initial_results)} initial matches.")
    
    return ChatSearchResponse(results=final_results) 