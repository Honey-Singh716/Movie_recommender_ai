import streamlit as st
import pandas as pd
import warnings
from sklearn.exceptions import InconsistentVersionWarning

from modules.text_preprocessing import clean_and_normalize_text
from modules.models import load_models
from modules.home_page import show_home_page
from modules.movie_info_page import show_movie_info_page
from modules.mood_page import show_mood_page
from modules.actor_page import show_actor_page
from modules.movie_recommender_page import show_movie_recommender_page
from modules.movie_battle_page import movie_battle_ui
from modules.about_page import about

# Suppress warnings
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

cast_df = pd.read_csv("./data/cast_df.csv")

# Set page configuration
st.set_page_config(
    page_title="Movie AI Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #45a049; }
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div>div,
    .stNumberInput>div>div>input {
        background-color: #1E1E1E;
        color: white;
    }
    .stSlider>div>div>div>div { background-color: #4CAF50; }
    .stSuccess { background-color: #1E3D1E; padding: 1rem; border-radius: 0.5rem; }
    .stInfo { background-color: #1E3D4F; padding: 1rem; border-radius: 0.5rem; }
    .stWarning { background-color: #4D3D1E; padding: 1rem; border-radius: 0.5rem; }
    .stError { background-color: #4D1E1E; padding: 1rem; border-radius: 0.5rem; }
    </style>
""", unsafe_allow_html=True)



def main():
    try:
        # Load models and data
        data, tfidf, similarity,mood_model = load_models()
        
        # Store in session state for access across modules
        st.session_state.data = data
        st.session_state.tfidf = tfidf
        st.session_state.similarity = similarity
        st.session_state.mood_model = mood_model
        
    
        pages = [
            "Home",
            "Movie Information",
            "Movie Recommender",
            "Mood-Based",
            "Actor Filmography",
            "Movie Battle",
            "About"
        ]

        # Initialize once
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"

        selected_page = st.sidebar.radio(
            "Navigation",
            pages,
            index=pages.index(st.session_state.current_page)
        )

        # Sidebar click updates session state
        st.session_state.current_page = selected_page

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

if __name__ == "__main__":
    main()
