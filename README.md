# 🎬 CineMatch – Movie Recommendation System

<blockquote>
🚀 **Live Application:** [Explore CineMatch](https://cinematch-3neayqnzuc6xyswwccscvq.streamlit.app/)
</blockquote>

**Discover movies you'll love with CineMatch!**

CineMatch is a movie recommendation web application built using Python and Streamlit. It helps users discover movies based on their interests by providing personalized recommendations through a content-based filtering approach.

The application combines a movie recommendation model, The Movie Database (TMDB) API, and a PostgreSQL database hosted on Supabase to provide an interactive movie discovery experience.

## 🌟 Project Overview

Finding a movie to watch can sometimes be difficult when there are thousands of options available. CineMatch aims to make this process easier by recommending movies similar to the ones users already enjoy.

Users can explore movies, view movie information and posters, create personal accounts, maintain their watchlists, and keep track of their movie exploration history.

## ✨ Key Features

- **Movie Recommendations:** Get movie recommendations based on the movie you select.
- **Content-Based Filtering:** Uses similarity scores to identify movies with similar characteristics.
- **Movie Information:** Fetches movie details and posters using the TMDB API.
- **User Authentication:** Supports user registration and login.
- **Secure Password Storage:** Passwords are protected using salted PBKDF2-HMAC-SHA256 hashing.
- **Personal Watchlist:** Save movies to a personal watchlist for future viewing.
- **Movie History:** Keeps track of movies explored by each user.
- **Persistent Database:** Stores user information, watchlists, and history in Supabase PostgreSQL.
- **Interactive Interface:** Built with Streamlit for a simple and user-friendly experience.

## ⚙️ How CineMatch Works

### 1. Movie Dataset and Processing

The application uses a movie dataset containing information about movies.

The dataset is processed using Python and Pandas to prepare the information required by the recommendation model.

### 2. Content-Based Recommendation System

CineMatch uses a content-based filtering approach.

The recommendation workflow is:

1. The user selects a movie.
2. The application identifies the selected movie in the processed dataset.
3. A precomputed similarity matrix is used to find movies with similar characteristics.
4. Movies with the highest similarity scores are selected.
5. The recommended movies are displayed to the user.

This approach recommends movies based on similarities between movie characteristics rather than relying on ratings from other users.

### 3. TMDB API Integration

CineMatch integrates with **The Movie Database (TMDB) API** to retrieve movie information.

The application uses TMDB to fetch:
- Movie posters
- Movie details
- Additional movie information

### 4. User Authentication

CineMatch provides a registration and login system.

The authentication workflow includes:

1. Users create an account with a username and password.
2. Passwords are securely hashed using PBKDF2-HMAC-SHA256 with a randomly generated salt.
3. User credentials are stored in the PostgreSQL database.
4. During login, the submitted password is verified against the stored password hash.
5. Authenticated users can access their personal movie features.

Passwords are not stored as plain text.

### 5. Database Integration – Supabase PostgreSQL

CineMatch uses **Supabase PostgreSQL** as its database backend.

The database provides persistent storage for user accounts and personalized movie activity.

The main database entities are:

**Users**
- Stores registered usernames.
- Stores password hashes and salts.
- Records account creation timestamps.

**Movie History**
- Records movies explored by users.
- Associates each history entry with its respective user.
- Stores timestamps for movie exploration.

**Movie Watchlist**
- Stores movies saved by users.
- Associates saved movies with individual user accounts.
- Prevents duplicate entries for the same movie and user.

Database relationships use foreign keys to connect user accounts with their movie history and watchlists. Cascading deletion maintains referential integrity when a user is removed.

Supabase provides hosted PostgreSQL database infrastructure, allowing CineMatch to retain user data beyond individual application sessions.

### 6. Personal Movie Experience

After logging in, users can:

- Discover recommended movies.
- Explore movie information.
- Save movies to their personal watchlist.
- View their previously explored movies.
- Manage their saved movie collection.

Each user's watchlist and movie history are associated with their own account.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| Pandas | Dataset processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine learning and similarity calculations |
| NLTK | Text processing |
| Requests | TMDB API communication |
| TMDB API | Movie information and posters |
| PostgreSQL | Database management |
| Supabase | Hosted PostgreSQL database |
| Psycopg | Python-PostgreSQL connectivity |
| Git & GitHub | Version control and project hosting |

## 🔄 Overall Project Workflow

1. Movie data is loaded and processed.
2. Movie similarity information is prepared for recommendations.
3. A user accesses the CineMatch application.
4. The user registers or logs in.
5. The application verifies the user's credentials using the database.
6. The user selects a movie to discover similar movies.
7. The recommendation model generates movie suggestions.
8. TMDB provides movie posters and additional information.
9. Users can add movies to their watchlists.
10. Movie exploration activity is stored in the database.
11. Users can revisit their personal watchlists and movie history.

## 🚀 Running the Project Locally

### Prerequisites

- Python installed
- pip package manager
- A TMDB API key
- A Supabase project with PostgreSQL configured

### Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Configure your application secrets locally with:

- `TMDB_API_KEY`
- `DATABASE_URL`

Keep these credentials private. Never commit API keys, database passwords, or other secrets to GitHub.

### Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

## ☁️ Database and Deployment

CineMatch uses Supabase PostgreSQL for persistent storage.

For deployment on Streamlit Community Cloud:

1. Push the project to GitHub.
2. Connect the GitHub repository to Streamlit Community Cloud.
3. Configure the TMDB API key and PostgreSQL connection string through the application's deployment secrets.
4. Deploy the application.

The database connection credentials should be maintained securely through deployment secrets rather than committed to the repository.

## 🔮 Future Improvements

Potential improvements for CineMatch include:

- Genre-based movie filtering.
- More advanced recommendation algorithms.
- Movie ratings and reviews.
- Improved user profiles.
- Additional movie discovery filters.
- Enhanced UI and user experience.
- Deployment and performance optimization.

## 🎯 Project Goal

The goal of CineMatch is to combine machine learning concepts, API integration, database management, and web development into a practical movie discovery application.

It demonstrates how Python-based recommendation systems can be integrated with a modern web interface and a persistent relational database to create a personalized user experience.

---

**CineMatch – Find your next favourite movie! 🍿**
