import requests
import pandas as pd
import streamlit as st
import time

def get_movie_details(movie_title, data):
    """
    Fetch structured movie details.
    Returns a dictionary with movie information.
    """
    try:
        movie = data[data['title'] == movie_title].iloc[0]
        
        # Extract director from crew (first person listed)
        director = movie['crew'][0] if isinstance(movie.get('crew'), list) and movie.get('crew') else "Unknown"
        
        # Format genres
        genres = ", ".join(str(g) for g in movie.get('genres', [])) if isinstance(movie.get('genres'), list) else "N/A"
        
        return {
            'title': movie.get('title', 'N/A'),
            'release_date': movie.get('release_date', 'N/A'),
            'vote_average': movie.get('vote_average', 'N/A'),
            'overview': movie.get('overview', 'No overview available'),
            'director': director,
            'genres': genres,
            'runtime': movie.get('runtime', 'N/A'),
            'revenue': movie.get('revenue', 'N/A'),
            'budget': movie.get('budget', 'N/A'),
            'popularity': movie.get('popularity', 'N/A')
        }
    except IndexError:
        return None
    except Exception as e:
        st.error(f"Error getting movie details: {str(e)}")
        return None


def display_movie_card(movie_row):
    if isinstance(movie_row, pd.Series):
        movie_row = movie_row.to_dict()

    title = movie_row.get("title", "Untitled")

    release_date = movie_row.get("release_date")
    year = release_date.split("-")[0] if isinstance(release_date, str) else "N/A"

    rating = movie_row.get("vote_average")
    rating = f"{rating:.1f}" if isinstance(rating, (int, float)) else "N/A"

    api_key = st.secrets.get("TMDB_API_KEY")
    poster_url = None
    if movie_row.get("id") and api_key:
        poster_url = get_poster_from_tmdb_id(movie_row["id"], api_key)

    POSTER_HEIGHT = 340

    # Card container
    st.markdown(
        """
        <div style="
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: default;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 10px 20px rgba(255,65,108,0.2)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.3)';">
        """,
        unsafe_allow_html=True
    )

    # Poster with error handling
    try:
        if poster_url and isinstance(poster_url, str) and poster_url.startswith(('http://', 'https://')):
            st.markdown(
                f"""
                <img src="{poster_url}"
                     style="
                        width:100%;
                        height:{POSTER_HEIGHT}px;
                        object-fit:cover;
                        border-radius:10px;
                        background:#2b2b2b;
                     "
                     onerror="this.onerror=null; this.src='https://via.placeholder.com/300x450?text=No+Poster+Available';">
                """,
                unsafe_allow_html=True
            )
        else:
            raise ValueError("Invalid poster URL")
    except Exception:
        st.markdown(
            f"""
            <div style="
                width:100%;
                height:{POSTER_HEIGHT}px;
                background:#2b2b2b;
                border-radius:10px;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#aaa;
                font-size:16px;
            ">
                {title[:30]}{'...' if len(title) > 30 else ''}
                <br>
                <small>No poster available</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Divider
    st.markdown(
        """
        <div style="
            width:100%;
            height:4px;
            background:#000;
            margin:10px 0;
            border-radius:2px;
        "></div>
        """,
        unsafe_allow_html=True
    )

    # Text
    st.markdown(f"**{title}**")
    st.caption(f"{year} ⭐ {rating}")

    # Close card
    st.markdown("</div>", unsafe_allow_html=True)



TMDB_IMG = "https://image.tmdb.org/t/p/w500"

@st.cache_data(show_spinner=False, ttl=86400)  # Cache for 24 hours
def get_poster_from_tmdb_id(tmdb_id, api_key):
    """
    Get movie poster URL from TMDB API with improved reliability
    """
    if not api_key or not tmdb_id:
        return None
    
    # First try to get from the main movie details
    try:
        # Try with movie details endpoint first
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {
            "api_key": api_key,
            "language": "en-US"
        }
        
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        # Try to get poster from main response
        poster_path = data.get("poster_path")
        
        # If no poster in main response, try the images endpoint
        if not poster_path and "images" in data and "posters" in data["images"]:
            posters = data["images"]["posters"]
            if posters:
                poster_path = posters[0].get("file_path")
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
            
    except (requests.exceptions.RequestException, ValueError, KeyError):
        # If any error occurs, try the images endpoint directly
        try:
            images_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images"
            params = {"api_key": api_key}
            
            response = requests.get(images_url, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()
            
            if "posters" in data and data["posters"]:
                poster_path = data["posters"][0].get("file_path")
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"
        except:
            pass
    
    return None


@st.cache_data(show_spinner=False)
def get_actor_image_by_name(actor_name, api_key):

    url = "https://api.themoviedb.org/3/search/person"
    params = {"api_key": api_key, "query": actor_name}

    try:
        res = requests.get(url, params=params, timeout=5).json()
        if res.get("results"):
            p = res["results"][0]
            if p.get("profile_path"):
                return "https://image.tmdb.org/t/p/w300" + p["profile_path"]
    except:
        pass

    return None





