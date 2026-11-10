
import random
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests
import streamlit as st

from database import (
    register_user,
    authenticate_user,
    save_history,
    get_history,
    clear_history,
    save_watchlist,
    get_watchlist,
    remove_watchlist_item,
    clear_watchlist,
)



st.set_page_config(
    page_title="CineMatch | Movie Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(
            circle at top left,
            #1b1b2b 0%,
            #101018 45%
        );
        color: #ffffff;
    }

    [data-testid="stSidebar"] {
        background-color: #151520;
        border-right: 1px solid #262636;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    .hero {
        padding: 34px 38px;
        border-radius: 18px;
        background: linear-gradient(
            120deg,
            #e50914 0%,
            #8a1c7c 55%,
            #3a2a8f 100%
        );
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, .35);
    }

    .hero h1 {
        margin: 0;
        font-size: 2.2rem;
        color: #fff;
    }

    .hero p {
        margin: 6px 0 0 0;
        font-size: 1.05rem;
        color: #f1e9f5;
    }

    div[data-testid="stMetric"] {
        background: #20202c;
        border: 1px solid #2c2c3d;
        padding: 16px;
        border-radius: 14px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 9px;
        min-height: 40px;
        transition: transform .12s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
    }

    .badge {
        display: inline-block;
        padding: 2px 10px;
        margin: 2px 4px 2px 0;
        border-radius: 999px;
        background: #2a2a3b;
        color: #cfcfe0;
        font-size: 12px;
    }

    .badge-match {
        background: #14532d;
        color: #bbf7d0;
        font-weight: 600;
    }

    .badge-rate {
        background: #4a3b05;
        color: #fde68a;
        font-weight: 600;
    }

    .movie-title {
        font-weight: 700;
        font-size: 15px;
        line-height: 1.3;
        min-height: 40px;
        margin: 8px 0 4px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_user_session():
    """Clear data belonging to the previous login."""

    keys_to_clear = [
        "history",
        "recommendations",
        "active_movie",
        "random_movie",
        "show_random_recommendations",
        "watchlist",
        "next_page",
        "num_recs",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


if "user" not in st.session_state:
    st.session_state.user = None


if st.session_state.user is None:

    st.title("🎬 Welcome to CineMatch")
    st.subheader("Your personal movie discovery platform")
    st.write("Login or create an account to continue.")

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    with login_tab:

        with st.form("login_form"):

            login_username = st.text_input("Username")

            login_password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login_button:

                user = authenticate_user(
                    login_username,
                    login_password
                )

                if user:

                    reset_user_session()

                    st.session_state.user = user

                    
                    st.session_state.history = get_history(user["id"])
                    st.session_state.watchlist = get_watchlist(user["id"])

                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error("Invalid username or password.")

    with register_tab:

        with st.form("register_form"):

            new_username = st.text_input("Choose a username")

            new_password = st.text_input(
                "Choose a password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

            if register_button:

                if new_password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    success, message = register_user(
                        new_username,
                        new_password
                    )

                    if success:

                        st.success(message)

                        st.info(
                            "Your account is ready! "
                            "Please go to the Login tab."
                        )

                    else:
                        st.error(message)

    st.stop()



current_user_id = int(st.session_state.user["id"])

st.session_state.history = get_history(current_user_id)
st.session_state.watchlist = get_watchlist(current_user_id)


DEFAULTS = {
    "recommendations": [],
    "active_movie": None,
    "random_movie": None,
    "show_random_recommendations": False,
    "navigation": "🏠 Dashboard",
    "num_recs": 5,
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


if "next_page" in st.session_state:
    st.session_state.navigation = st.session_state.pop("next_page")



@st.cache_data
def load_data():

    movies = pd.read_csv("model/movies.csv")
    similarity_matrix = np.load("model/similarity.npy")

    movies = movies.reset_index(drop=True)

    if len(movies) != similarity_matrix.shape[0]:

        raise ValueError(
            "Movie data and similarity matrix do not match."
        )

    return movies, similarity_matrix


new_df, similarity = load_data()


all_movies = (
    new_df["title"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)


if not all_movies:

    st.error("No movies were found in model/movies.csv.")
    st.stop()


if st.session_state.random_movie not in all_movies:
    st.session_state.random_movie = random.choice(all_movies)



def api_key_available():

    try:
        return bool(st.secrets["TMDB_API_KEY"])

    except Exception:
        return False


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_movie_details(movie_id):

    try:

        api_key = st.secrets["TMDB_API_KEY"]

        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{int(movie_id)}",
            params={
                "api_key": api_key,
                "append_to_response": "videos,credits",
            },
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trending():

    try:

        api_key = st.secrets["TMDB_API_KEY"]

        response = requests.get(
            "https://api.themoviedb.org/3/trending/movie/week",
            params={"api_key": api_key},
            timeout=15,
        )

        response.raise_for_status()

        return [
            {
                "id": movie["id"],
                "title": movie["title"],
            }
            for movie in response.json().get("results", [])[:5]
        ]

    except Exception:
        return []


def fetch_many(movie_ids):

    movie_ids = list(movie_ids)

    if not movie_ids:
        return {}

    with ThreadPoolExecutor(
        max_workers=min(8, len(movie_ids))
    ) as pool:

        results = list(
            pool.map(fetch_movie_details, movie_ids)
        )

    return dict(zip(movie_ids, results))


def get_poster(details):

    if details and details.get("poster_path"):

        return (
            "https://image.tmdb.org/t/p/w500"
            + details["poster_path"]
        )

    return None


def get_trailer(details):

    if not details:
        return None

    videos = details.get("videos", {}).get("results", [])

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
        ):

            return (
                f"https://www.youtube.com/watch?v={video['key']}"
            )

    return None


def get_director(details):

    if not details:
        return None

    crew = details.get("credits", {}).get("crew", [])

    for person in crew:

        if person.get("job") == "Director":
            return person.get("name")

    return None


def get_cast(details, limit=5):

    if not details:
        return []

    cast = details.get("credits", {}).get("cast", [])

    return [
        person["name"]
        for person in cast[:limit]
    ]


def get_year(details):

    release = (details or {}).get("release_date") or ""

    return release[:4] if release else "—"


def get_genres(details):

    return [
        genre["name"]
        for genre in (details or {}).get("genres", [])
    ]


def recommend(movie, n=5):

    matching_movies = new_df.index[
        new_df["title"] == movie
    ].tolist()

    if not matching_movies:
        return []

    movie_index = matching_movies[0]

    distances = similarity[movie_index]

    movie_scores = sorted(
        enumerate(distances),
        reverse=True,
        key=lambda item: item[1]
    )

    recommendations = []

    for index, score in movie_scores:

        if index == movie_index:
            continue

        movie_row = new_df.iloc[index]

        recommendations.append({
            "id": int(movie_row["id"]),
            "title": movie_row["title"],
            "score": float(score),
        })

        if len(recommendations) >= n:
            break

    return recommendations


def add_to_history(movie):

    user_id = st.session_state.user["id"]

    save_history(user_id, movie)

    st.session_state.history = get_history(user_id)


def run_recommendation(title):

    st.session_state.recommendations = recommend(
        title,
        st.session_state.get("num_recs", 5)
    )

    st.session_state.active_movie = title

    add_to_history(title)


def toggle_watchlist(movie_id, title):
    """
    Add or remove a movie from the logged-in user's
    permanent database watchlist.
    """

    user_id = int(st.session_state.user["id"])
    movie_id = int(movie_id)

    watchlist = st.session_state.watchlist

    if movie_id in watchlist:

        remove_watchlist_item(
            user_id,
            movie_id
        )

    else:

        save_watchlist(
            user_id,
            movie_id,
            title
        )

    
    st.session_state.watchlist = get_watchlist(user_id)


def stretch_button(label, **kwargs):

    try:

        return st.button(
            label,
            width="stretch",
            **kwargs
        )

    except TypeError:

        return st.button(
            label,
            use_container_width=True,
            **kwargs
        )


def show_image(url):

    try:

        st.image(url, width="stretch")

    except TypeError:

        st.image(
            url,
            use_container_width=True
        )



def show_movie_card(movie, details, prefix):

    movie_id = int(movie["id"])

    with st.container(border=True):

        poster = get_poster(details)

        if poster:
            show_image(poster)

        else:
            st.info("Poster unavailable")

        st.markdown(
            f"<div class='movie-title'>{movie['title']}</div>",
            unsafe_allow_html=True
        )

        if details:

            rating = details.get("vote_average", 0) or 0

            badges = (
                f"<span class='badge badge-rate'>"
                f"⭐ {rating:.1f}</span>"
            )

            if movie.get("score") is not None:

                badges += (
                    f"<span class='badge badge-match'>"
                    f"{movie['score'] * 100:.0f}% match</span>"
                )

            badges += (
                f"<span class='badge'>"
                f"📅 {get_year(details)}</span>"
            )

            st.markdown(
                badges,
                unsafe_allow_html=True
            )

            genres = get_genres(details)

            if genres:

                st.markdown(
                    "".join(
                        f"<span class='badge'>{genre}</span>"
                        for genre in genres[:3]
                    ),
                    unsafe_allow_html=True
                )

            with st.expander("Details"):

                tagline = details.get("tagline")

                if tagline:
                    st.caption(f"_{tagline}_")

                st.write(
                    details.get("overview")
                    or "Description unavailable."
                )

                runtime = details.get("runtime")

                if runtime:

                    st.caption(
                        f"⏱️ {runtime // 60}h {runtime % 60}m"
                    )

                director = get_director(details)

                if director:
                    st.caption(f"🎬 Director: {director}")

                cast = get_cast(details)

                if cast:

                    st.caption(
                        "🎭 Cast: " + ", ".join(cast)
                    )

        else:

            st.caption("Movie details unavailable")

        col_a, col_b = st.columns(2)

        in_list = movie_id in st.session_state.watchlist

        with col_a:

            st.button(
                "💔 Remove" if in_list else "❤️ Save",
                key=f"{prefix}_wl_{movie_id}",
                on_click=toggle_watchlist,
                args=(movie_id, movie["title"]),
            )

        with col_b:

            trailer = get_trailer(details)

            if trailer:
                st.link_button("▶️ Trailer", trailer)



def render_results(recs, prefix, show_filters=True):

    if not recs:

        st.info("No recommendations to display.")
        return

    with st.spinner("Loading movie details..."):

        details_map = fetch_many([
            movie["id"]
            for movie in recs
        ])

    min_rating = 0.0
    chosen_genres = []
    sort_by = "Best match"

    if show_filters:

        all_genres = sorted({
            genre
            for details in details_map.values()
            for genre in get_genres(details)
        })

        with st.expander("🎛️ Filter & sort results"):

            f1, f2, f3 = st.columns(3)

            with f1:

                min_rating = st.slider(
                    "Minimum rating",
                    0.0,
                    10.0,
                    0.0,
                    0.5,
                    key=f"{prefix}_minrating",
                )

            with f2:

                chosen_genres = st.multiselect(
                    "Genres",
                    all_genres,
                    key=f"{prefix}_genres",
                )

            with f3:

                sort_by = st.selectbox(
                    "Sort by",
                    [
                        "Best match",
                        "Rating",
                        "Newest",
                        "Oldest",
                    ],
                    key=f"{prefix}_sort",
                )

    items = []

    for movie in recs:

        details = details_map.get(movie["id"])

        if details:

            rating = details.get("vote_average", 0) or 0

            if rating < min_rating:
                continue

            if (
                chosen_genres
                and not set(chosen_genres) & set(get_genres(details))
            ):
                continue

        items.append((movie, details))

    if sort_by == "Rating":

        items.sort(
            key=lambda item: (
                (item[1] or {}).get("vote_average", 0) or 0
            ),
            reverse=True
        )

    elif sort_by == "Newest":

        items.sort(
            key=lambda item: (
                (item[1] or {}).get("release_date") or ""
            ),
            reverse=True
        )

    elif sort_by == "Oldest":

        items.sort(
            key=lambda item: (
                (item[1] or {}).get("release_date") or "9999"
            )
        )

    if not items:

        st.warning(
            "No movies match your filters. Try relaxing them."
        )
        return

    for start in range(0, len(items), 5):

        row = items[start:start + 5]

        cols = st.columns(5)

        for col, (movie, details) in zip(cols, row):

            with col:

                show_movie_card(
                    movie,
                    details,
                    prefix
                )



PAGES = [
    "🏠 Dashboard",
    "🔍 Discover Movies",
    "❤️ Watchlist",
    "🕒 History",
    "🎲 Random Movie",
]

st.sidebar.title("🎬 CineMatch")

st.sidebar.write(
    f"👤 Welcome, {st.session_state.user['username']}!"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    reset_user_session()

    st.session_state.user = None

    st.rerun()


st.sidebar.caption(
    "Your personal movie discovery platform"
)

page = st.sidebar.radio(
    "NAVIGATION",
    PAGES,
    key="navigation"
)

st.sidebar.divider()

st.sidebar.subheader("⚙️ Settings")

st.sidebar.slider(
    "Recommendations per search",
    min_value=5,
    max_value=15,
    value=5,
    step=5,
    key="num_recs",
    help="How many similar movies to show.",
)

if not api_key_available():

    st.sidebar.warning(
        "TMDB_API_KEY missing in secrets. "
        "Posters and details are disabled."
    )

st.sidebar.divider()

st.sidebar.caption("Powered by TMDB")



if page == "🏠 Dashboard":

    st.markdown(
        """
        <div class="hero">
            <h1>🎬 Welcome to CineMatch</h1>
            <p>
                Discover movies. Explore stories.
                Find your next favourite.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user_history = get_history(current_user_id)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🎞️ Total Movies",
        f"{len(new_df):,}"
    )

    c2.metric(
        "✨ Recommendations",
        len(st.session_state.recommendations)
    )

    c3.metric(
        "🕒 Recent Searches",
        len(user_history)
    )

    c4.metric(
        "❤️ Watchlist",
        len(st.session_state.watchlist)
    )

    st.divider()

    st.subheader("🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("**🔍 Discover Movies**")

        st.caption(
            "Find movies similar to your favourite films."
        )

        if stretch_button(
            "Explore Movies",
            key="qa_explore"
        ):

            st.session_state.next_page = "🔍 Discover Movies"
            st.rerun()

    with col2:

        st.markdown("**🎲 Random Movie**")

        st.caption(
            "Let CineMatch choose a movie for you."
        )

        if stretch_button(
            "Surprise Me",
            key="qa_random"
        ):

            st.session_state.random_movie = random.choice(
                all_movies
            )

            st.session_state.show_random_recommendations = False

            st.session_state.next_page = "🎲 Random Movie"

            st.rerun()

    with col3:

        st.markdown("**❤️ My Watchlist**")

        st.caption(
            "Movies you saved to watch later."
        )

        if stretch_button(
            "Open Watchlist",
            key="qa_watchlist"
        ):

            st.session_state.next_page = "❤️ Watchlist"
            st.rerun()

    st.divider()

    trending = fetch_trending()

    if trending:

        st.subheader("🔥 Trending This Week")

        render_results(
            trending,
            "trend",
            show_filters=False
        )

        st.divider()

    st.subheader("🕒 Recently Explored")

    if user_history:

        for item in user_history[:5]:

            st.write(
                f"🎬 **{item['title']}** — {item['time']}"
            )

    else:

        st.info(
            "Your recently explored movies will appear here."
        )

    if st.session_state.watchlist:

        st.divider()

        st.subheader("📊 Your Taste Profile")

        saved = fetch_many(
            list(st.session_state.watchlist.keys())
        )

        genre_counts = pd.Series(
            [
                genre
                for details in saved.values()
                for genre in get_genres(details)
            ]
        ).value_counts()

        if not genre_counts.empty:
            st.bar_chart(genre_counts)

    if st.session_state.recommendations:

        st.divider()

        st.subheader(
            f"🍿 Latest Recommendations for "
            f"{st.session_state.active_movie}"
        )

        render_results(
            st.session_state.recommendations,
            "dash",
            show_filters=False
        )


elif page == "🔍 Discover Movies":

    st.title("🔍 Discover Movies")

    st.write(
        "Search for a movie and discover similar films."
    )

    st.divider()

    selected_movie = st.selectbox(
        "Search or select a movie",
        all_movies,
        index=None,
        placeholder="Start typing a movie title..."
    )

    col1, col2 = st.columns(2)

    with col1:

        get_recommendations = stretch_button(
            "✨ Get Recommendations",
            key="get_recs",
            disabled=selected_movie is None
        )

    with col2:

        surprise = stretch_button(
            "🎲 Surprise Me",
            key="discover_surprise"
        )

    if get_recommendations and selected_movie:

        run_recommendation(selected_movie)

    if surprise:

        run_recommendation(
            random.choice(all_movies)
        )

    if st.session_state.recommendations:

        st.divider()

        st.subheader(
            f"🍿 Movies similar to "
            f"{st.session_state.active_movie}"
        )

        render_results(
            st.session_state.recommendations,
            "disc"
        )
elif page == "❤️ Watchlist":

    st.title("❤️ My Watchlist")

    st.write(
        "Movies you saved to watch later."
    )

    st.divider()

    watchlist = get_watchlist(current_user_id)

    st.session_state.watchlist = watchlist

    if watchlist:

        items = [
            {
                "id": movie_id,
                "title": info["title"]
            }
            for movie_id, info in watchlist.items()
        ]

        render_results(
            items,
            "wl",
            show_filters=True
        )

        st.divider()

        export_df = pd.DataFrame([
            {
                "Title": info["title"],
                "Saved on": info["added"]
            }
            for info in watchlist.values()
        ])

        col1, col2 = st.columns(2)

        with col1:

            st.download_button(
                "⬇️ Download Watchlist (CSV)",
                export_df.to_csv(index=False).encode("utf-8"),
                file_name="cinematch_watchlist.csv",
                mime="text/csv"
            )

        with col2:

            if st.button("🗑️ Clear Watchlist"):

                clear_watchlist(current_user_id)

                st.session_state.watchlist = {}

                st.success("Your watchlist has been cleared.")

                st.rerun()

    else:

        st.info(
            "Your watchlist is empty. "
            "Tap ❤️ Save on any movie to add it."
        )

elif page == "🕒 History":

    st.title("🕒 Recommendation History")

    st.write(
        "Keep track of the movies you have explored."
    )

    st.divider()

    user_history = get_history(current_user_id)

    st.session_state.history = user_history

    if user_history:

        for index, item in enumerate(user_history):

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.markdown(
                        f"**🎬 {item['title']}**"
                    )

                    st.caption(item["time"])

                with col2:

                    if st.button(
                        "Explore",
                        key=f"history_{index}"
                    ):

                        st.session_state.recommendations = recommend(
                            item["title"],
                            st.session_state.get("num_recs", 5)
                        )

                        st.session_state.active_movie = item["title"]

                        st.session_state.next_page = (
                            "🔍 Discover Movies"
                        )

                        st.rerun()

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            history_df = pd.DataFrame(user_history)

            st.download_button(
                "⬇️ Download History (CSV)",
                history_df.to_csv(index=False).encode("utf-8"),
                file_name="cinematch_history.csv",
                mime="text/csv"
            )

        with col2:

            if st.button("🗑️ Clear History"):

                clear_history(current_user_id)

                st.session_state.history = []

                st.success("Your history has been cleared.")

                st.rerun()

    else:

        st.info(
            "No history yet. Explore some movies first!"
        )


elif page == "🎲 Random Movie":

    st.title("🎲 Random Movie Generator")

    st.write(
        "Can't decide what to watch? "
        "Let CineMatch pick one for you."
    )

    st.divider()

    random_choice = st.session_state.random_movie

    random_row = new_df[
        new_df["title"] == random_choice
    ].iloc[0]

    random_id = int(random_row["id"])

    random_details = fetch_movie_details(random_id)

    col1, col2 = st.columns([1, 2])

    with col1:

        poster = get_poster(random_details)

        if poster:
            show_image(poster)

        else:
            st.info("Poster unavailable")

    with col2:

        st.subheader(random_choice)

        if random_details:

            tagline = random_details.get("tagline")

            if tagline:
                st.caption(f"_{tagline}_")

            runtime = random_details.get("runtime")

            badges = (
                f"<span class='badge badge-rate'>"
                f"⭐ {(random_details.get('vote_average') or 0):.1f}/10"
                f"</span>"
                f"<span class='badge'>"
                f"📅 {get_year(random_details)}</span>"
            )

            if runtime:

                badges += (
                    f"<span class='badge'>"
                    f"⏱️ {runtime // 60}h {runtime % 60}m"
                    f"</span>"
                )

            badges += "".join(
                f"<span class='badge'>{genre}</span>"
                for genre in get_genres(random_details)
            )

            st.markdown(
                badges,
                unsafe_allow_html=True
            )

            st.write(
                random_details.get("overview")
                or "Description unavailable."
            )

            director = get_director(random_details)

            if director:
                st.caption(f"🎬 Director: {director}")

            cast = get_cast(random_details)

            if cast:

                st.caption(
                    "🎭 Cast: " + ", ".join(cast)
                )

            trailer = get_trailer(random_details)

            if trailer:

                st.link_button(
                    "▶️ Watch Trailer",
                    trailer
                )

        else:

            st.info(
                "Additional movie details are unavailable."
            )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        if stretch_button(
            "🎲 Pick Another Movie",
            key="rnd_pick"
        ):

            st.session_state.random_movie = random.choice(
                all_movies
            )

            st.session_state.show_random_recommendations = False

            st.rerun()

    with col2:

        if stretch_button(
            "✨ Find Similar Movies",
            key="rnd_similar"
        ):

            run_recommendation(random_choice)

            st.session_state.show_random_recommendations = True

            st.rerun()

    with col3:

        in_list = random_id in st.session_state.watchlist

        stretch_button(
            "💔 Remove from Watchlist"
            if in_list
            else "❤️ Add to Watchlist",
            key="rnd_wl",
            on_click=toggle_watchlist,
            args=(random_id, random_choice)
        )

    if st.session_state.show_random_recommendations:

        st.divider()

        st.subheader(
            f"🍿 Movies Similar to {random_choice}"
        )

        render_results(
            st.session_state.recommendations,
            "rnd"
        )


st.divider()

st.caption(
    "CineMatch | Movie recommendations powered by TMDB."
)
