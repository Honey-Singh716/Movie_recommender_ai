import streamlit as st
from utils.utils import display_movie_card
import pandas as pd


def show_home_page(data):

    # HERO SECTION
    st.markdown(
        """
        <div style="
            background: linear-gradient(to right, rgba(0,0,0,0.88), rgba(0,0,0,0.25)),
                        url('https://image.tmdb.org/t/p/original/9n2tJBplPbgR2ca05hS5CKXwP2c.jpg');
            background-size: cover;
            background-position: center;
            padding: 90px 50px;
            border-radius: 18px;
            margin-bottom: 32px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        ">
            <h1 style="font-size:52px; margin-bottom:8px; font-weight:800;">
                Unlimited Movies, Shows &amp; More
            </h1>
            <p style="font-size:20px; color:#d0d0d0; max-width:520px;">
                Powered by Movie AI Recommender — discover your next favourite film.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================
    # GENRE FILTER
    # ======================
    all_genres = set()
    for g_list in data["genres"].dropna():
        if isinstance(g_list, list):
            all_genres.update(g_list)
    all_genres = sorted(all_genres)

    selected_genre = st.selectbox(
        "Filter by genre (optional)",
        options=["All Genres"] + all_genres,
        key="home_genre_filter"
    )

    def apply_genre_filter(df):
        if selected_genre == "All Genres":
            return df
        return df[df["genres"].apply(
            lambda g: selected_genre in g if isinstance(g, list) else False
        )]

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================
    # POPULAR THIS WEEK
    # ======================
    st.markdown("## Popular This Week")

    if "popularity" in data.columns:
        popular_base = data.sort_values("popularity", ascending=False)
        popular = apply_genre_filter(popular_base).head(10)
    else:
        st.warning("Popularity data not available.")
        popular = data.head(10)

    if popular.empty:
        st.info(f"No popular movies found for genre: **{selected_genre}**")
    else:
        cols = st.columns(5)
        for i, (_, movie) in enumerate(popular.iterrows()):
            with cols[i % 5]:
                display_movie_card(movie, key_suffix="popular")

    st.markdown("---")

    # ======================
    # TOP RATED
    # ======================
    st.markdown("## ⭐ Top Rated Movies")

    if "vote_average" in data.columns:
        top_rated_base = data[data.get("vote_count", pd.Series([0]*len(data))) >= 100]\
            .sort_values("vote_average", ascending=False)
        top_rated = apply_genre_filter(top_rated_base).head(10)
    else:
        st.warning("Rating data not available.")
        top_rated = data.head(10)

    if top_rated.empty:
        st.info(f"No top-rated movies found for genre: **{selected_genre}**")
    else:
        cols = st.columns(5)
        for i, (_, movie) in enumerate(top_rated.iterrows()):
            with cols[i % 5]:
                display_movie_card(movie, key_suffix="top_rated")

    st.markdown("---")

    # ======================
    # TRENDING NOW
    # ======================
    st.markdown("## Trending Now")

    if "vote_count" in data.columns:
        trending_base = data.sort_values("vote_count", ascending=False)
    elif "popularity" in data.columns:
        trending_base = data.sort_values("popularity", ascending=False)
    else:
        st.warning("Trending data not available.")
        trending_base = data

    trending = apply_genre_filter(trending_base).head(10)

    if trending.empty:
        st.info(f"No trending movies found for genre: **{selected_genre}**")
    else:
        cols = st.columns(5)
        for i, (_, movie) in enumerate(trending.iterrows()):
            with cols[i % 5]:
                display_movie_card(movie, key_suffix="trending")
