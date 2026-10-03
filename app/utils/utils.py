import math
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

        def safe_get(key, default=None):
            """Safely get a value from a pandas Series row."""
            val = movie[key] if key in movie.index else default
            # Treat NaN as missing
            if isinstance(val, float) and math.isnan(val):
                return default
            return val

        # Extract director from crew list
        crew = safe_get('crew', [])
        director = crew[0] if isinstance(crew, list) and len(crew) > 0 else "Unknown"

        # Format genres
        genres_raw = safe_get('genres', [])
        genres = ", ".join(str(g) for g in genres_raw) if isinstance(genres_raw, list) else "N/A"

        return {
            'title': safe_get('title', 'N/A'),
            'release_date': safe_get('release_date', 'N/A'),
            'vote_average': safe_get('vote_average', 'N/A'),
            'overview': safe_get('overview', 'No overview available'),
            'director': director,
            'genres': genres,
            'runtime': safe_get('runtime', 'N/A'),
            'revenue': safe_get('revenue', 'N/A'),
            'budget': safe_get('budget', 'N/A'),
            'popularity': safe_get('popularity', 'N/A')
        }
    except IndexError:
        return None
    except Exception as e:
        st.error(f"Error getting movie details: {str(e)}")
        return None


def _rating_color(rating):
    """Return a color string for a movie rating badge."""
    try:
        r = float(rating)
        if r >= 8.0:
            return "#1ed760"   # green
        elif r >= 6.5:
            return "#f7971e"   # amber
        elif r >= 5.0:
            return "#FF416C"   # orange-red
        else:
            return "#888"      # grey
    except (TypeError, ValueError):
        return "#888"


def _add_to_watchlist(title):
    """Add a movie title to the session watchlist."""
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []
    if title not in st.session_state.watchlist:
        st.session_state.watchlist.append(title)


def _remove_from_watchlist(title):
    """Remove a movie title from the session watchlist."""
    if "watchlist" in st.session_state and title in st.session_state.watchlist:
        st.session_state.watchlist.remove(title)


