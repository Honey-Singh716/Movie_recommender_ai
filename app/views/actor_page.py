import streamlit as st
from core.recommendations import recommend_by_actor
from utils.utils import display_movie_card, get_actor_image_by_name


# app/modules/actor_page.py
def show_actor_page(data, initial_actor=""):
    st.header("Actor / Actress Filmography")

    # Initialize once
    if "actor_search" not in st.session_state:
        st.session_state.actor_search = initial_actor

    actor_name = st.text_input(
        "Actor/Actress Name:",
        value=st.session_state.actor_search,
        placeholder="e.g., Tom Hanks or Meryl Streep"
    )

    if actor_name.strip():
        st.session_state.actor_search = actor_name.strip()

        
        api_key = st.secrets.get("TMDB_API_KEY")
        actor_img = (
            get_actor_image_by_name(actor_name, api_key)
            if api_key else None
        )


        col1, col2 = st.columns([1, 4])


        with col1:
            if actor_img:
                st.image(actor_img, width=150)
            else:
                st.image(
                    "https://via.placeholder.com/150x225?text=No+Image",
                    width=150
                )


        with col2:
            pass  # Actor bio / extra info can be added here later

        st.divider()

        
        st.write(f"Showing movies where {st.session_state.actor_search} appeared:")

        actor_movies = recommend_by_actor(st.session_state.actor_search, data)

        if actor_movies.empty:
            st.warning(f"No movies found for {st.session_state.actor_search}")
            return

        st.subheader(f"Movies featuring {st.session_state.actor_search}")

        cols = st.columns(5)
        for i, (_, movie) in enumerate(actor_movies.iterrows()):
            with cols[i % 5]:
                display_movie_card(movie)
