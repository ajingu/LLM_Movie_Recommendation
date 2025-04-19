# https://developer.themoviedb.org/reference/discover-movie

import requests, csv, os, time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

fields = ["id","title","release_date","overview","genre_ids","poster_path"]
movies = {}  # Using dictionary to store unique movies by ID

for page in range(1, 60):            # ~1000 movies is enough for an MVP
    r = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        params={"api_key":API_KEY, "sort_by":"popularity.desc", "page":page}
    ).json()
    
    for m in r["results"]:
        movie_id = m.get("id")
        if movie_id not in movies:  # Only add if we haven't seen this movie before
            movies[movie_id] = {f: m.get(f) for f in fields}
    time.sleep(0.30)                # stay under 40 req/10 s hard limit

# Convert dictionary values to list for writing to CSV
unique_movies = list(movies.values())

with open("../data/movies.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(unique_movies)