def display_movie_card(movie_row, key_suffix=""):
    if isinstance(movie_row, pd.Series):
        movie_row = movie_row.to_dict()

    title = movie_row.get("title", "Untitled")

    release_date = movie_row.get("release_date")
    year = release_date.split("-")[0] if isinstance(release_date, str) else "N/A"

    rating = movie_row.get("vote_average")
    rating_display = f"{rating:.1f}" if isinstance(rating, (int, float)) else "N/A"
    badge_color = _rating_color(rating)

    api_key = st.secrets.get("TMDB_API_KEY")
    poster_url = None
    
    # Try different ID fields in case dataset uses different names
    movie_id = movie_row.get("id") or movie_row.get("movie_id")
    
    if movie_id and api_key:
        poster_url = get_poster_from_tmdb_id(movie_id, api_key)

    POSTER_HEIGHT = 340

    # Watchlist state
    in_watchlist = title in st.session_state.get("watchlist", [])
    wl_icon = "❤️" if in_watchlist else "🤍"

    # Card container
    st.markdown(
        f"""
        <div style="
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: default;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            position: relative;
        " onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0 10px 20px rgba(255,65,108,0.2)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.3)';">
        """,
        unsafe_allow_html=True
    )

    # Poster with error handling
    try:
        if poster_url and isinstance(poster_url, str) and poster_url.startswith(('http://', 'https://')):
            st.markdown(
                f"""
                <div style="position:relative;">
                    <img src="{poster_url}"
                         style="
                            width:100%;
                            height:{POSTER_HEIGHT}px;
                            object-fit:cover;
                            border-radius:10px;
                            background:#2b2b2b;
                         "
                         onerror="this.onerror=null; this.src='https://placehold.co/300x450/1a1a2e/ffffff?text=No+Poster';">
                    <div style="
                        position:absolute; top:8px; right:8px;
                        background:rgba(0,0,0,0.7); border-radius:6px;
                        padding:2px 8px; font-size:13px; font-weight:700;
                        color:{badge_color};
                        backdrop-filter:blur(4px);
                    ">⭐ {rating_display}</div>
                </div>
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
                background:linear-gradient(135deg,#1a1a2e,#2d2d44);
                border-radius:10px;
                display:flex;
                flex-direction:column;
                align-items:center;
                justify-content:center;
                color:#aaa;
                font-size:14px;
                position:relative;
            ">
                <span style="font-size:40px;margin-bottom:8px;"></span>
                {title[:28]}{'...' if len(title) > 28 else ''}
                <small style="margin-top:4px;color:#777;">No poster</small>
                <div style="
                    position:absolute; top:8px; right:8px;
                    background:rgba(0,0,0,0.7); border-radius:6px;
                    padding:2px 8px; font-size:13px; font-weight:700;
                    color:{badge_color};
                ">⭐ {rating_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Title and year
    st.markdown(
        f"""
        <div style="margin-top:8px;">
            <div style="font-weight:700; font-size:14px; line-height:1.3;
                        overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
                        color:#f0f0f0;" title="{title}">
                {title}
            </div>
            <div style="color:#9aa0a6; font-size:12px; margin-top:2px;">
                {year}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Watchlist button — compact
    wl_key = f"wl_{title[:30].replace(' ', '_').replace('/', '_')}_{key_suffix}"
    if in_watchlist:
        if st.button(f"{wl_icon} Remove", key=f"rm_{wl_key}", use_container_width=True):
            _remove_from_watchlist(title)
            st.rerun()
    else:
        if st.button(f"{wl_icon} Watchlist", key=f"add_{wl_key}", use_container_width=True):
            _add_to_watchlist(title)
            st.rerun()

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
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {
            "api_key": api_key,
            "language": "en-US"
        }
        
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        poster_path = data.get("poster_path")
        
        if not poster_path and "images" in data and "posters" in data["images"]:
            posters = data["images"]["posters"]
            if posters:
                poster_path = posters[0].get("file_path")
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
            
    except (requests.exceptions.RequestException, ValueError, KeyError):
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
        except Exception:
            pass
    
    return None


@st.cache_data(show_spinner=False, ttl=86400)
def get_actor_image_by_name(actor_name, api_key):
    url = "https://api.themoviedb.org/3/search/person"
    params = {"api_key": api_key, "query": actor_name}

    try:
        res = requests.get(url, params=params, timeout=5).json()
        if res.get("results"):
            p = res["results"][0]
            if p.get("profile_path"):
                return "https://image.tmdb.org/t/p/w300" + p["profile_path"]
    except Exception:
        pass

    return None


@st.cache_data(show_spinner=False, ttl=3600)
def get_actor_info_from_tmdb(actor_name, api_key):
    """Fetch actor biography and details from TMDB."""
    if not api_key or not actor_name:
        return None
    try:
        search_url = "https://api.themoviedb.org/3/search/person"
        params = {"api_key": api_key, "query": actor_name}
        res = requests.get(search_url, params=params, timeout=5).json()
        if not res.get("results"):
            return None
        person = res["results"][0]
        person_id = person.get("id")
        if not person_id:
            return None
        # Fetch full details
        detail_url = f"https://api.themoviedb.org/3/person/{person_id}"
        detail_params = {"api_key": api_key, "language": "en-US"}
        detail = requests.get(detail_url, params=detail_params, timeout=5).json()
        return {
            "name": detail.get("name", actor_name),
            "biography": detail.get("biography", ""),
            "birthday": detail.get("birthday", ""),
            "place_of_birth": detail.get("place_of_birth", ""),
            "known_for_department": detail.get("known_for_department", "Acting"),
            "popularity": detail.get("popularity", 0),
            "profile_path": detail.get("profile_path"),
        }
    except Exception:
        return None


def search_tmdb_movies(query, api_key):
    """Search TMDB for movies matching query title."""
    if not api_key or not query:
        return []
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": api_key,
            "query": query,
            "language": "en-US",
            "page": 1,
            "include_adult": "false"
        }
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        results = response.json().get("results", [])
        return results
    except Exception as e:
        print(f"Error searching TMDB: {e}")
        return []


