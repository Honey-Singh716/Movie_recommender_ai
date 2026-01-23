import os
import pickle
import pandas as pd
import streamlit as st

# Define the models directory
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')

def load_models():
    """Load all the required models and data"""
    try:
        # Movie recommender data
        data = pd.read_pickle(os.path.join(MODELS_DIR, 'cleaned_movie_data.pkl'))
        tfidf = pickle.load(open(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'), 'rb'))
        similarity = pickle.load(open(os.path.join(MODELS_DIR, 'cosine_similarity.pkl'), 'rb'))

        # Mood prediction model (PIPELINE)
        mood_model_path = os.path.join(MODELS_DIR, 'mood_text_model.pkl')
        mood_model = None

        if os.path.exists(mood_model_path):
            mood_model = pickle.load(open(mood_model_path, 'rb'))

        return data, tfidf, similarity, mood_model

    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        st.stop()
