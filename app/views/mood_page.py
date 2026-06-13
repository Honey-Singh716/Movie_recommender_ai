import streamlit as st
from core.recommendations import recommend_movies_by_genres
from core.mood_prediction import (
    predict_mood,
    get_genres_for_mood,
    get_mood_emoji,
    get_mood_label,
    get_all_mood_labels,
    MOOD_GENRE_MAP,
)
from utils.utils import display_movie_card


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _confidence_bar(label: str, confidence: float, color: str = "#FF416C") -> str:
    """Render an HTML confidence progress bar."""
    pct = int(confidence * 100)
    return f"""
    <div style="margin: 6px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
            <span style="font-weight:600; font-size:14px;">{label}</span>
            <span style="color:{color}; font-weight:700; font-size:14px;">{pct}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.08); border-radius:20px; height:10px; overflow:hidden;">
            <div style="background:linear-gradient(90deg,{color},#FF4B2B);
                        width:{pct}%; height:100%; border-radius:20px;
                        transition:width 0.5s ease;"></div>
        </div>
    </div>
    """


def _mood_chip(mood: str, confidence: float) -> str:
    """Render a styled mood chip badge."""
    emoji = get_mood_emoji(mood)
    label = get_mood_label(mood)
    pct = int(confidence * 100)
    return f"""
    <div style="
        display:inline-flex; align-items:center; gap:8px;
        background:linear-gradient(135deg,rgba(255,65,108,0.2),rgba(255,75,43,0.1));
        border:1px solid rgba(255,65,108,0.4);
        border-radius:50px; padding:8px 18px; margin:6px 4px;
        font-weight:600; font-size:15px; backdrop-filter:blur(4px);">
        <span style="font-size:20px;">{emoji}</span>
        <span>{label}</span>
        <span style="
            background:rgba(255,65,108,0.3); border-radius:20px;
            padding:2px 10px; font-size:12px; color:#FF416C; font-weight:700;">
            {pct}%
        </span>
    </div>
    """


def _genre_tags(genres: list[str]) -> str:
    """Render genre tags as small pills."""
    tags = "".join(
        f'<span style="background:rgba(255,255,255,0.1); border-radius:12px; '
        f'padding:3px 12px; margin:3px; font-size:12px; display:inline-block;">{g}</span>'
        for g in genres
    )
    return f'<div style="margin:8px 0;">{tags}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────

