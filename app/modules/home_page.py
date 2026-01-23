import streamlit as st
from .utils import display_movie_card


def show_home_page(data):

    # HERO SECTION
    st.markdown(
        """
        <div style="
            background: linear-gradient(to right, rgba(0,0,0,0.85), rgba(0,0,0,0.2)),
                        url('https://image.tmdb.org/t/p/original/9n2tJBplPbgR2ca05hS5CKXwP2c.jpg');
            background-size: cover;
            padding: 80px 40px;
            border-radius: 14px;
            margin-bottom: 30px;
        ">
            <h1 style="font-size:46px">Unlimited movies, shows & more</h1>
            <p style="font-size:18px">Powered by Movie AI Recommender</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================
    # POPULAR THIS WEEK
    # ======================
    st.markdown("## Popular This Week")

    if "popularity" in data.columns:
        popular = data.sort_values("popularity", ascending=False).head(10)
    else:
        st.warning("Popularity data not available.")
        popular = data.head(10)

    cols = st.columns(5)
    for i, (_, movie) in enumerate(popular.iterrows()):
        with cols[i % 5]:
            display_movie_card(movie)

    st.markdown("---")

    # ======================
    # TOP RATED
    # ======================
    st.markdown("## Top Rated Movies")

    if "vote_average" in data.columns:
        top_rated = data.sort_values("vote_average", ascending=False).head(10)
    else:
        st.warning("Rating data not available.")
        top_rated = data.head(10)

    cols = st.columns(5)
    for i, (_, movie) in enumerate(top_rated.iterrows()):
        with cols[i % 5]:
            display_movie_card(movie)

    st.markdown("---")

    # ======================
    # TRENDING NOW
    # ======================
    st.markdown("## Trending Now")

    if "vote_count" in data.columns:
        trending = data.sort_values("vote_count", ascending=False).head(10)
    elif "popularity" in data.columns:
        trending = data.sort_values("popularity", ascending=False).head(10)
    else:
        st.warning("Trending data not available.")
        trending = data.head(10)

    cols = st.columns(5)
    for i, (_, movie) in enumerate(trending.iterrows()):
        with cols[i % 5]:
            display_movie_card(movie)
