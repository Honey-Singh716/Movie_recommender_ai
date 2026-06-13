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

def recommend_movies_by_genres(genres, data, max_movies=50):
    if not genres:
        return pd.DataFrame()

    genres = {g.lower() for g in genres}

    mask = data['genres'].apply(
        lambda movie_genres: (
            isinstance(movie_genres, list) and
            bool(genres & {g.lower() for g in movie_genres})
        )
    )

    return (
        data[mask]
        .sort_values('popularity', ascending=False)
        .head(max_movies)
    )



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

