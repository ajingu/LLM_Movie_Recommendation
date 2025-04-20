from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import openai
import os
import chromadb

# Import utility functions (assuming they handle API key loading and DB querying)
from backend.src.api import get_api_key
# Re-use or adapt the core query logic
from backend.src.database.query_vector_db import query_vector_database 
# Or potentially directly use chromadb client and embedding generation here
# import chromadb 

router = APIRouter()

MODEL = "text-embedding-3-small" # Same model for consistency

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

# --- API Endpoint ---
@router.post("/chat_search", response_model=ChatSearchResponse, tags=["Chat Search"])
async def chat_search_movies(chat_query: ChatSearchQuery = Body(...)):
    """Receives conversation history and returns relevant movie recommendations."""
    if not chat_query.messages:
        raise HTTPException(status_code=400, detail="No messages provided in the chat query.")

    # 1. Create embedding based on conversation context (using our basic helper)
    # For this simple version, we directly embed the concatenated text.
    # A real app would likely use an LLM to interpret the conversation
    # and generate a more refined query/summary before embedding.
    print(f"Generating embedding for conversation context...")
    query_embedding = create_embedding_from_conversation(chat_query.messages)

    if query_embedding is None:
        raise HTTPException(status_code=500, detail="Failed to generate embedding for conversation.")

    # 2. Query the vector database (reusing the existing function's logic)
    # We need to adapt query_vector_database or replicate its core logic here
    # to accept an embedding directly instead of text.
    
    # --- Replicated/Adapted Query Logic --- 
    # This part should ideally be refactored into a shared utility 
    # function that both endpoints can use.
    print(f"Querying vector database with generated embedding...")
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__)) # Get dir of this file
        # Navigate up correctly: endpoints -> src -> backend -> chroma_db
        db_dir = os.path.join(script_dir, "../../chroma_db") 
        collection_name = "movies"
        
        if not os.path.exists(db_dir):
             raise HTTPException(status_code=500, detail=f"ChromaDB directory not found at {db_dir}. Run setup first.")

        client = chromadb.PersistentClient(path=db_dir)
        collection = client.get_collection(name=collection_name)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=chat_query.n_results,
            include=['metadatas', 'distances'] 
        )
    except Exception as e:
        print(f"Error querying ChromaDB collection in chat search: {e}")
        raise HTTPException(status_code=500, detail="Failed to query vector database.")
    # --- End Replicated/Adapted Query Logic --- 

    # 3. Format and return results
    if not results or not results.get('ids') or not results['ids'][0]:
        return ChatSearchResponse(results=[]) # Return empty list if no results

    formatted_results = []
    ids = results['ids'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for i in range(len(ids)):
        item = metadatas[i]
        item['distance'] = distances[i]
        item['id'] = ids[i]
        formatted_results.append(ChatSearchResultItem(**item))
        
    print(f"Found {len(formatted_results)} results via chat query.")
    return ChatSearchResponse(results=formatted_results) 