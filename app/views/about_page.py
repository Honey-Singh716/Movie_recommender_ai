import streamlit as st


def about():
    # Header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(255,65,108,0.15), rgba(255,75,43,0.1));
        border: 1px solid rgba(255,65,108,0.3);
        border-radius: 16px; padding: 30px 36px; margin-bottom: 24px;
    ">
        <h1 style="margin-bottom:8px;">Movie Recommender AI</h1>
        <p style="color:#9aa0a6; font-size:16px; max-width:600px; line-height:1.6;">
            An intelligent, AI-powered movie discovery platform that helps you find films 
            matching your <strong>mood, preferences, and interests</strong> — powered by 
            machine learning and natural language processing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    st.markdown("### ✨ Key Features")

    features = [
        ("Actor", "Mood-Based Recommendations", "Describe your mood in plain English and get movies tailored to how you feel right now."),
        ("🤖", "AI Content Filtering", "Content-based filtering using TF-IDF and cosine similarity finds movies with similar themes, genres & style."),
        ("", "Movie Battle Arena", "Compare two movies head-to-head on ratings, revenue, popularity and more with visual charts."),
        ("", "Movie Details Explorer", "Deep-dive into any movie — cast, overview, budget, revenue, and similar film suggestions."),
        ("⭐", "Actor Filmography", "Explore the complete filmography of any actor/actress with their biography from TMDB."),
        ("❤️", "Watchlist", "Save movies to your personal watchlist accessible from any page in the sidebar."),
    ]

    f_cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with f_cols[i % 3]:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 14px; padding: 20px;
                margin-bottom: 16px; min-height: 140px;
            ">
                <div style="font-size:28px; margin-bottom:8px;">{icon}</div>
                <div style="font-weight:700; font-size:15px; margin-bottom:6px;">{title}</div>
                <div style="color:#9aa0a6; font-size:13px; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Tech stack
    st.markdown("### 🛠️ Technologies Used")

    tech = [
        ("🐍", "Python"),
        ("📊", "Scikit-learn (TF-IDF + Cosine Similarity)"),
        ("🔤", "NLTK (Lemmatization & NLP)"),
        ("🌐", "Streamlit (Web App)"),
        ("🎞️", "TMDB API (Movie Data & Posters)"),
        ("🗄️", "SQLite (Local Movie Database)"),
        ("📐", "NumPy & Pandas (Data Processing)"),
        ("📈", "ML Mood Classifier (Custom Trained)"),
    ]

    t_cols = st.columns(4)
    for i, (icon, name) in enumerate(tech):
        with t_cols[i % 4]:
            st.markdown(f"""
            <div style="
                background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.06);
                border-radius:10px; padding:12px;
                text-align:center; margin-bottom:10px;
                font-size:13px;
            ">
                <div style="font-size:22px;">{icon}</div>
                <div style="margin-top:4px;">{name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Contact
    st.markdown("### 📬 Contact & Profiles")
    
    links = [
        ("💼", "LinkedIn", "https://www.linkedin.com/in/honey-singh-in"),
        ("📓", "Kaggle",   "https://www.kaggle.com/honeysingh12coder"),
        ("🐙", "GitHub",   "https://github.com/Honey-Singh716"),
        ("✉️", "Email",    "mailto:honeysingh.work12@gmail.com"),
    ]

    lc = st.columns(4)
    for i, (icon, label, href) in enumerate(links):
        with lc[i]:
            st.markdown(f"""
            <a href="{href}" target="_blank" style="text-decoration:none;">
            <div style="
                background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.08);
                border-radius:12px; padding:16px;
                text-align:center; transition:all 0.2s;
                cursor:pointer;
            " onmouseover="this.style.borderColor='#FF416C';"
               onmouseout="this.style.borderColor='rgba(255,255,255,0.08)';">
                <div style="font-size:26px;">{icon}</div>
                <div style="font-weight:600; margin-top:6px; color:#f0f0f0;">{label}</div>
            </div>
            </a>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption(
        "🎓 This project is built for **educational and demonstration purposes only**. "
        "It does not aim to replace commercial recommendation platforms."
    )


# NOTE: about() is called from main.py; do NOT call it here at module level.
