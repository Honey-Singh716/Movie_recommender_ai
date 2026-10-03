import streamlit as st
from core.recommendations import recommend_by_actor
from utils.utils import display_movie_card, get_actor_image_by_name, get_actor_info_from_tmdb


def show_actor_page(data, initial_actor=""):
    st.header("⭐ Actor / Actress Filmography")
    st.write("Explore the complete movie filmography of any actor or actress.")

    # Initialize once
    if "actor_search" not in st.session_state:
        st.session_state.actor_search = initial_actor

    actor_name = st.text_input(
        "Actor/Actress Name:",
        value=st.session_state.actor_search,
        placeholder="e.g., Tom Hanks or Meryl Streep",
        key="actor_search_input"
    )

    if actor_name.strip():
        st.session_state.actor_search = actor_name.strip()

        api_key = st.secrets.get("TMDB_API_KEY")
        actor_img = get_actor_image_by_name(actor_name, api_key) if api_key else None
        actor_info = get_actor_info_from_tmdb(actor_name, api_key) if api_key else None

        col1, col2 = st.columns([1, 4])

        with col1:
            img_src = actor_img if actor_img else "https://placehold.co/150x225/1a1a2e/ffffff?text=Actor"
            st.markdown(
                f"""
                <img src="{img_src}" style="
                    width:150px; height:225px; object-fit:cover;
                    border-radius:14px;
                    box-shadow:0 8px 24px rgba(0,0,0,0.5);
                " onerror="this.src='https://placehold.co/150x225/1a1a2e/ffffff?text=Actor'"/>
                """,
                unsafe_allow_html=True
            )

        with col2:
            if actor_info:
                st.markdown(f"## {actor_info.get('name', actor_name)}")
                
                meta_cols = st.columns(3)
                if actor_info.get("birthday"):
                    meta_cols[0].metric("🎂 Birthday", actor_info["birthday"])
                if actor_info.get("place_of_birth"):
                    meta_cols[1].metric("📍 Born In", actor_info["place_of_birth"][:30])
                if actor_info.get("known_for_department"):
                    meta_cols[2].metric("Known For", actor_info["known_for_department"])

                bio = actor_info.get("biography", "")
                if bio:
                    # Show first 500 chars with expander for more
                    short_bio = bio[:450]
                    if len(bio) > 450:
                        short_bio += "…"
                    st.markdown(f"> {short_bio}")
                    if len(bio) > 450:
                        with st.expander("Read full biography"):
                            st.write(bio)
            else:
                st.markdown(f"## {actor_name}")
                st.caption("Add a TMDB API key in secrets to see full actor biography and details.")

        st.divider()

        actor_movies = recommend_by_actor(st.session_state.actor_search, data)

        if actor_movies.empty:
            st.warning(f"No movies found for **{st.session_state.actor_search}** in the local database.")
            st.info("💡 Tip: Try the full name exactly as credited (e.g. 'Robert Downey Jr.' not 'Downey')")
            return

        movie_count = len(actor_movies)
        st.subheader(f"{movie_count} Movies featuring {st.session_state.actor_search}")

        cols = st.columns(5)
        for i, (_, movie) in enumerate(actor_movies.iterrows()):
            with cols[i % 5]:
                display_movie_card(movie)
