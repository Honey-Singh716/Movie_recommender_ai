import re
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# MOOD → GENRE MAPPING
# 20 moods mapped to TMDB genre names. Ordered by relevance weight.
# ─────────────────────────────────────────────────────────────────────────────
MOOD_GENRE_MAP: dict[str, list[str]] = {
    "happy":          ["Comedy", "Family", "Animation", "Music", "Adventure"],
    "sad":            ["Drama", "Romance", "Music"],
    "romantic":       ["Romance", "Drama", "Comedy"],
    "thrilling":      ["Action", "Thriller", "Crime", "Adventure"],
    "scary":          ["Horror", "Mystery", "Thriller"],
    "calm":           ["Documentary", "Animation", "Family", "Drama"],
    "dark":           ["Crime", "Thriller", "Mystery", "Drama", "Horror"],
    "excited":        ["Action", "Adventure", "Science Fiction", "Comedy", "Thriller"],
    "emotional":      ["Drama", "Romance", "Family", "Music"],
    "inspirational":  ["Drama", "History", "War", "Western"],
    "fantasy_escape": ["Fantasy", "Science Fiction", "Adventure", "Animation"],
    "patriotic":      ["War", "History", "Drama", "Action"],
    "mysterious":     ["Mystery", "Thriller", "Crime", "Science Fiction"],
    "artistic":       ["Drama", "Music", "Documentary", "Foreign"],
    "nostalgic":      ["Drama", "Family", "Animation", "Romance"],
    "adventurous":    ["Adventure", "Action", "Science Fiction", "Fantasy"],
    "funny":          ["Comedy", "Animation", "Family"],
    "violent":        ["Action", "Crime", "Thriller", "War"],
    "heartwarming":   ["Family", "Romance", "Animation", "Drama"],
    "bored":          ["Action", "Comedy", "Adventure", "Thriller", "Science Fiction"],
}

# ─────────────────────────────────────────────────────────────────────────────
# MOOD → KEYWORDS
# Primary keywords that strongly signal a mood (weight: 0.7 each)
# ─────────────────────────────────────────────────────────────────────────────
MOOD_KEYWORDS: dict[str, list[str]] = {
    "happy":          ["happy", "joy", "laugh", "fun", "cheerful", "upbeat", "lighthearted", "hilarious", "silly"],
    "sad":            ["sad", "cry", "depressed", "grief", "sorrow", "heartbreak", "melancholy", "tears", "loss"],
    "romantic":       ["romantic", "love", "romance", "date", "couple", "relationship", "passionate", "tender"],
    "thrilling":      ["thrill", "thriller", "suspense", "intense", "gripping", "edge", "adrenaline", "chase"],
    "scary":          ["scary", "horror", "fear", "terrifying", "creepy", "haunted", "nightmare", "spooky", "ghost"],
    "calm":           ["calm", "peaceful", "relax", "quiet", "soothing", "gentle", "slow", "meditative"],
    "dark":           ["dark", "grim", "sinister", "disturbing", "bleak", "violent", "brutal", "psychological"],
    "excited":        ["excited", "pumped", "hyped", "thrilled", "energetic", "fired", "action", "rush"],
    "emotional":      ["emotional", "touching", "moving", "tearful", "sentimental", "powerful", "deep"],
    "inspirational":  ["inspire", "motivate", "triumph", "overcome", "real story", "biography", "based on true"],
    "fantasy_escape": ["fantasy", "magic", "wizard", "dragon", "otherworld", "epic", "mythical", "dreamlike"],
    "patriotic":      ["war", "nation", "soldier", "army", "freedom", "country", "battle", "military", "patriot"],
    "mysterious":     ["mystery", "detective", "clue", "puzzle", "investigation", "who", "hidden", "secret"],
    "artistic":       ["artistic", "art", "poet", "experimental", "indie", "avant", "aesthetic", "surreal"],
    "nostalgic":      ["nostalgic", "childhood", "classic", "retro", "vintage", "throwback", "old"],
    "adventurous":    ["adventure", "explore", "journey", "quest", "expedition", "travel", "discover"],
    "funny":          ["funny", "comedy", "comic", "humor", "wit", "parody", "satire", "absurd", "slapstick"],
    "violent":        ["violent", "brutal", "bloody", "fight", "kill", "shoot", "gore", "intense action"],
    "heartwarming":   ["heartwarming", "sweet", "wholesome", "feel good", "warm", "uplifting", "touching family"],
    "bored":          ["bored", "boring", "entertain me", "no idea what to watch", "surprise me"],
}

