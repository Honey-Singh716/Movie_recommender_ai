import streamlit as st
import pandas as pd
import warnings

from core.text_preprocessing import clean_and_normalize_text
from core.models import load_models
from pages.home_page import show_home_page
from pages.movie_info_page import show_movie_info_page
from pages.mood_page import show_mood_page
from pages.actor_page import show_actor_page
from pages.movie_recommender_page import show_movie_recommender_page
from pages.movie_battle_page import movie_battle_ui
from pages.about_page import about

# Suppress warnings
warnings.filterwarnings("ignore")

cast_df = pd.read_csv("./data/processed/cast_df.csv")

# Set page configuration
st.set_page_config(
    page_title="Movie AI Recommender",
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
    
    /* Hide top border in sidebar */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
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
