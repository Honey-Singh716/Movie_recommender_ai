import streamlit as st
from core.recommendations import recommend
from utils.utils import display_movie_card


def show_movie_recommender_page(data):

    st.markdown("""
    <div style="padding: 20px 0;">
        <h1 style="margin-bottom:5px;">🤖 Movie Recommender</h1>
        <p style="color: #b3b3b3; font-size: 16px;">
            Discover movies similar to what you love using AI-powered similarity analysis.
        </p>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    # How it works
    with st.expander("How it works", expanded=False):
        st.markdown("""
        - You choose **one movie** you enjoyed  
        - Our system analyzes **content similarity** using TF-IDF + cosine similarity  
        - You optionally filter by **language**  
        - We return up to 20 movies with **similar themes, cast & style**
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    language_options = {
        "all": "🌐 All Languages", "en": "🇬🇧 English", "fr": "🇫🇷 French",
        "es": "🇪🇸 Spanish", "de": "🇩🇪 German", "hi": "🇮🇳 Hindi",
        "ja": "🇯🇵 Japanese", "it": "🇮🇹 Italian", "ko": "🇰🇷 Korean",
        "ru": "🇷🇺 Russian", "pt": "🇵🇹 Portuguese", "zh": "🇨🇳 Chinese",
        "da": "🇩🇰 Danish", "sv": "🇸🇪 Swedish", "nl": "🇳🇱 Dutch",
        "fa": "🇮🇷 Persian", "th": "🇹🇭 Thai", "he": "🇮🇱 Hebrew",
        "id": "🇮🇩 Indonesian", "ta": "Tamil", "ar": "🇸🇦 Arabic",
        "tr": "🇹🇷 Turkish", "pl": "🇵🇱 Polish", "el": "🇬🇷 Greek",
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        from utils.utils import movie_search_selector
        selected_movie_row = movie_search_selector("Select a movie you like", key_prefix="recommender")
        selected_movie = selected_movie_row["title"] if selected_movie_row is not None else None

    with col2:
        selected_language = st.selectbox(
            "🌐 Language Preference",
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            help="Optional: filter recommendations by original language"
        )
        num_results = st.slider("Max results", min_value=5, max_value=20, value=10, step=5)

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn = st.columns([3, 2, 3])
    with col_btn[1]:
        get_recommendation = st.button("✨ Get AI Recommendations", use_container_width=True, type="primary")

    title_to_lang = dict(zip(data["title"], data["original_language"]))

    if get_recommendation:
        if not selected_movie:
            # If no movie is selected but a language is chosen, show movies in that language
            if selected_language != "all":
                language_movies = data[data['original_language'] == selected_language]
                language_movies = language_movies.sort_values("popularity", ascending=False)
                if not language_movies.empty:
                    lang_label = language_options[selected_language]
                    st.markdown(f"""
                    <hr>
                    <h3>Showing movies in <span style="color:#4ade80;">{lang_label}</span></h3>
                    <p style="color:#b3b3b3;">
                        These are the most popular movies available in {lang_label}.
                    </p>
                    """, unsafe_allow_html=True)

                    cols = st.columns(5)
                    shown = 0
                    for _, movie_row in language_movies.iterrows():
                        if shown >= num_results * 5:
                            break
                        with cols[shown % 5]:
                            display_movie_card(movie_row)
                        shown += 1
                else:
                    st.warning(f"No movies found in {language_options[selected_language]}.")
            else:
                st.warning("Please search for and select a movie, or choose a specific language.")
        else:
            with st.spinner("🤖 Analysing movie similarity using AI..."):
                recommendations = recommend(selected_movie, data, st.session_state.similarity, top_n=20)

                # Language filter
                if selected_language != "all":
                    filtered = [m for m in recommendations if title_to_lang.get(m) == selected_language]
                    if not filtered:
                        st.warning(
                            f"No similar movies found in {language_options[selected_language]}. "
                            "Showing all languages instead."
                        )
                    else:
                        recommendations = filtered

            if recommendations:
                st.markdown(f"""
                <hr>
                <h3>Because you liked <span style="color:#4ade80;">{selected_movie}</span></h3>
                <p style="color:#b3b3b3;">
                    These movies share similar themes, genres, cast or storytelling style.
                    Ranked by AI similarity score.
                </p>
                """, unsafe_allow_html=True)

                # Show selected movie's info as context
                sel_row = data[data["title"] == selected_movie]
                if not sel_row.empty:
                    sel_info = sel_row.iloc[0]
                    genres_list = sel_info.get("genres", [])
                    genres_str = ", ".join(genres_list) if isinstance(genres_list, list) else "—"
                    year = str(sel_info.get("release_date", ""))[:4] or "—"
                    st.caption(f"{year}  |  {genres_str}")

                st.markdown("<br>", unsafe_allow_html=True)

                display_count = min(len(recommendations), num_results * 2)
                cols = st.columns(5)
                for i, movie_title in enumerate(recommendations[:display_count]):
                    movie_rows = data[data["title"] == movie_title]
                    if movie_rows.empty:
                        continue
                    with cols[i % 5]:
                        display_movie_card(movie_rows.iloc[0])
            else:
                st.warning("No recommendations found. Try selecting a different movie.")
