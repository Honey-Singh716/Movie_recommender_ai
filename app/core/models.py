import os
import sys
import pickle
import pandas as pd
import streamlit as st
from core.text_preprocessing import clean_and_normalize_text

# ------------------------------------------------------------------
# Pickle deserialization fix:
# The .pkl files were built in a notebook/script where
# clean_and_normalize_text lived in __main__ (or 'main').
# Inject it into those module namespaces so pickle.load() can find
# it even though the function now lives in core.text_preprocessing.
# ------------------------------------------------------------------
def _register_fn_for_pickle():
    fn = clean_and_normalize_text
    for mod_name in ('__main__', 'main'):
        mod = sys.modules.get(mod_name)
        if mod is not None and not hasattr(mod, 'clean_and_normalize_text'):
            setattr(mod, 'clean_and_normalize_text', fn)

_register_fn_for_pickle()

# __file__ = app/core/models.py  →  go up 3 levels to reach project root
MODELS_DIR = os.path.join(
    os.path.dirname(   # app/
        os.path.dirname(   # Movie_recommender_ai/
            os.path.dirname(os.path.abspath(__file__))  # app/core/
        )
    ),
    'models'
)

def rebuild_tfidf_and_similarity(data):
    """Dynamically fit TF-IDF vectorizer and compute cosine similarity matrix."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    data['tags'] = data['tags'].fillna('')
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['tags'])
    similarity = cosine_similarity(tfidf_matrix)
    return tfidf, similarity

@st.cache_resource(show_spinner="Loading AI models…")
def load_models():
    """Load all the required models and data. Cached so rebuild only happens once per session."""
    try:
        # Re-register just before loading in case modules were added after import
        _register_fn_for_pickle()

        # Load database and fetch all movies
        from utils.db_manager import init_db, load_all_movies
        init_db()
        data = load_all_movies()
        tfidf, similarity = rebuild_tfidf_and_similarity(data)

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
