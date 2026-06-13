import streamlit as st
from core.recommendations import recommend
from utils.utils import display_movie_card

def show_movie_recommender_page(data):
   
    st.markdown("""
    <div style="padding: 20px 0;">
        <h1 style="margin-bottom:5px;">Movie Recommender</h1>
        <p style="color: #b3b3b3; font-size: 16px;">
            Discover movies similar to what you love using AI-powered similarity analysis.
        </p>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### How it works
    - You choose **one movie** you enjoyed  
    - Our system analyzes **content similarity**  
    - You optionally filter by **language**  
    - We recommend movies with **similar themes & style**
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    movie_titles = data["title"].tolist()
    language_options = {
        "all": "All Languages", "en": "English", "fr": "French", "es": "Spanish",
        "ch": "Chinese", "de": "German", "hi": "Hindi", "ja": "Japanese",
        "it": "Italian", "ko": "Korean", "ru": "Russian", "pt": "Portuguese",
        "da": "Danish", "sv": "Swedish", "nl": "Dutch", "fa": "Persian (Farsi)",
        "th": "Thai", "he": "Hebrew", "id": "Indonesian", "cs": "Czech",
        "ta": "Tamil", "ro": "Romanian", "ar": "Arabic", "te": "Telugu",
        "hu": "Hungarian", "af": "Afrikaans", "is": "Icelandic", "tr": "Turkish",
        "vi": "Vietnamese", "pl": "Polish", "nb": "Norwegian Bokmål", "ky": "Kyrgyz",
        "no": "Norwegian", "sl": "Slovenian", "ps": "Pashto", "el": "Greek"
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_movie = st.selectbox(
            "Select a movie you like",
            movie_titles,
            index=None,
            placeholder="Start typing a movie name...",
            help="This movie will be used as the reference for recommendations"
        )

    with col2:
        selected_language = st.selectbox(
            "Language Preference",
            options=language_options.keys(),
            format_func=lambda x: language_options[x],
            help="Optional: filter recommendations by language"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn = st.columns([3, 2, 3])
    with col_btn[1]:
        get_recommendation = st.button("✨ Get AI Recommendations", use_container_width=True)

    
    title_to_lang = dict(zip(data["title"], data["original_language"]))

    
    if get_recommendation:
        if not selected_movie:
            # If no movie is selected but a language is chosen, show movies in that language
            if selected_language != "all":
                language_movies = data[data['original_language'] == selected_language]['title'].tolist()
                if language_movies:
                    st.markdown(f"""
                    <hr>
                    <h3>Showing movies in <span style="color:#4ade80;">{language_options[selected_language]}</span></h3>
                    <p style="color:#b3b3b3;">
                        These movies are available in {language_options[selected_language]}.
                    </p>
                    """, unsafe_allow_html=True)

                    cols = st.columns(5)
                    for i, movie_title in enumerate(language_movies[:50]):
                        movie_row = data[data["title"] == movie_title].iloc[0]
                        with cols[i % 5]:
                            display_movie_card(movie_row)
                else:
                    st.warning(f"No movies found in {language_options[selected_language]}.")
            else:
                st.warning("Please select a movie or choose a specific language to see recommendations.")
        else:
            with st.spinner("Analyzing movie similarity using AI..."):
                recommendations = recommend(selected_movie, data, st.session_state.similarity)

                # Language filter
                if selected_language != "all":
                    recommendations = [m for m in recommendations if title_to_lang.get(m) == selected_language]
                    if not recommendations:
                        st.warning(f"No similar movies found in {language_options[selected_language]}. Showing all languages instead.")
                        recommendations = recommend(selected_movie, data, st.session_state.similarity)

            
            if recommendations:
                st.markdown(f"""
                <hr>
                <h3>Because you liked <span style="color:#4ade80;">{selected_movie}</span></h3>
                <p style="color:#b3b3b3;">
                    These movies share similar themes, genres, or storytelling style.
                </p>
                """, unsafe_allow_html=True)

                cols = st.columns(5)
                for i, movie_title in enumerate(recommendations[:50]):
                    movie_row = data[data["title"] == movie_title].iloc[0]
                    with cols[i % 5]:
                        display_movie_card(movie_row)
            else:
                st.warning("No recommendations found. Try selecting a different movie.")
