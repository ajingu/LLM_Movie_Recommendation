import chromadb
import openai
import os
import argparse
from backend.src.api import get_api_key

# --- Configuration ---
MODEL = "text-embedding-3-small"

def query_vector_database(query_text: str, n_results: int = 5):
    """Queries the vector database for movies similar to the query text.

    Args:
        query_text: The text query to search for.
        n_results: The number of similar results to return.

    Returns:
        A list of dictionaries, where each dictionary contains the 
        metadata of a matching movie and its similarity distance.
        Returns None if an error occurs.
    """
    print(f"Querying database for: \"{query_text}\" (Top {n_results} results)")

    # --- Get API Key ---
    try:
        openai.api_key = get_api_key("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found.")
    except Exception as e:
        print(f"Error getting API key: {e}")
        return None

    # --- Database Configuration ---
    script_dir = os.path.dirname(__file__)
    db_dir = os.path.join(script_dir, "../../chroma_db")
    collection_name = "movies"

    if not os.path.exists(db_dir):
        print(f"Error: ChromaDB directory not found at {db_dir}. Please run setup_vector_db.py first.")
        return None

    # --- Initialize ChromaDB Client ---
    print("Initializing ChromaDB client...")
    try:
        client = chromadb.PersistentClient(path=db_dir)
        collection = client.get_collection(name=collection_name)
        print(f"Connected to collection '{collection_name}' with {collection.count()} items.")
    except Exception as e:
        print(f"Error connecting to ChromaDB collection: {e}")
        return None

    # --- Generate Query Embedding ---
    print("Generating embedding for the query...")
    try:
        response = openai.embeddings.create(model=MODEL, input=[query_text])
        query_embedding = response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

    # --- Query ChromaDB ---
    print("Querying the collection...")
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['metadatas', 'distances'] # Include metadata and distances
        )
    except Exception as e:
        print(f"Error querying ChromaDB collection: {e}")
        return None

    # --- Format and Return Results ---
    if not results or not results.get('ids') or not results['ids'][0]:
        print("No results found for the query.")
        return []

    formatted_results = []
    ids = results['ids'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for i in range(len(ids)):
        result = metadatas[i]
        result['distance'] = distances[i]
        result['id'] = ids[i]
        formatted_results.append(result)
        
    print(f"Found {len(formatted_results)} results.")
    return formatted_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the movie vector database.")
    parser.add_argument("query", type=str, help="The text query to search for.")
    parser.add_argument("-n", "--n_results", type=int, default=5, help="Number of results to return.")
    
    args = parser.parse_args()

    search_results = query_vector_database(args.query, args.n_results)

    if search_results:
        print("\n--- Search Results ---")
        for i, result in enumerate(search_results):
            print(f"{i+1}. Title: {result.get('title', 'N/A')}")
            print(f"   Release Date: {result.get('release_date', 'N/A')}")
            print(f"   Genres: {result.get('genres', 'N/A')}")
            print(f"   Distance: {result['distance']:.4f}") # Lower distance means more similar
            print(f"   Overview: {result.get('overview', 'N/A')[:150]}...") # Truncated overview
            print("---")
    elif search_results == []:
         print("No matching movies found.")
    else:
        print("Query failed.") 