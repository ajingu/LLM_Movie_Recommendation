# LLM Mobile Movie Search

This is a full-stack mobile application that leverages Large Language Models (LLMs) and vector embeddings to provide a powerful semantic search and conversational recommendation engine for movies.

https://github.com/user-attachments/assets/73c28a2f-a09e-41fb-bff7-5030ced052a3

## 🌟 Overview

The project consists of a React Native (Expo) frontend and a Python (FastAPI) backend. It offers two primary ways for users to discover movies:

1.  **Semantic Search:** A traditional search screen where users can type in a description, a theme, or a vague idea of a movie, and the system will find the most relevant matches based on semantic meaning, not just keywords.
2.  **Conversational Chat:** A chat interface where users can interact with an AI assistant. Users can ask for recommendations, refine their search, and get movie suggestions in a natural, conversational flow.

## ✨ Features

- **Backend:**
  - Built with **FastAPI** for high performance.
  - Uses **The Movie Database (TMDB)** as the data source for movies.
  - Generates vector embeddings for movie overviews for semantic search.
  - `/api/search` endpoint for direct semantic search.
  - `/api/chat_search` endpoint that integrates with an LLM to provide conversational responses and tool-use (movie search).
- **Frontend:**
  - Cross-platform mobile app built with **React Native & Expo**.
  - Written in **TypeScript** for type safety and better developer experience.
  - Tab-based navigation using **Expo Router**.
  - **Search Tab:** Displays search results in a clean, scrollable list.
  - **Chat Tab:** A familiar chat UI that can render both text messages and interactive horizontal carousels of movie recommendations.

## 🛠️ Tech Stack

| Area     | Technology                                                                                                  |
| :------- | :---------------------------------------------------------------------------------------------------------- |
| Backend  | **Python**, **FastAPI**, **Sentence-Transformers** (for embeddings), **ChromaDB/FAISS** (for vector search) |
| Frontend | **React Native**, **Expo**, **TypeScript**, **Expo Router**                                                 |
| Data     | **The Movie Database (TMDB) API**                                                                           |
| AI/LLM   | **OpenAI API** (or similar, for the chat functionality)                                                     |

## 🚀 Getting Started

### Prerequisites

- Node.js and npm/yarn
- Python 3.8+ and pip
- A TMDB API Key
- An OpenAI API Key (or another LLM provider)
- Expo Go app on your mobile device for testing.

### Backend Setup

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory and add your API keys:

    ```env
    TMDB_API_KEY="your_tmdb_api_key_here"
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

4.  **Fetch and Process Data:**
    Run the script to download movie data from TMDB. This will create a `movies_with_genres.csv` file in the `data/` directory.

    ```bash
    python src/database/fetch_data_from_tmdb.py
    ```

    _(Note: A second script to generate and store embeddings in a vector database would also be run here, e.g., `python src/database/generate_embeddings.py`)_

5.  **Run the backend server:**
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The server will be available at `http://<YOUR_LOCAL_IP>:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**

    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**

    ```bash
    npm install
    # or
    yarn install
    ```

3.  **Configure the API URL:**
    Open the following files and update the `API_BASE_URL` constant to point to your backend server's local IP address:

    - `frontend/app/(tabs)/index.tsx`
    - `frontend/app/(tabs)/chat.tsx`

    ```typescript
    // Replace <YOUR_MACHINE_LOCAL_IP> with your actual IP
    const API_BASE_URL = "http://<YOUR_MACHINE_LOCAL_IP>:8000/api";
    ```

4.  **Start the development server:**

    ```bash
    npx expo start
    ```

5.  Scan the QR code with the Expo Go app on your iOS or Android device to run the application. Ensure your device is on the same Wi-Fi network as your computer.

## 🖼️ Screenshots

_(Placeholder for app screenshots)_

| Search Screen  | Chat Screen  |
| :------------: | :----------: |
| !Search Screen | !Chat Screen |

## ⚙️ How It Works

### 1. Data Ingestion & Embedding

- The `fetch_data_from_tmdb.py` script queries the TMDB API for a list of popular movies.
- It saves relevant data (title, overview, genres, etc.) into a CSV file.
- A separate process (not shown in context) would then read this CSV, use a model like `Sentence-Transformers` to convert the movie overviews into numerical vector embeddings, and store these embeddings in a vector database like ChromaDB.

### 2. Semantic Search (`/api/search`)

1.  The React Native app sends the user's query text to the FastAPI backend.
2.  The backend converts the incoming query into an embedding using the same sentence-transformer model.
3.  It performs a similarity search (e.g., cosine similarity) in the vector database to find the movie embeddings that are "closest" to the query embedding.
4.  The top N results are returned to the frontend and displayed in a list.

### 3. Conversational Search (`/api/chat_search`)

1.  The user sends a message in the chat UI.
2.  The frontend sends the entire conversation history to the `/api/chat_search` endpoint.
3.  The backend forwards this conversation to an LLM (like GPT-4). The LLM is prompted to act as a helpful movie assistant and is given access to a "tool" which is our semantic search function.
4.  If the user's request requires finding movies, the LLM calls the search tool with an appropriate query.
5.  The backend executes the search, gets the movie results, and passes them back to the LLM.
6.  The LLM formats a natural language response, which might include a sentence like "Here are some movies you might like," and includes the structured movie data.
7.  The backend sends this complete response to the frontend, which then renders the text and the movie recommendation carousel.
