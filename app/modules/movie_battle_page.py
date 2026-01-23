import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests



TMDB_API_KEY = st.secrets["TMDB_API_KEY"]



@st.cache_data(show_spinner=False)
def get_poster_from_tmdb_id(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=5).json()
        poster_path = response.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        pass

    return None




def movie_battle_ui(data):
    st.title(" Movie Battle Arena")
    st.write("Compare two movies head-to-head on popularity, ratings, revenue & more")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        movie_1 = st.selectbox(
            " Select First Movie",
            sorted(data['title'].unique()),
            key="movie1"
        )

    with col2:
        movie_2 = st.selectbox(
            "Select Second Movie",
            sorted(data['title'].unique()),
            key="movie2"
        )

    if movie_1 == movie_2:
        st.warning("Please select two different movies")
        return

    if st.button("Start Battle", type="primary"):
        m1 = data[data['title'] == movie_1].iloc[0]
        m2 = data[data['title'] == movie_2].iloc[0]


        tmdb_id_1 = int(m1['id'])
        tmdb_id_2 = int(m2['id'])
        
        poster_1 = get_poster_from_tmdb_id(tmdb_id_1)
        poster_2 = get_poster_from_tmdb_id(tmdb_id_2)


        # Safe numeric extraction
        def safe(v):
            try:
                return float(v)
            except:
                return 0.0


        st.markdown("## Movie Battle")

        col1, col2, col3 = st.columns([3, 1, 3])
 
        with col1:
            st.subheader(movie_1)
            if poster_1:
                st.image(poster_1, use_container_width=True)
            else:
                st.write("Poster not available")

        with col2:
            st.markdown("### VS")

        with col3:
            st.subheader(movie_2)
            if poster_2:
                st.image(poster_2, use_container_width=True)
            else:
                st.write("Poster not available")




        stats = {
            "Rating ": (safe(m1['vote_average']), safe(m2['vote_average'])),
            "Vote Count ": (safe(m1['vote_count']), safe(m2['vote_count'])),
            "Popularity ": (safe(m1['popularity']), safe(m2['popularity'])),
            "Budget ": (safe(m1['budget']), safe(m2['budget'])),
            "Revenue ": (safe(m1['revenue']), safe(m2['revenue'])),
            "Profit ": (
                safe(m1['revenue']) - safe(m1['budget']),
                safe(m2['revenue']) - safe(m2['budget'])
            )
        }

        st.markdown("---")

        



        st.markdown("## Movie Info")
        st.write(f"**{movie_1}** → Release Year: ***{int(m1['release_date'][:4])}***")
        st.write(f"**{movie_2}** → Release Year: ***{int(m2['release_date'][:4])}***")

        st.subheader(" Head-to-Head Comparison")
          
        def format_value(metric, value):
            if "Rating" in metric:
                return f"{value:.1f}"
            if "Vote" in metric:
                return f"{int(value):,}"
            if "Revenue" in metric or "Budget" in metric or "Profit" in metric:
                return f"${value:,.0f}"
            return f"{value:,.2f}"


        for metric, (v1, v2) in stats.items():
            st.markdown(f"### {metric}") 

            c1, c2, c3 = st.columns([3, 3, 2])

            with c1:
                st.metric(
                    label=movie_1,
                    value=format_value(metric, v1)
                )

            with c2:
                st.metric(
                    label=movie_2,
                    value=format_value(metric, v2)
                )

            with c3:
                if v1 > v2:
                    st.success(f" {movie_1}")
                elif v2 > v1:
                    st.success(f" {movie_2}")
                else:
                    st.info(" Tie")

            st.markdown("---")  # separator between metrics



        st.subheader(" Advanced Visual Analysis")
        
        def plot_mini_bar(movie_1, movie_2, v1, v2, title, ylabel):
            fig, ax = plt.subplots(figsize=(3.2, 2.4))  # small figure
            ax.bar(["movie_1", "movie_2"], [v1, v2],color = ["r","b"])
            ax.set_title(title, fontsize=9)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.tick_params(axis='x', labelsize=7) 
            ax.tick_params(axis='y', labelsize=7)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)


        
        st.markdown("## IMDb Rating")

        col_text, col_plot = st.columns([2, 1])  # 2/3 text, 1/3 plot
        
        with col_text:
            st.metric(movie_1, format_value("Rating", safe(m1['vote_average'])))
            st.metric(movie_2, format_value("Rating", safe(m2['vote_average'])))

        with col_plot:
            plot_mini_bar(
                movie_1, movie_2,
                safe(m1['vote_average']),
                safe(m2['vote_average']),
                "Rating",
                "0–10"
            )



        st.markdown("## Popularity")

        col_text, col_plot = st.columns([2, 1])

        with col_text:
            st.metric(movie_1, format_value("Popularity", safe(m1['popularity'])))
            st.metric(movie_2, format_value("Popularity", safe(m2['popularity'])))

        with col_plot:
            plot_mini_bar(
                movie_1, movie_2,
                safe(m1['popularity']),
                safe(m2['popularity']),
                "Popularity",
                "Score"
            )



        st.markdown("## ⏱ Runtime")

        col_text, col_plot = st.columns([2, 1])

        with col_text:
            st.metric(movie_1, f"{safe(m1['runtime'])} min")
            st.metric(movie_2, f"{safe(m2['runtime'])} min")

        with col_plot:
            plot_mini_bar(
                movie_1, movie_2,
                safe(m1['runtime']),
                safe(m2['runtime']),
                "Runtime",
                "Minutes"
            )


        
        st.markdown("## Budget")
        col_text, col_plot = st.columns([2, 1])

        with col_text:
            st.metric(movie_1, f"{safe(m1['budget'])}")
            st.metric(movie_2, f"{safe(m2['budget'])}")

        with col_plot:
            plot_mini_bar(
                movie_1, movie_2,
                safe(m1['budget']),
                safe(m2['budget']),
                "Budget Comparison",
                "USD ($)"
            )


        st.markdown("## Revenue")
        col_text, col_plot = st.columns([2, 1])

        with col_text:
            st.metric(movie_1, f"{safe(m1['revenue'])}")
            st.metric(movie_2, f"{safe(m2['revenue'])}")
        
        with col_plot:
            plot_mini_bar(
                movie_1, movie_2,
                safe(m1['revenue']),
                safe(m2['revenue']),
                "Revenue Comparison",
                "USD ($)"
            )

        st.markdown("## Profit")
        col_text, col_plot = st.columns([2, 1])
       
        profit = safe(m1['revenue']) - safe(m1['budget'])
        profit2 = safe(m2["revenue"]) - safe(m2["budget"])

        with col_text:
            st.metric(movie_1, profit)
            st.metric(movie_2, profit2)

        with col_plot:
            plot_mini_bar(
                movie_1,movie_2,
                profit,
                profit2,
                "Profit Comparison",
                "USD ($)"
            )




        st.markdown("---")
        st.subheader(" Final Verdict")

        score_1 = sum(v1 > v2 for k, (v1, v2) in stats.items() if "Budget" not in k)
        score_2 = sum(v2 > v1 for k, (v1, v2) in stats.items() if "Budget" not in k)


        if score_1 > score_2:
            st.success(f" **{movie_1} wins the battle!**")
        elif score_2 > score_1:
            st.success(f" **{movie_2} wins the battle!**")
        else:
            st.info(" **It's a draw!**")