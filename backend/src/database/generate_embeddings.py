import csv, os, openai, numpy as np #, psycopg2, json, time
from backend.src.api import get_api_key

openai.api_key = get_api_key("OPENAI_API_KEY")

MODEL = "text-embedding-3-small"       # 1.5 ¢ per 1 k tokens, 1536-dim output :contentReference[oaicite:0]{index=0}
BATCH  = 100                            # keep requests < 2048 tokens

rows, buf = [], []
data_path = os.path.join(os.path.dirname(__file__), "../../data/movies_with_genres.csv")

print(f"Reading data from: {data_path}")

with open(data_path, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, movie in enumerate(reader):
        # Basic check for required fields
        if not all(k in movie for k in ["title", "release_date", "genres", "overview"]):
            print(f"Skipping row {i+1} due to missing fields: {movie}")
            continue
            
        text_to_embed = f'{movie["title"]} ({movie["release_date"]}) — Genres: {movie["genres"]}. Plot: {movie["overview"]}'
        buf.append(text_to_embed)
        rows.append(movie) # Append the original movie dictionary
        
        if len(buf) == BATCH:
            print(f"Processing batch ending at row {i+1}")
            try:
                resp = openai.embeddings.create(model=MODEL, input=buf)
                # Add embeddings back to the corresponding rows
                for idx, embedding_data in enumerate(resp.data):
                    row_index = len(rows) - BATCH + idx
                    rows[row_index]["embedding"] = embedding_data.embedding
            except Exception as e:
                print(f"Error processing batch ending at row {i+1}: {e}")
            finally:
                buf = [] # Clear buffer regardless of success or failure

# Process any remaining entries in buf after the loop finishes
if buf:
    print(f"Processing final batch of size {len(buf)}")
    try:
        resp = openai.embeddings.create(model=MODEL, input=buf)
        for idx, embedding_data in enumerate(resp.data):
            row_index = len(rows) - len(buf) + idx
            rows[row_index]["embedding"] = embedding_data.embedding
    except Exception as e:
        print(f"Error processing final batch: {e}")

# Verify all rows have embeddings before saving
missing_embeddings = [i for i, r in enumerate(rows) if "embedding" not in r]
if missing_embeddings:
    print(f"Warning: Rows at indices {missing_embeddings} are missing embeddings.")
    # Optionally filter out rows without embeddings or handle differently
    rows_with_embeddings = [r for r in rows if "embedding" in r]
else:
    rows_with_embeddings = rows

if not rows_with_embeddings:
    print("No rows with embeddings found to save.")
else:
    # Dump embeddings to a .npy file
    embeddings_path = os.path.join(os.path.dirname(__file__), "../../data/movies_embeddings.npy")
    print(f"Saving {len(rows_with_embeddings)} embeddings to: {embeddings_path}")
    try:
        np.save(embeddings_path, [r["embedding"] for r in rows_with_embeddings])
        print("Embeddings saved successfully.")
    except Exception as e:
        print(f"Error saving embeddings: {e}")
