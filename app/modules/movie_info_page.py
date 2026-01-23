import streamlit as st
from .recommendations import recommend
from .utils import display_movie_card, get_movie_details
import pandas as pd
from .utils import get_poster_from_tmdb_id,get_actor_image_by_name



def show_movie_info_page(data,cast_df):
    """Display the movie information explorer page"""
    st.header(" Movie Information Explorer")
    st.write("Search a movie to get complete details, insights, and predictions")
    
    # Movie search with autocomplete
    movie_titles = data['title'].tolist()
    selected_movie = st.selectbox(
        "Search for a movie:",
        movie_titles,
        index=None,
        placeholder="Type to search...",
        help="Start typing to search for a movie"
    )
    
    if selected_movie:
        with st.spinner(f"Fetching details for {selected_movie}..."):
            # Get movie details
            details = get_movie_details(selected_movie, data)
            movie_row = data[data["title"] == selected_movie].iloc[0]
            
            if details:
                # Display movie details
                st.markdown(f"## {details['title']}")
                
                # Main content columns
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Movie poster
                    
                    api_key = st.secrets.get("TMDB_API_KEY")
                    poster_url = get_poster_from_tmdb_id(movie_row["id"], api_key) if api_key else None
   

                    if poster_url:
                        st.image(poster_url, width=200)
                    else:
                        st.image(
                        "https://via.placeholder.com/300x450?text=No+Poster",
                        width=300
                        )

                    
                    # Quick stats
                    st.metric("Rating", f"{details['vote_average']}")
                    st.metric("Release Date", details['release_date'])
                    st.metric("Runtime", f"{details['runtime']} minutes")
                
                with col2:
                    # Movie details
                    st.write(f"**Genres:** {details['genres']}")
                    st.write(f"**Director:** {details['director']}")
                    
                    #Movie Bidget
                    if 'budget' in details and details['budget']:
                        st.metric("Budget", f"${details['budget']:,.2f}")

                    # Revenue prediction
                    if 'revenue' in details and details['revenue']:
                        st.metric("Revenue", f"${details['revenue']:,.2f}")
                    
                    #Profit Calculation

                    budget = details.get("budget")
                    revenue = details.get("revenue")

                    if isinstance(budget, (int, float)) and isinstance(revenue, (int, float)):
                        if revenue > budget:
                            st.metric("Profit", f"${revenue - budget:,.2f}")
                        else:
                            st.metric("Profit", "No Profit")


                # Movie overview
                st.subheader("Overview")
                st.write(details['overview'])
                
                #Cast Section
                show_cast_section(movie_row, cast_df)


                # Similar movies
                st.subheader(" Similar Movies")
                st.caption("Based on your selection, here are some similar movies:")

                similar_movies = recommend(selected_movie,data,st.session_state.get('similarity')   )                
                
                if similar_movies:
                    cols = st.columns(5)
                    for i, title in enumerate(similar_movies[:]):
                        movie_row = data[data["title"] == title].iloc[0]
                        with cols[i % 5]:
                            display_movie_card(movie_row)
                else:
                    st.warning("No similar movies found.")
            else:
                st.error("Could not fetch movie details. Please try another movie.")
    
    return None


def get_movie_cast(movie_id,cast_df,top_n = 10):
    cast = cast_df[cast_df["movie_id"] == movie_id] \
        .sort_values("order") \
        .head(top_n)

    return cast    


TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

TMDB_IMG = "https://image.tmdb.org/t/p/w185"


def show_cast_section(movie_row, cast_df):
    st.markdown("### Top Cast")

    cast = get_movie_cast(movie_row["id"], cast_df)

    if cast.empty:
        st.info("No cast information available for this movie.")
        return

    cols = st.columns(5)  # more columns = smaller cards
    col_idx = 0

    for _, actor in cast.iterrows():
        img = get_actor_image_by_name(actor["name"],TMDB_API_KEY)
        actor_name = actor.get('name', 'Unknown')

        with cols[col_idx % 5]:
            # Display the cast member without click functionality
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="{img if img else 'https://via.placeholder.com/120x180?text=No+Image'}" 
                         style="width:120px; height:180px; object-fit:cover; border-radius:12px; 
                                box-shadow: 0 4px 8px rgba(0,0,0,0.2);"/>
                    <div style="margin-top:8px; font-weight:600; font-size:14px; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {actor_name}
                    </div>
                    <div style="font-size:12px; color:#9aa0a6;">
                        as {actor['character']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        col_idx += 1
