import pandas as pd
import streamlit as st

def recommend(movie_title, data, similarity, top_n= 20):
    """Get movie recommendations based on similarity"""
    try:
        idx = data[data['title'] == movie_title].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        return [data.iloc[i[0]]['title'] for i in sim_scores]
    except Exception as e:
        st.error(f"Error finding recommendations: {str(e)}")
        return []

def recommend_movies_by_genres(
    genres: list[str],
    data,
    max_movies: int = 50,
    min_vote_avg: float = 5.5,
    min_vote_count: int = 50,
) -> "pd.DataFrame":
    """
    Return movies ranked by how well they match the requested genres.

    Scoring per movie:
      genre_match_score = number of requested genres the movie covers
                          (normalised 0–1 by len(genres))
      popularity_score  = log-scaled normalised popularity

      final_score = 0.65 × genre_match + 0.35 × popularity

    Only movies with vote_average >= min_vote_avg and
    vote_count >= min_vote_count are returned (quality gate).
    """
    if not genres:
        return pd.DataFrame()

    import numpy as np

    target_genres = {g.lower() for g in genres}

    # Quality gate
    df = data.copy()
    if "vote_average" in df.columns:
        df = df[df["vote_average"] >= min_vote_avg]
    if "vote_count" in df.columns:
        df = df[df["vote_count"] >= min_vote_count]

    # Genre match score (0 → 1)
    def genre_match(movie_genres):
        if not isinstance(movie_genres, list):
            return 0.0
        hits = sum(1 for g in movie_genres if g.lower() in target_genres)
        return hits / len(target_genres)

    df = df.copy()
    df["_genre_score"] = df["genres"].apply(genre_match)

    # Keep only movies with at least one matching genre
    df = df[df["_genre_score"] > 0]
    if df.empty:
        return pd.DataFrame()

    # Normalise popularity (log scale)
    if "popularity" in df.columns:
        log_pop = np.log1p(df["popularity"])
        pop_min, pop_max = log_pop.min(), log_pop.max()
        span = pop_max - pop_min if pop_max != pop_min else 1.0
        df["_pop_score"] = (log_pop - pop_min) / span
    else:
        df["_pop_score"] = 0.0

    # Final combined score
    df["_final_score"] = 0.65 * df["_genre_score"] + 0.35 * df["_pop_score"]

    result = (
        df.sort_values("_final_score", ascending=False)
          .drop(columns=["_genre_score", "_pop_score", "_final_score"])
          .head(max_movies)
    )
    return result




def recommend_by_actor(actor_name, data, top_n=30):
    """
    Return movies featuring the given actor/actress using EXACT cast matching.
    Returns the full movie data needed for display.
    """
    # Normalize actor name
    actor_name = actor_name.strip().lower()

    def exact_actor_match(cast):
        if isinstance(cast, list):
            return actor_name in [actor.strip().lower() for actor in cast]
        return False

    # Apply strict filtering and return all columns
    actor_movies = data[data["cast"].apply(exact_actor_match)]

    if actor_movies.empty:
        return pd.DataFrame()

    # Sort by popularity and return all columns
    return actor_movies.sort_values("popularity", ascending=False).head(top_n)

