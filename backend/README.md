# LLM Mobile Backend

A FastAPI-based backend server for the LLM Mobile application.

## Setup

1.  **Create Environment**: Create a conda environment and activate it:
    ```bash
    conda create -n llm_mobile python=3.11  # Or your preferred Python 3.8+ version
    conda activate llm_mobile
    ```

2.  **Install Dependencies**: Install required Python packages.
    ```bash
    # Install FastAPI server requirements
    pip install -r requirements.txt
    # Install requirements for database scripts
    pip install chromadb openai numpy python-dotenv requests 
    ```
    *Note: Ensure `pip` installs packages into your conda environment.*

3.  **API Keys**: Create a `.env` file in the `backend` directory with your API keys:
    ```env
    TMDB_API_KEY="your_themoviedb_api_key"
    OPENAI_API_KEY="your_openai_api_key"
    ```

## Database Setup & Usage

These scripts are located in `backend/src/database` and should be run from the project root (`llm_mobile/`) using the `python -m` flag.

1.  **Fetch Movie Data** (`fetch_data_from_tmdb.py`):
    *   **Purpose**: Downloads movie data from The Movie Database (TMDB) API, fetches genre names, handles duplicates, and saves the results to `backend/data/movies_with_genres.csv`.
    *   **Requires**: `TMDB_API_KEY` in `.env`.
    *   **Usage**:
        ```bash
        python -m backend.src.database.fetch_data_from_tmdb
        ```

2.  **Generate Embeddings** (`generate_embeddings.py`):
    *   **Purpose**: Reads the movie data from `movies_with_genres.csv`, creates text embeddings for each movie using the OpenAI API, and saves them to `backend/data/movies_embeddings.npy`.
    *   **Requires**: `OPENAI_API_KEY` in `.env` and the `movies_with_genres.csv` file created by the previous step.
    *   **Usage**:
        ```bash
        python -m backend.src.database.generate_embeddings
        ```

3.  **Setup Vector Database** (`setup_vector_db.py`):
    *   **Purpose**: Initializes a ChromaDB vector database, reads the movie data and embeddings, and populates the database. The database is stored persistently in `backend/chroma_db/`.
    *   **Requires**: `movies_with_genres.csv` and `movies_embeddings.npy` in `backend/data/`.
    *   **Usage**:
        ```bash
        python -m backend.src.database.setup_vector_db
        ```

4.  **Query Vector Database (Standalone)** (`query_vector_db.py`):
    *   **Purpose**: Allows you to test the vector search directly from the command line without running the server. Takes a text query and returns the most similar movies.
    *   **Requires**: The ChromaDB database created by the previous step and `OPENAI_API_KEY` in `.env`.
    *   **Usage**:
        ```bash
        python -m backend.src.database.query_vector_db "your search query here" -n 5 
        ```

## Running the Server

Make sure you have activated the conda environment (`conda activate llm_mobile`) and are in the project root (`llm_mobile/`). Run the server using the Uvicorn executable from your *conda environment's bin directory*:

```bash
# Example (adjust path based on your conda installation)
/path/to/your/conda/envs/llm_mobile/bin/uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000

# Or find the path dynamically
PYTHON_DIR=$(dirname $(which python))
$PYTHON_DIR/uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Endpoints

-   `GET /`: Welcome message.
-   `GET /health`: Health check endpoint.
-   `POST /api/search`: Performs a semantic search for movies based on a text query.
    *   **Request Body (JSON)**:
        ```json
        {
            "query_text": "string",
            "n_results": integer (optional, default: 5)
        }
        ```
    *   **Example Usage (curl)**:
        ```bash
        curl -X POST "http://localhost:8000/api/search" \
             -H "Content-Type: application/json" \
             -d '{
                   "query_text": "space movies with aliens",
                   "n_results": 3
                 }'
        ```
    *   **Response Body (JSON)**: A list of matching movie objects including metadata and similarity distance.

## API Documentation

Once the server is running, you can access interactive API documentation:

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc` 