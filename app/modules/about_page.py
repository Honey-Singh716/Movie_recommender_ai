import streamlit as st
from PIL import Image

def about():
    st.title(" About Movie AI Recommender")
    
    st.write("""
    A smart movie recommendation system that helps you discover films based on your preferences and mood.
    """)
    
    # How It Works Section
    st.markdown("---")
    st.header("How It Works")
    
    # Step 1
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 1. Choose Your Mood")
            st.write("Select how you're feeling from our mood categories or let our AI detect your mood.")
        with col2:
            st.image("../assets/screenshots/Mood_movie.png", use_column_width=True)
    
    # Step 2        
    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 2. Rate Movies")
            st.write("Rate a few movies to help us understand your taste better. The more you rate, the better our recommendations become!")
        with col2:
            st.image("../assets/screenshots/Recommender.png", use_column_width=True, caption="Rate and get recommendations")
    
    # Step 3
    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 3. Get Recommendations")
            st.write("Receive personalized movie suggestions based on your mood and preferences.")
        with col2:
            st.image("../assets/screenshots/movies_analysis.png", use_column_width=True, caption="Discover new movies")
    
    # Features Section
    st.markdown("---")
    st.header("✨ Key Features")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander(" Personalized Recommendations"):
            st.write("Get movie suggestions tailored specifically to your taste and viewing history.")
        with st.expander(" Mood-Based Filtering"):
            st.write("Find movies that match your current mood or desired emotional experience.")
        with st.expander(" Movie Battles"):
            st.write("Compare movies head-to-head and help improve our recommendation algorithm.")
    
    with col2:
        with st.expander(" AI-Powered Analysis"):
            st.write("Our advanced AI analyzes thousands of movies to find your perfect match.")
        with st.expander(" User-Friendly Interface"):
            st.write("Simple, intuitive design that makes finding your next favorite movie a breeze.")
        with st.expander(" Comprehensive Database"):
            st.write("Access to a vast collection of movies from different genres, years, and countries.")
    
    # About Me Section
    st.markdown("---")
    st.header(" About the Creator")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            image = Image.open("app/images/honey.jpg")
            st.image(image, use_column_width=True)
        except:
            st.image("../assets/screenshots/movie_info.png", use_column_width=True, caption="Movie details and info")
    
    with col2:
        st.markdown("""
        ### Honey Singh
        *AI/ML Engineer & Movie Enthusiast*
        
        Passionate about building intelligent systems that enhance the way we discover and enjoy movies. 
        With a background in machine learning and a love for cinema, I created this platform to help 
        people find their next favorite film.
        
        **Connect with me:**  
        [GitHub](https://github.com) | [LinkedIn](https://linkedin.com) | [Twitter](https://twitter.com)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem; color: #666;'>
        <p>Made with  by Honey Singh | © 2024 Movie AI Recommender</p>
    </div>
    """, unsafe_allow_html=True)