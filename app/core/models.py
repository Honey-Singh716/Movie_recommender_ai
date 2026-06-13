import os
import pickle
import pandas as pd
import streamlit as st

# __file__ = app/core/models.py  →  go up 3 levels to reach project root (Movie_recommender_ai/)
MODELS_DIR = os.path.join(
    os.path.dirname(   # app/
        os.path.dirname(   # Movie_recommender_ai/
            os.path.dirname(os.path.abspath(__file__))  # app/core/
        )
    ),
    'models'
)

def load_models():
    """Load all the required models and data"""
    try:
        # Movie recommender data — use context managers to avoid file handle leaks
        data = pd.read_pickle(os.path.join(MODELS_DIR, 'cleaned_movie_data.pkl'))
        with open(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'), 'rb') as f:
            tfidf = pickle.load(f)
        with open(os.path.join(MODELS_DIR, 'cosine_similarity.pkl'), 'rb') as f:
            similarity = pickle.load(f)

        # Mood prediction model (PIPELINE)
        mood_model_path = os.path.join(MODELS_DIR, 'mood_text_model.pkl')
        mood_model = None

        if os.path.exists(mood_model_path):
            with open(mood_model_path, 'rb') as f:
                mood_model = pickle.load(f)

        return data, tfidf, similarity, mood_model

    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        st.stop()
