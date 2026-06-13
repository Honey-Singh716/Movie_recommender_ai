import re
import streamlit as st
import numpy as np

mood_genre_map = {
    "happy": ["Comedy", "Family", "Music", "Animation"],
    "sad": ["Drama", "Romance"],
    "romantic": ["Romance", "Drama"],
    "thrilling": ["Action", "Thriller", "Crime"],
    "scary": ["Horror"],
    "calm": ["Animation", "Family", "Drama", "Documentary"],
    "dark": ["Crime", "Mystery", "Drama","Thriller"],
    "excited": ["Action", "Adventure", "Science Fiction", "Thriller","Comedy"],
    "emotional": ["Drama", "Family", "Romance"],
    "inspirational": ["Drama", "Biography", "History", "Sport"],
    "fantasy_escape": ["Fantasy", "Science Fiction", "Adventure"],
    "patriotic": ["War", "History", "Drama"],
    "mysterious": ["Mystery", "Thriller"],
    "artistic": ["Drama", "Music", "Independent"],
    "classic": ["Drama", "Romance", "Western"]
}

# synonyms to boost keyword accuracy
mood_synonyms = {
    "happy": ["joyful", "cheerful", "glad", "delighted", "uplifting", "positive", "fun"],
    "sad": ["unhappy", "down", "low", "depressed", "heartbroken", "melancholy", "blue"],
    "romantic":["love", "loving", "affectionate", "passionate", "relationship", "romance"],
    "thrilling": ["exciting", "intense", "adrenaline", "edge of seat", "gripping", "fast paced"],
    "scary": ["fear", "frightening", "creepy", "terrifying", "haunting", "spooky"],
    "calm": ["peaceful", "relaxed", "soothing", "quiet", "gentle", "slow"],
    "dark": ["grim", "bleak", "intense", "serious", "violent", "disturbing"],
    "excited": ["thrilled", "pumped", "energetic", "hyped", "enthusiastic"],
    "emotional": ["touching", "tearful", "moving", "sentimental", "emotional"],
    "inspirational": ["motivational", "uplifting", "encouraging", "empowering", "hopeful"],
    "fantasy_escape": ["magical", "imaginary", "otherworldly", "dreamlike", "epic"],
    "patriotic": ["nationalistic", "freedom", "country", "soldier", "army", "war"],
    "mysterious": ["suspense", "unknown", "puzzling", "enigmatic", "investigation"],
    "artistic": ["creative", "aesthetic", "experimental", "artsy", "poetic"],
    "classic": ["old", "vintage", "retro", "timeless", "golden era"]
}



def predict_mood(text, mood_model, top_k=2, min_confidence=0.35):
    if not text or not text.strip():
        return []

    text = text.lower().strip()
    scores = {}

    # Keyword + synonym matching
    for mood in mood_genre_map:
        if re.search(rf"\b{mood}\b", text):
            scores[mood] = scores.get(mood, 0) + 0.6

        for syn in mood_synonyms.get(mood, []):
            if re.search(rf"\b{syn}\b", text):
                scores[mood] = scores.get(mood, 0) + 0.4

    # ML confidence using decision_function (CORRECT WAY)
    try:
        decision_scores = mood_model.decision_function([text])

        if decision_scores.ndim == 1:
            decision_scores = np.array([decision_scores])

        exp_scores = np.exp(decision_scores)
        probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

        for mood, prob in zip(mood_model.classes_, probs[0]):
            scores[mood] = scores.get(mood, 0) + float(prob)

    except Exception as e:
        st.warning(f"ML model error: {e}")

    # Normalize scores
    if scores:
        max_score = max(scores.values())
        scores = {m: s / max_score for m, s in scores.items()}

    # Filter + rank
    results = [(m, s) for m, s in scores.items() if s >= min_confidence]
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_k]



def get_genres_for_mood(mood):
    return mood_genre_map.get(mood.lower(), [])
