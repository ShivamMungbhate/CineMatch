import requests
import tomllib

# Read API key from Streamlit secrets
with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

api_key = secrets["TMDB_API_KEY"]

url = "https://api.themoviedb.org/3/movie/550"

try:
    response = requests.get(
        url,
        params={"api_key": api_key},
        timeout=20
    )

    print("Status:", response.status_code)

    if response.status_code == 200:
        print("SUCCESS! TMDB API is working.")
        print("Movie:", response.json()["title"])

    else:
        print("TMDB response:", response.text[:300])

except requests.exceptions.RequestException as e:
    print("Connection error:", e)