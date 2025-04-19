import chromadb
import csv
import numpy as np
import os

def setup_vector_database():
    # --- Configuration ---
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, "../../data")
    db_dir = os.path.join(script_dir, "../../chroma_db") # Directory to store DB data
    csv_path = os.path.join(data_dir, "movies_with_genres.csv")
    npy_path = os.path.join(data_dir, "movies_embeddings.npy")
    collection_name = "movies"

    print("Starting vector database setup...")

    # --- Load Data ---
    print(f"Loading data from {csv_path}...")
    movies = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic validation
                if not all(k in row for k in ['id', 'title', 'release_date', 'genres', 'overview', 'poster_path']):
                    print(f"Warning: Skipping row due to missing keys: {row}")
                    continue
                movies.append(row)
    except FileNotFoundError:
        print(f"Error: Data file not found at {csv_path}")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    print(f"Loaded {len(movies)} movie records.")

    # --- Load Embeddings ---
    print(f"Loading embeddings from {npy_path}...")
    try:
        embeddings = np.load(npy_path)
    except FileNotFoundError:
        print(f"Error: Embeddings file not found at {npy_path}")
        return
    except Exception as e:
        print(f"Error loading embeddings file: {e}")
        return
        
    print(f"Loaded {embeddings.shape[0]} embeddings with dimension {embeddings.shape[1]}.")

    # --- Data Consistency Check ---
    if len(movies) != embeddings.shape[0]:
        print(f"Error: Mismatch between number of movies ({len(movies)}) and embeddings ({embeddings.shape[0]}). Aborting.")
        return

    # --- Initialize ChromaDB ---
    print(f"Initializing ChromaDB client with persistence path: {db_dir}")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    client = chromadb.PersistentClient(path=db_dir)

    # --- Create or Get Collection ---
    print(f"Creating or getting collection: {collection_name}")
    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} # Use cosine distance
        )
    except Exception as e:
        print(f"Error creating/getting ChromaDB collection: {e}")
        return

    # --- Prepare Data for ChromaDB ---
    ids = []
    metadatas = []
    embeddings_list = []

    for i, movie in enumerate(movies):
        ids.append(str(movie['id'])) # IDs must be strings
        metadatas.append({
            "title": movie.get('title', ''),
            "release_date": movie.get('release_date', ''),
            "genres": movie.get('genres', ''),
            "overview": movie.get('overview', ''),
            "poster_path": movie.get('poster_path', '')
        })
        embeddings_list.append(embeddings[i].tolist()) # Convert numpy array to list

    # --- Add Data to Collection (in batches) ---
    batch_size = 100 # Adjust batch size as needed
    num_batches = (len(ids) + batch_size - 1) // batch_size
    print(f"Adding {len(ids)} items to collection in {num_batches} batches...")

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(ids))
        print(f"Adding batch {i+1}/{num_batches} (items {start_idx+1}-{end_idx})...")
        
        batch_ids = ids[start_idx:end_idx]
        batch_embeddings = embeddings_list[start_idx:end_idx]
        batch_metadatas = metadatas[start_idx:end_idx]
        
        try:
            collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas
            )
        except Exception as e:
            print(f"Error adding batch {i+1} to ChromaDB: {e}")
            # Decide whether to continue or stop on error
            # return 

    print("-----------------------------------------")
    print(f"Successfully added {collection.count()} items to the '{collection_name}' collection.")
    print(f"Database stored at: {db_dir}")
    print("-----------------------------------------")

if __name__ == "__main__":
    setup_vector_database() 