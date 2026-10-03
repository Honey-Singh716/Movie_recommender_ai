import streamlit as st
from core.recommendations import recommend
from utils.utils import display_movie_card, get_movie_details, get_poster_from_tmdb_id, get_actor_image_by_name
import pandas as pd


def show_movie_info_page(data, cast_df):
    """Display the movie information explorer page"""
    st.header("Movie Information Explorer")
    st.write("Search a movie to get complete details, insights, and predictions")
    
    # Movie search with autocomplete
    from utils.utils import movie_search_selector
    selected_movie_row = movie_search_selector("Search for a movie:", key_prefix="info_page")
    selected_movie = selected_movie_row["title"] if selected_movie_row is not None else None
    
    if selected_movie:
        with st.spinner(f"Fetching details for {selected_movie}..."):
            # Get movie details
            details = get_movie_details(selected_movie, data)
            # Use a separate variable name to avoid shadowing
            info_movie_row = data[data["title"] == selected_movie].iloc[0]
            
            if details:
                # Display movie details
                st.markdown(f"## {details['title']}")
                
                # Main content columns
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Movie poster
                    api_key = st.secrets.get("TMDB_API_KEY")
                    poster_url = get_poster_from_tmdb_id(info_movie_row["id"], api_key) if api_key else None

                    if poster_url:
                        st.image(poster_url, width=220)
                    else:
                        st.markdown("""
                        <div style="
                            width:220px; height:330px;
                            background:linear-gradient(135deg,#1a1a2e,#2d2d44);
                            border-radius:12px;
                            display:flex; flex-direction:column;
                            align-items:center; justify-content:center;
                            color:#aaa; font-size:14px;
                        ">
                            <span style="font-size:50px;"></span>
                            <small>No poster</small>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Quick stats
                    rating = details['vote_average']
                    st.metric("⭐ Rating", f"{rating}/10" if isinstance(rating, (int, float)) else "N/A")
                    st.metric("Release", details['release_date'])
                    st.metric("⏱ Runtime", f"{details['runtime']} min")
                
                with col2:
                    # Movie details
                    st.markdown(f"**Genres:** {details['genres']}")
                    st.markdown(f"**Director:** {details['director']}")
                    
                    # Overview
                    st.markdown("**📖 Overview:**")
                    st.markdown(f"> {details['overview']}")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Budget / Revenue / Profit in a row
                    budget = details.get("budget")
                    revenue = details.get("revenue")

                    bc, rc, pc = st.columns(3)
                    if isinstance(budget, (int, float)) and budget > 0:
                        bc.metric("💰 Budget", f"${budget:,.0f}")
                    else:
                        bc.metric("💰 Budget", "N/A")

                    if isinstance(revenue, (int, float)) and revenue > 0:
                        rc.metric("Revenue", f"${revenue:,.0f}")
                    else:
                        rc.metric("Revenue", "N/A")

                    if isinstance(budget, (int, float)) and isinstance(revenue, (int, float)) and budget > 0 and revenue > 0:
                        profit = revenue - budget
                        profit_str = f"${profit:,.0f}" if profit > 0 else f"-${abs(profit):,.0f}"
                        pc.metric("💹 Profit", profit_str, delta=None)
                    else:
                        pc.metric("💹 Profit", "N/A")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # "Find Similar" button that navigates to recommender
                    if st.button("🤖 Find Similar Movies", use_container_width=True, key="find_similar_btn"):
                        st.session_state.current_page = "Movie Recommender"
                        # Pre-fill the recommender search so user sees this movie
                        st.session_state["recommender_query"] = selected_movie
                        st.rerun()

                st.markdown("---")
                
                # Cast Section
                show_cast_section(info_movie_row, cast_df)

                st.markdown("---")

                # Similar movies
                st.subheader("🔗 Similar Movies")
                st.caption("Based on your selection, here are some similar movies:")

                similar_movies = recommend(selected_movie, data, st.session_state.get('similarity'))
                
                if similar_movies:
                    cols = st.columns(5)
                    for i, title in enumerate(similar_movies[:20]):
                        row = data[data["title"] == title]
                        if row.empty:
                            continue
                        with cols[i % 5]:
                            display_movie_card(row.iloc[0])
                else:
                    st.warning("No similar movies found.")
            else:
                st.error("Could not fetch movie details. Please try another movie.")
    
    return None


def get_movie_cast(movie_id, cast_df, top_n=10):
    cast = cast_df[cast_df["movie_id"] == movie_id] \
        .sort_values("order") \
        .head(top_n)
    return cast


def show_cast_section(movie_row, cast_df):
    st.markdown("### Top Cast")

    cast = get_movie_cast(movie_row["id"], cast_df)

    if cast.empty:
        st.info("No cast information available for this movie.")
        return

    cols = st.columns(5)
    col_idx = 0

    tmdb_api_key = st.secrets.get("TMDB_API_KEY")

    for _, actor in cast.iterrows():
        img = get_actor_image_by_name(actor["name"], tmdb_api_key) if tmdb_api_key else None
        actor_name = actor.get('name', 'Unknown')
        character = actor.get('character', '')

        with cols[col_idx % 5]:
            img_src = img if img else "https://placehold.co/120x180/1a1a2e/ffffff?text=Actor"
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom:12px;">
                    <img src="{img_src}" 
                         style="width:110px; height:165px; object-fit:cover; border-radius:12px; 
                                box-shadow: 0 4px 12px rgba(0,0,0,0.4);"
                         onerror="this.src='https://placehold.co/120x180/1a1a2e/ffffff?text=Actor'"/>
                    <div style="margin-top:6px; font-weight:700; font-size:13px;
                                max-width:110px; overflow:hidden; text-overflow:ellipsis;
                                white-space:nowrap; margin:6px auto 0;">
                        {actor_name}
                    </div>
                    <div style="font-size:11px; color:#9aa0a6; max-width:110px;
                                overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin:auto;">
                        as {character}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Click to explore actor
            if st.button("Films", key=f"actor_btn_{actor_name[:15]}_{col_idx}", use_container_width=True):
                st.session_state.actor_search = actor_name
                st.session_state.current_page = "Actor Filmography"
                st.rerun()

        col_idx += 1