# ─────────────────────────────────────────────────────────────────────────────
# MOOD → SYNONYMS  (broader, weight: 0.4 each)
# ─────────────────────────────────────────────────────────────────────────────
MOOD_SYNONYMS: dict[str, list[str]] = {
    "happy":          ["joyful", "gleeful", "delighted", "glad", "positive", "bright", "cheer", "smile"],
    "sad":            ["unhappy", "down", "low", "blue", "gloomy", "miserable", "lonely", "dreary"],
    "romantic":       ["affectionate", "lovey", "intimate", "sensual", "charming", "flirty", "crush"],
    "thrilling":      ["fast paced", "nail biting", "page turner", "tense", "breathless", "on the edge"],
    "scary":          ["frightening", "eerie", "chilling", "bone chilling", "macabre", "uncanny"],
    "calm":           ["serene", "tranquil", "mellow", "chill", "laid back", "leisurely", "steady"],
    "dark":           ["edgy", "nihilistic", "twisted", "morbid", "gritty", "shadowy", "raw"],
    "excited":        ["enthusiastic", "stoked", "amped", "eager", "electric", "bouncing"],
    "emotional":      ["poignant", "bittersweet", "wrenching", "cathartic", "resonant", "gut punch"],
    "inspirational":  ["empowering", "hopeful", "encouraging", "rousing", "uplifting", "courageous"],
    "fantasy_escape": ["imaginary", "enchanting", "whimsical", "fantastical", "surreal", "grand"],
    "patriotic":      ["nationalistic", "proud", "heroic", "sacrifice", "duty", "honour"],
    "mysterious":     ["suspenseful", "enigmatic", "cryptic", "whodunit", "unexplained", "conspiratorial"],
    "artistic":       ["creative", "poetic", "auteur", "visionary", "nuanced", "layered"],
    "nostalgic":      ["reminisce", "memories", "sentimental", "golden age", "timeless", "old school"],
    "adventurous":    ["daring", "bold", "brave", "wild", "rugged", "heroic journey", "odyssey"],
    "funny":          ["amusing", "laugh out loud", "lol", "ridiculous", "goofy", "wacky", "zany"],
    "violent":        ["gory", "action packed", "raw", "aggressive", "explosive", "warfare"],
    "heartwarming":   ["cozy", "comforting", "positive", "smile inducing", "life affirming", "hopeful"],
    "bored":          ["nothing to watch", "suggest me", "surprise me", "any movie", "not sure"],
}

# Emoji for each mood (used in UI)
MOOD_EMOJI: dict[str, str] = {
    "happy": "😄", "sad": "😢", "romantic": "❤️", "thrilling": "⚡",
    "scary": "👻", "calm": "🧘", "dark": "🌑", "excited": "🔥",
    "emotional": "💧", "inspirational": "🌟", "fantasy_escape": "🧙",
    "patriotic": "🏴", "mysterious": "🔍", "artistic": "🎨",
    "nostalgic": "📼", "adventurous": "🗺️", "funny": "😂",
    "violent": "💥", "heartwarming": "🤗", "bored": "🎲",
}

# Display-friendly labels
MOOD_LABELS: dict[str, str] = {
    "happy": "Happy", "sad": "Sad", "romantic": "Romantic",
    "thrilling": "Thrilling", "scary": "Scary", "calm": "Calm",
    "dark": "Dark", "excited": "Excited", "emotional": "Emotional",
    "inspirational": "Inspirational", "fantasy_escape": "Fantasy Escape",
    "patriotic": "Patriotic", "mysterious": "Mysterious", "artistic": "Artistic",
    "nostalgic": "Nostalgic", "adventurous": "Adventurous", "funny": "Funny",
    "violent": "Action-Violent", "heartwarming": "Heartwarming", "bored": "Surprise Me",
}


# ─────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# Multi-signal: keyword match + synonym match + ML model (if available)
# ─────────────────────────────────────────────────────────────────────────────

