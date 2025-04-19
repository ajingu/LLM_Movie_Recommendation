# https://developer.themoviedb.org/reference/discover-movie
# https://developer.themoviedb.org/reference/genre-movie-list

import requests, csv, os, time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# First, fetch the genre list
genre_response = requests.get(
    "https://api.themoviedb.org/3/genre/movie/list",
    params={"api_key": API_KEY}
).json()

# Create a mapping of genre IDs to names
genre_map = {genre["id"]: genre["name"] for genre in genre_response["genres"]}

fields = ["id", "title", "release_date", "overview", "genres", "poster_path"]
movies = {}  # Using dictionary to store unique movies by ID

for page in range(1, 60):            # ~1000 movies is enough for an MVP
    r = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        params={"api_key":API_KEY, "sort_by":"popularity.desc", "page":page}
    ).json()
    
    for m in r["results"]:
        movie_id = m.get("id")
        if movie_id not in movies:  # Only add if we haven't seen this movie before
            # Convert genre IDs to genre names
            genre_ids = m.get("genre_ids", [])
            genre_names = [genre_map.get(genre_id, "Unknown") for genre_id in genre_ids]
            
            movie_data = {
                "id": m.get("id"),
                "title": m.get("title"),
                "release_date": m.get("release_date"),
                "overview": m.get("overview"),
                "genres": ", ".join(genre_names),  # Join genre names with commas
                "poster_path": m.get("poster_path")
            }
            movies[movie_id] = movie_data
    time.sleep(0.30)                # stay under 40 req/10 s hard limit

# Convert dictionary values to list for writing to CSV
unique_movies = list(movies.values())

with open("../../data/movies_with_genres.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(unique_movies)
