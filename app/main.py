import streamlit as st
import pandas as pd
import os
import warnings

from core.text_preprocessing import clean_and_normalize_text
from core.models import load_models
from views.home_page import show_home_page
from views.movie_info_page import show_movie_info_page
from views.mood_page import show_mood_page
from views.actor_page import show_actor_page
from views.movie_recommender_page import show_movie_recommender_page
from views.movie_battle_page import movie_battle_ui
from views.about_page import about

# Suppress warnings
warnings.filterwarnings("ignore")

# Resolve data path relative to this file so it works from any working directory
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_APP_DIR)
DATA_DIR = os.path.join(_PROJECT_ROOT, "data", "processed")

# Set page configuration
st.set_page_config(
    page_title="Movie AI Recommender",
    # page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main { 
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); 
        color: #F8F9FA; 
    }
    
    /* Modern Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6);
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div>div,
    .stNumberInput>div>div>input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus, 
    .stSelectbox>div>div>div>div:focus {
        border-color: #FF416C;
        box-shadow: 0 0 0 2px rgba(255, 65, 108, 0.2);
    }
    
    /* Sliders */
    .stSlider>div>div>div>div { background: linear-gradient(90deg, #FF416C, #FF4B2B); }
    
    /* Alerts */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 1rem;
    }
    .stSuccess { background: rgba(30, 215, 96, 0.15); border-left: 4px solid #1ed760; }
    .stInfo { background: rgba(29, 161, 242, 0.15); border-left: 4px solid #1da1f2; }
    .stWarning { background: rgba(255, 173, 31, 0.15); border-left: 4px solid #ffad1f; }
    .stError { background: rgba(224, 36, 94, 0.15); border-left: 4px solid #e0245e; }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF416C, #FF4B2B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Watchlist badge */
    .wl-badge {
        display: inline-block;
        background: linear-gradient(90deg, #FF416C, #FF4B2B);
        border-radius: 50px;
        padding: 2px 12px;
        font-size: 12px;
        font-weight: 700;
        color: white;
        margin-left: 6px;
    }
    </style>
""", unsafe_allow_html=True)


def _render_sidebar_extras(data):
    """Render watchlist and quick stats in the sidebar."""
    st.sidebar.markdown("---")

    # ── Quick Stats ────────────────────────────────────────────────
    st.sidebar.markdown("###  Library Stats")
    total = len(data)
    genres_col = data.get("genres") if hasattr(data, "get") else None
    # Count unique genres safely
    try:
        all_genres = set()
        for g_list in data["genres"].dropna():
            if isinstance(g_list, list):
                all_genres.update(g_list)
        num_genres = len(all_genres)
    except Exception:
        num_genres = "—"

    col_a, col_b = st.sidebar.columns(2)
    col_a.metric("Movies", f"{total:,}")
    col_b.metric("Genres", num_genres)

    # ── Watchlist ─────────────────────────────────────────────────
    st.sidebar.markdown("---")
    watchlist = st.session_state.get("watchlist", [])
    wl_count = len(watchlist)
    wl_label = f"❤️ Watchlist ({wl_count})" if wl_count else "🤍 Watchlist (empty)"
    with st.sidebar.expander(wl_label, expanded=False):
        if watchlist:
            for title in watchlist:
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{title[:22]}{'…' if len(title)>22 else ''}**")
                if c2.button("✕", key=f"sidebar_rm_{title[:20]}"):
                    st.session_state.watchlist.remove(title)
                    st.rerun()
            if st.button(" Clear Watchlist", use_container_width=True):
                st.session_state.watchlist = []
                st.rerun()
        else:
            st.caption("Add movies using the 🤍 button on any card.")

    # ── Search History ───────────────────────────────────────────
    history = st.session_state.get("search_history", [])
    if history:
        st.sidebar.markdown("---")
        with st.sidebar.expander(" Recent Searches", expanded=False):
            for h in history:
                st.caption(f" {h}")


def main():
    try:
        # Load models and data (cached — runs only once per session)
        data, tfidf, similarity, mood_model = load_models()
        from utils.db_manager import load_cast_data
        cast_df = load_cast_data()

        # Store in session state for access across modules
        st.session_state.data = data
        st.session_state.tfidf = tfidf
        st.session_state.similarity = similarity
        st.session_state.mood_model = mood_model

        # Initialize watchlist
        if "watchlist" not in st.session_state:
            st.session_state.watchlist = []
    
        pages = [
            "Home",
            "Movie Information",
            "Movie Recommender",
            "Mood-Based",
            "Actor Filmography",
            "Movie Battle",
            "About"
        ]

        # Map display names → internal page keys
        page_keys = {
            "Home": "Home",
            "Movie Information": "Movie Information",
            "Movie Recommender": "Movie Recommender",
            "Mood-Based": "Mood-Based",
            "Actor Filmography": "Actor Filmography",
            "Movie Battle": "Movie Battle",
            "About": "About",
        }

        # Initialize once
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"

        # Find which display label matches current page
        current_display = next((k for k, v in page_keys.items() if v == st.session_state.current_page), pages[0])

        # Sidebar logo/header
        st.sidebar.markdown("""
        <div style="text-align:center; padding:10px 0 4px;">
            <span style="font-size:36px;"></span><br>
            <span style="font-weight:800; font-size:18px; 
                         background:linear-gradient(90deg,#FF416C,#FF4B2B);
                         -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Movie AI
            </span>
        </div>
        """, unsafe_allow_html=True)

        selected_display = st.sidebar.radio(
            "Navigation",
            pages,
            index=pages.index(current_display)
        )

        # Update session state
        st.session_state.current_page = page_keys[selected_display]

        # Render sidebar extras (stats, watchlist, history)
        _render_sidebar_extras(data)

        current_page = st.session_state.current_page
        
        # Home Page
        if current_page == "Home":
            show_home_page(data)
        
        # Movie Information Page
        elif current_page == "Movie Information":
            show_movie_info_page(data, cast_df)
        
        # Movie Recommender Page
        elif current_page == "Movie Recommender":
            show_movie_recommender_page(data)

        # Mood-Based Recommendations
        elif current_page == "Mood-Based":
            show_mood_page(data, mood_model)
        
        # Actor Filmography Page
        elif current_page == "Actor Filmography":
            actor_name = st.session_state.get('actor_search', '')
            show_actor_page(data, initial_actor=actor_name)

        # Movie Battle Page
        elif current_page == "Movie Battle":
            movie_battle_ui(data)

        elif current_page == "About":
            about()    
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try again or contact support if the issue persists.")
        import traceback
        with st.expander(" Error details (for debugging)"):
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