def fetch_and_save_movie_from_tmdb(tmdb_id, api_key):
    """
    Fetch a movie's complete details, keywords, and credits from TMDB API,
    preprocess/format them, and save them to the SQLite database.
    """
    if not api_key or not tmdb_id:
        return None
    
    from ..core.text_preprocessing import clean_and_normalize_text
    from .db_manager import insert_movie_to_db
    
    try:
        # 1. Fetch movie details
        details_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        details = requests.get(details_url, params={"api_key": api_key, "language": "en-US"}, timeout=10).json()
        
        if "id" not in details:
            return None
            
        # 2. Fetch keywords
        keywords_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/keywords"
        keywords_data = requests.get(keywords_url, params={"api_key": api_key}, timeout=10).json()
        keywords_list = [k["name"] for k in keywords_data.get("keywords", [])]
        
        # 3. Fetch credits (cast & crew)
        credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
        credits_data = requests.get(credits_url, params={"api_key": api_key}, timeout=10).json()
        
        raw_cast = credits_data.get("cast", [])
        raw_crew = credits_data.get("crew", [])
        
        # Extract directors first, then other crew names
        directors = [member["name"] for member in raw_crew if member.get("job") == "Director"]
        other_crew = [member["name"] for member in raw_crew if member.get("job") != "Director"]
        crew_list = directors + other_crew
        
        # Limit cast list
        cast_names = [member["name"] for member in raw_cast[:5]]
        
        # Prep collapsed columns
        genres_list = [g["name"] for g in details.get("genres", [])]
        genres_collapsed = "".join(g.replace(" ", "") for g in genres_list)
        keywords_collapsed = "".join(k.replace(" ", "") for k in keywords_list)
        cast_collapsed = "".join(c.replace(" ", "") for c in cast_names)
        overview = details.get("overview") or ""
        overview_cleaned = clean_and_normalize_text(overview)
        
        tags = f"{genres_collapsed} {keywords_collapsed} {cast_collapsed} {overview_cleaned}"
        
        # Prep movies table row
        movie_row = {
            "budget": details.get("budget", 0),
            "genres": genres_list,
            "homepage": details.get("homepage", ""),
            "id": int(tmdb_id),
            "keywords": keywords_list,
            "original_language": details.get("original_language", "en"),
            "original_title": details.get("original_title", details.get("title")),
            "overview": overview,
            "popularity": details.get("popularity", 0.0),
            "production_companies": [pc["name"] for pc in details.get("production_companies", [])],
            "production_countries": [pc["name"] for pc in details.get("production_countries", [])],
            "release_date": details.get("release_date", ""),
            "revenue": details.get("revenue", 0),
            "runtime": details.get("runtime", 0),
            "spoken_languages": [sl["name"] for sl in details.get("spoken_languages", [])],
            "status": details.get("status", "Released"),
            "tagline": details.get("tagline", ""),
            "title": details.get("title"),
            "vote_average": details.get("vote_average", 0.0),
            "vote_count": details.get("vote_count", 0),
            "cast": cast_names,
            "crew": crew_list,
            "genres_collapsed": genres_collapsed,
            "keywords_collapsed": keywords_collapsed,
            "cast_collapsed": cast_collapsed,
            "overview_cleaned": overview_cleaned,
            "tags": tags
        }
        
        # Prep cast table rows
        cast_rows = []
        for member in raw_cast[:15]:  # Store up to 15 cast members in DB
            cast_rows.append({
                "cast_id": member.get("cast_id", 0),
                "person_id": member.get("id", 0),
                "name": member.get("name", "Unknown"),
                "character": member.get("character", "Unknown"),
                "order": member.get("order", 999),
                "movie_id": int(tmdb_id),
                "movie_title": details.get("title")
            })
            
        # Save to SQLite
        insert_movie_to_db(movie_row, cast_rows)
        return movie_row
    except Exception as e:
        print(f"Error fetching/saving movie from TMDB: {e}")
        return None


def movie_search_selector(label="Search for a movie:", key_prefix="search"):
    """
    Renders a text input for fuzzy/keyword searching movies from local DB or TMDB.
    Returns the selected movie row (pandas Series/dict) or None.
    """
    import streamlit as st
    from .db_manager import search_movies_in_db, load_all_movies
    from core.models import rebuild_tfidf_and_similarity

    # Use a session state variable to store the final selection
    sel_key = f"{key_prefix}_selected_movie_val"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = None

    search_query = st.text_input("Type movie title...", placeholder="e.g. Iron Man, Avatar...", key=f"{key_prefix}_query")
    
    selected_movie_title = None
    
    if search_query:
        # Track search history
        if "search_history" not in st.session_state:
            st.session_state.search_history = []
        if search_query not in st.session_state.search_history:
            st.session_state.search_history.insert(0, search_query)
            st.session_state.search_history = st.session_state.search_history[:5]  # keep last 5

        matches = search_movies_in_db(search_query)
        api_key = st.secrets.get("TMDB_API_KEY")
        
        if not matches:
            if api_key:
                st.info(f"No local matches for '{search_query}'. Searching TMDB...")
                tmdb_results = search_tmdb_movies(search_query, api_key)
                if tmdb_results:
                    options = {res["id"]: f"{res['title']} ({res.get('release_date', '')[:4]}) [Import from TMDB]" for res in tmdb_results[:5]}
                    selected_tmdb_id = st.selectbox(
                        "Found matches on TMDB. Choose one to import:", 
                        options=list(options.keys()), 
                        format_func=lambda x: options[x],
                        key=f"{key_prefix}_tmdb_select"
                    )
                    if st.button("📥 Import and Load Movie", key=f"{key_prefix}_import_btn", use_container_width=True):
                        with st.spinner("Importing from TMDB..."):
                            new_movie = fetch_and_save_movie_from_tmdb(selected_tmdb_id, api_key)
                            if new_movie:
                                st.success(f"Imported '{new_movie['title']}'!")
                                # Rebuild TF-IDF and similarity
                                st.session_state.data = load_all_movies()
                                tfidf, similarity = rebuild_tfidf_and_similarity(st.session_state.data)
                                st.session_state.tfidf = tfidf
                                st.session_state.similarity = similarity
                                st.session_state[sel_key] = new_movie['title']
                                st.rerun()
                else:
                    st.warning("No matches found on TMDB either.")
            else:
                st.warning("No local matches found. (Add TMDB_API_KEY in secrets to search online)")
        else:
            # We have matches
            selected_movie_title = st.selectbox(
                label,
                matches,
                key=f"{key_prefix}_match_select"
            )
            st.session_state[sel_key] = selected_movie_title
    else:
        st.session_state[sel_key] = None

    # Return the selected movie data row if one is selected
    current_sel = st.session_state.get(sel_key)
    if current_sel:
        data = st.session_state.get('data')
        if data is not None:
            matching_rows = data[data["title"] == current_sel]
            if not matching_rows.empty:
                return matching_rows.iloc[0]
    return None