def _keyword_score(text: str) -> dict[str, float]:
    """Primary keyword match: +0.7 per hit (strong signal)."""
    scores: dict[str, float] = {}
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                scores[mood] = scores.get(mood, 0.0) + 0.7
    return scores


def _synonym_score(text: str) -> dict[str, float]:
    """Synonym match: +0.35 per hit (softer signal)."""
    scores: dict[str, float] = {}
    for mood, synonyms in MOOD_SYNONYMS.items():
        for syn in synonyms:
            if re.search(rf"\b{re.escape(syn)}\b", text):
                scores[mood] = scores.get(mood, 0.0) + 0.35
    return scores


def _ml_score(text: str, mood_model) -> dict[str, float]:
    """
    ML classifier signal via softmax over decision_function scores.
    Returns a dict of mood → probability [0, 1].
    """
    scores: dict[str, float] = {}
    if mood_model is None:
        return scores
    try:
        raw = mood_model.decision_function([text])
        if raw.ndim == 1:
            raw = raw.reshape(1, -1)
        # Softmax
        shifted = raw - raw.max(axis=1, keepdims=True)  # numerical stability
        exp_raw = np.exp(shifted)
        probs = exp_raw / exp_raw.sum(axis=1, keepdims=True)
        for mood, prob in zip(mood_model.classes_, probs[0]):
            scores[mood] = float(prob)
    except Exception:
        pass
    return scores


def _merge_scores(
    kw: dict[str, float],
    syn: dict[str, float],
    ml: dict[str, float],
    ml_weight: float = 1.2,
) -> dict[str, float]:
    """
    Combine keyword, synonym, and ML scores.
    ML contributes with a higher weight since it's a trained signal.
    """
    all_moods = set(MOOD_GENRE_MAP)
    merged: dict[str, float] = {}
    for mood in all_moods:
        merged[mood] = (
            kw.get(mood, 0.0)
            + syn.get(mood, 0.0)
            + ml.get(mood, 0.0) * ml_weight
        )
    return merged


def _normalize(scores: dict[str, float]) -> dict[str, float]:
    """Min-max normalize so confidence sits in [0, 1]."""
    if not scores:
        return scores
    min_v, max_v = min(scores.values()), max(scores.values())
    span = max_v - min_v if max_v != min_v else 1.0
    return {m: (v - min_v) / span for m, v in scores.items()}


def predict_mood(
    text: str,
    mood_model,
    top_k: int = 3,
    min_confidence: float = 0.25,
) -> list[tuple[str, float]]:
    """
    Predict top-k moods from free-form text.

    Returns a list of (mood, confidence) tuples sorted by confidence desc.
    confidence is in [0, 1] — 1.0 = highest relative confidence.

    Pipeline:
      1. Clean & lowercase input
      2. Keyword match  (weight 0.7 / hit)
      3. Synonym match  (weight 0.35 / hit)
      4. ML classifier  (softmax probability × 1.2)
      5. Merge + normalize
      6. Filter by min_confidence, return top_k
    """
    if not text or not text.strip():
        return []

    text_clean = text.lower().strip()

    kw_scores  = _keyword_score(text_clean)
    syn_scores = _synonym_score(text_clean)
    ml_scores  = _ml_score(text_clean, mood_model)

    merged    = _merge_scores(kw_scores, syn_scores, ml_scores)
    normed    = _normalize(merged)

    results = [
        (mood, score)
        for mood, score in normed.items()
        if score >= min_confidence
    ]
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_genres_for_mood(mood: str) -> list[str]:
    """Return genre list for a given mood key."""
    return MOOD_GENRE_MAP.get(mood.lower(), [])


def get_mood_emoji(mood: str) -> str:
    return MOOD_EMOJI.get(mood, "🎬")


def get_mood_label(mood: str) -> str:
    return MOOD_LABELS.get(mood, mood.replace("_", " ").title())


def get_all_mood_labels() -> dict[str, str]:
    """Return all mood keys with their emoji + label for display."""
    return {k: f"{MOOD_EMOJI.get(k, '🎬')} {MOOD_LABELS.get(k, k)}" for k in MOOD_GENRE_MAP}