def show_mood_page(data, mood_model):
    """Display the mood-based movie recommendation page."""

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:20px 0 10px;">
        <h1 style="margin-bottom:4px;"> Mood → Movie Engine</h1>
        <p style="color:#9aa0a6; font-size:16px; margin:0;">
            Tell us how you feel in plain English — our AI maps your mood to genres
            and finds movies you'll love.
        </p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.08);">
    """, unsafe_allow_html=True)

    # ── Input ────────────────────────────────────────────────────────────────
    col_input, col_mode = st.columns([3, 1])

    with col_input:
        user_text = st.text_area(
            "How are you feeling? What kind of movie do you want?",
            placeholder=(
                "e.g.  'I'm feeling a bit lonely tonight, want something emotional and heartwarming'\n"
                "      'I want a crazy action-packed movie with a good story'\n"
                "      'Bored, surprise me with something dark and mysterious'"
            ),
            height=100,
            help="Be as descriptive as you like — the more detail, the better the match.",
            key="mood_input_text",
        )

    with col_mode:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)  # vertical align
        quality_gate = st.checkbox(
            "High quality only",
            value=True,
            help="Only show movies with ≥ 6.0 rating and ≥ 100 votes",
        )
        top_k = st.slider("Max results", min_value=10, max_value=50, value=20, step=5)

    # ── OR: Quick mood picker ─────────────────────────────────────────────
    with st.expander("  Or pick your mood directly", expanded=False):
        all_labels = get_all_mood_labels()
        mood_keys   = list(all_labels.keys())
        mood_display = list(all_labels.values())

        selected_quick = st.selectbox(
            "Choose a mood",
            options=["— select —"] + mood_display,
            key="quick_mood_select",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detect & recommend ───────────────────────────────────────────────────
    if st.button("  Find My Movies", type="primary", use_container_width=True):

        # ── Resolve input: text OR quick picker ──────────────────────────────
        quick_mood_key = None
        if selected_quick and selected_quick != "— select —":
            idx = mood_display.index(selected_quick)
            quick_mood_key = mood_keys[idx]

        if not user_text.strip() and quick_mood_key is None:
            st.warning("Please describe your mood or pick one from the quick selector.")
            return

        with st.spinner("  Analysing your mood…"):

            # ── Mood Prediction ───────────────────────────────────────────
            if quick_mood_key:
                # Direct pick: confidence = 1.0
                mood_predictions = [(quick_mood_key, 1.0)]
            else:
                mood_predictions = predict_mood(
                    user_text,
                    mood_model,
                    top_k=3,
                    min_confidence=0.20,
                )

            if not mood_predictions:
                st.warning(
                    "  Could not detect a clear mood. Try being more specific!\n\n"
                    "**Tip:** words like *sad, excited, calm, scary, romantic* work great."
                )
                return

            # ── Mood Display ──────────────────────────────────────────────
            st.markdown("###  Detected Mood Profile")

            chip_html = "".join(_mood_chip(m, c) for m, c in mood_predictions)
            st.markdown(f'<div style="margin:8px 0 16px;">{chip_html}</div>',
                        unsafe_allow_html=True)

            # Confidence bars
            bar_cols = st.columns(min(len(mood_predictions), 3))
            colors = ["#FF416C", "#f7971e", "#4776e6"]
            for i, (mood, conf) in enumerate(mood_predictions):
                with bar_cols[i]:
                    label = f"{get_mood_emoji(mood)} {get_mood_label(mood)}"
                    st.markdown(
                        _confidence_bar(label, conf, colors[i % len(colors)]),
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Genre Resolution ──────────────────────────────────────────
            # Weight genres by mood confidence — moods with higher confidence
            # contribute more genres
            weighted_genres: dict[str, float] = {}
            for mood, conf in mood_predictions:
                for rank, genre in enumerate(get_genres_for_mood(mood)):
                    # First genres in the list are more representative → higher weight
                    genre_weight = conf * (1.0 / (rank + 1))
                    weighted_genres[genre] = weighted_genres.get(genre, 0.0) + genre_weight

            # Sort by weight, take top 6 unique genres
            selected_genres = [
                g for g, _ in sorted(weighted_genres.items(), key=lambda x: -x[1])
            ][:6]

            if not selected_genres:
                st.warning("Could not determine genres for the detected mood.")
                return

            # ── Genre Display ─────────────────────────────────────────────
            st.markdown("###  Mapped Genres")
            st.markdown(
                _genre_tags(selected_genres),
                unsafe_allow_html=True,
            )

            # ── Mood→Genre explainer ──────────────────────────────────────
            with st.expander("  Why these genres?", expanded=False):
                for mood, conf in mood_predictions:
                    genres_for_mood = get_genres_for_mood(mood)
                    st.markdown(
                        f"**{get_mood_emoji(mood)} {get_mood_label(mood)}** "
                        f"({int(conf*100)}% confidence) → "
                        + ", ".join(f"`{g}`" for g in genres_for_mood)
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Recommendations ───────────────────────────────────────────
            min_avg   = 6.0 if quality_gate else 0.0
            min_count = 100 if quality_gate else 0

            recommendations = recommend_movies_by_genres(
                selected_genres, data,
                max_movies=top_k,
                min_vote_avg=min_avg,
                min_vote_count=min_count,
            )

            if recommendations.empty:
                # Fallback: relax quality gate
                recommendations = recommend_movies_by_genres(
                    selected_genres, data, max_movies=top_k,
                    min_vote_avg=0.0, min_vote_count=0,
                )

            if not recommendations.empty:
                st.markdown(
                    f"###  {len(recommendations)} Movies For Your Mood",
                    unsafe_allow_html=False,
                )
                st.caption(
                    "Ranked by genre relevance (65%) + popularity (35%). "
                    "Movies hitting more of your genre preferences rank higher."
                )

                cols = st.columns(5)
                for i, (_, movie_row) in enumerate(recommendations.iterrows()):
                    with cols[i % 5]:
                        display_movie_card(movie_row)
            else:
                st.error("No movies found. Try a different mood or disable the quality gate.")

    # ── Examples / Help ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("  Example prompts that work well", expanded=False):
        examples = [
            ("😄 Happy", "I want something funny and light to cheer me up"),
            ("😢 Sad", "I feel heartbroken and want a movie to cry to"),
            ("❤️ Romantic", "Something for a date night, sweet and passionate"),
            ("⚡ Thrilling", "Edge-of-seat thriller with a lot of suspense and twists"),
            ("👻 Scary", "A genuinely creepy horror movie that will keep me up at night"),
            ("🌟 Inspirational", "A based-on-true-story movie that motivates me"),
            ("🧙 Fantasy", "Magic, dragons, epic worldbuilding — take me somewhere else"),
            ("🔍 Mysterious", "A detective whodunit with a clever twist ending"),
            ("🎲 Bored", "Bored, just suggest me something entertaining"),
        ]
        for emoji_label, prompt in examples:
            st.markdown(f"**{emoji_label}** — *\"{prompt}\"*")
