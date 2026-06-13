import streamlit as st
from core.recommendations import recommend_movies_by_genres
from core.mood_prediction import predict_mood, get_genres_for_mood
from utils.utils import display_movie_card

def show_mood_page(data, mood_model):
    """Display the mood-based recommendation page"""
    st.header(" Mood-Based Movie Recommendations")
    st.write("Describe the type of movie you're looking for and we'll find the perfect match!")

    user_text = st.text_input(
        "Describe the kind of movie you want to watch:",
        placeholder="e.g., 'I want a funny action movie with car chases'",
        help="Describe the type of movie you're in the mood for"
    )

    if st.button("Find Movies", type="primary"):
        if not user_text.strip():
            st.warning("Please describe what kind of movie you're looking for.")
        else:
            with st.spinner("Analyzing your mood and finding perfect movies..."):
                mood_predictions = predict_mood(
                    user_text, mood_model, top_k=3
                )

                if mood_predictions:
                    st.success(
                        " Detected moods: " +
                        ", ".join(f"{mood} ({prob:.1%})" for mood, prob in mood_predictions)
                    )

                    selected_genres = []
                    for mood, _ in mood_predictions:
                        selected_genres.extend(get_genres_for_mood(mood))

                    selected_genres = list(set(selected_genres))

                    if selected_genres:
                        st.info(f" Looking for {', '.join(selected_genres)} movies...")

                        recommendations = recommend_movies_by_genres(
                            selected_genres, data, max_movies=50
                        )

                        if not recommendations.empty:
                            st.success(f" Found {len(recommendations)} movies you might enjoy:")

                            cols = st.columns(5)
                            for i, (_, movie_row) in enumerate(recommendations.iterrows()):
                                with cols[i % 5]:
                                    display_movie_card(movie_row)
                        else:
                            st.warning("No movies found for the selected genres.")
                    else:
                        st.warning("Could not determine genres for the detected mood.")
                else:
                    st.warning("Could not detect any specific mood. Try being more descriptive!")

    st.write("--------------------------------------------------------------------------------------")
    st.subheader(" Examples")
    st.write("- A funny movie that makes me laugh")
    st.write("- Something romantic for date night")
    st.write("- A thrilling action movie")
    st.write("- A scary horror film")
