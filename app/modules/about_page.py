import streamlit as st

def about():
    st.markdown("## 🎬 About Movie Recommender AI")

    st.markdown(
        """
        **Movie Recommender AI** is an intelligent, AI-powered web application designed
        to help users discover movies that match their **mood, preferences, and interests**.

        This project demonstrates how **machine learning** and **natural language processing (NLP)**
        can be used to build a **content-based recommendation system** that analyzes movie metadata
        and suggests similar films using cosine similarity.

        The application also integrates the **TMDB API** to provide enriched movie details such as
        ratings, cast, overview, and release information — delivering a complete and interactive
        user experience.
        """
    )

    st.markdown("---")

    st.markdown("### 🧠 Technologies Used")
    st.markdown(
        """
        - **Python**
        - **Machine Learning (Content-Based Filtering)**
        - **NLP (Text Preprocessing & Similarity Modeling)**
        - **Scikit-learn**
        - **NLTK**
        - **Streamlit**
        - **TMDB API**
        """
    )

    st.markdown("---")

    st.markdown("### ✨ Key Features")
    st.markdown(
        """
        - 🎭 Mood-based movie recommendations  
        - 🧠 Content-based filtering using cosine similarity  
        - ⚔️ Movie Battle (compare two movies)  
        - 🎬 Detailed movie information (cast, ratings, overview)  
        - 🌐 Deployed using Streamlit Community Cloud  
        """
    )

    st.markdown("---")

    st.markdown("### 📬 Contact & Profiles")

    st.markdown(
        """
        - 🔗 **LinkedIn:** https://www.linkedin.com/in/honey-singh-in
        - 🧠 **Kaggle:** https://www.kaggle.com/honeysingh12coder
        - 💻 **GitHub:** https://github.com/Honey-Singh716
        - ✉️ **Email:** honeysingh.work12@gmail.com
        """
    )

    st.markdown("---")

    st.caption(
        "⚠️ This project is built for **educational and demonstration purposes only**. "
        "It does not aim to replace commercial recommendation platforms."
    )


# Call this function when About page is selected
about_section()
