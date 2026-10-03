import streamlit as st
import pandas as pd
import requests


# Import from shared utils — do NOT redefine get_poster_from_tmdb_id here
from utils.utils import get_poster_from_tmdb_id


def _format_money(value):
    """Format a numeric value as a human-readable dollar amount."""
    try:
        v = float(value)
        if v == 0:
            return "N/A"
        if v >= 1_000_000_000:
            return f"${v/1_000_000_000:.2f}B"
        if v >= 1_000_000:
            return f"${v/1_000_000:.1f}M"
        return f"${v:,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def _format_value(metric, value):
    """Format a metric value for display."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if "Rating" in metric:
        return f"{v:.1f} / 10"
    if "Vote" in metric:
        return f"{int(v):,}"
    if "Popularity" in metric:
        return f"{v:,.1f}"
    if "Runtime" in metric:
        return f"{int(v)} min"
    if any(k in metric for k in ("Revenue", "Budget", "Profit")):
        return _format_money(v)
    return f"{v:,.2f}"


def _safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _winner_banner(label, color="#1ed760"):
    return f"""
    <div style="
        background: linear-gradient(90deg, {color}22, {color}11);
        border: 1px solid {color}55;
        border-radius: 10px; padding: 8px 16px;
        text-align: center; font-weight: 700;
        color: {color}; font-size: 15px;
    ">🏆 {label} wins</div>
    """


def movie_battle_ui(data):
    st.markdown("""
    <div style="padding:20px 0 10px;">
        <h1 style="margin-bottom:4px;">Movie Battle Arena</h1>
        <p style="color:#9aa0a6; font-size:16px; margin:0;">
            Compare two movies head-to-head on ratings, revenue, popularity &amp; more.
        </p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.08);">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        from utils.utils import movie_search_selector
        m1_row = movie_search_selector("Select First Movie", key_prefix="battle_m1")
        movie_1 = m1_row["title"] if m1_row is not None else None

    with col2:
        m2_row = movie_search_selector("Select Second Movie", key_prefix="battle_m2")
        movie_2 = m2_row["title"] if m2_row is not None else None

    if not movie_1 or not movie_2:
        st.info("👆 Search and select **two movies** above to start the battle.")
        return

    if movie_1 == movie_2:
        st.warning("Please select two **different** movies.")
        return

    if st.button("Start Battle!", type="primary", use_container_width=True):
        m1 = data[data['title'] == movie_1].iloc[0]
        m2 = data[data['title'] == movie_2].iloc[0]

        api_key = st.secrets.get("TMDB_API_KEY")
        # Use shared cached function — not a local duplicate
        poster_1 = get_poster_from_tmdb_id(int(m1['id']), api_key) if api_key else None
        poster_2 = get_poster_from_tmdb_id(int(m2['id']), api_key) if api_key else None

        # ── Poster row ───────────────────────────────────────────────────────
        st.markdown("---")
        c1, c_vs, c2 = st.columns([4, 1, 4])

        with c1:
            st.subheader(movie_1)
            if poster_1:
                st.image(poster_1, use_column_width="always")
            else:
                st.markdown("""<div style="height:300px;background:#1a1a2e;border-radius:12px;
                    display:flex;align-items:center;justify-content:center;color:#666;">
                    No Poster</div>""", unsafe_allow_html=True)

        with c_vs:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:center;
                        height:100%;font-size:32px;font-weight:900;
                        background:linear-gradient(90deg,#FF416C,#FF4B2B);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        padding-top:100px;">
                VS
            </div>""", unsafe_allow_html=True)

        with c2:
            st.subheader(movie_2)
            if poster_2:
                st.image(poster_2, use_column_width="always")
            else:
                st.markdown("""<div style="height:300px;background:#1a1a2e;border-radius:12px;
                    display:flex;align-items:center;justify-content:center;color:#666;">
                    No Poster</div>""", unsafe_allow_html=True)

        # ── Release year ─────────────────────────────────────────────────────
        def safe_year(val):
            return str(val)[:4] if isinstance(val, str) and len(val) >= 4 else "N/A"

        st.markdown("---")
        cy1, cy2 = st.columns(2)
        cy1.info(f"**{movie_1}** — {safe_year(m1['release_date'])}")
        cy2.info(f"**{movie_2}** — {safe_year(m2['release_date'])}")

        # ── Stats definition ─────────────────────────────────────────────────
        profit_1 = _safe_float(m1['revenue']) - _safe_float(m1['budget']) \
            if _safe_float(m1['revenue']) > 0 and _safe_float(m1['budget']) > 0 else 0.0
        profit_2 = _safe_float(m2['revenue']) - _safe_float(m2['budget']) \
            if _safe_float(m2['revenue']) > 0 and _safe_float(m2['budget']) > 0 else 0.0

        stats = {
            "⭐ Rating":      (_safe_float(m1['vote_average']),  _safe_float(m2['vote_average'])),
            "Vote Count":  (_safe_float(m1['vote_count']),    _safe_float(m2['vote_count'])),
            "📊 Popularity":  (_safe_float(m1['popularity']),    _safe_float(m2['popularity'])),
            "💰 Budget":      (_safe_float(m1['budget']),         _safe_float(m2['budget'])),
            "Revenue":     (_safe_float(m1['revenue']),        _safe_float(m2['revenue'])),
            "💹 Profit":      (profit_1,                          profit_2),
            "Runtime":     (_safe_float(m1['runtime']),        _safe_float(m2['runtime'])),
        }

        # ── Head-to-Head comparison table ────────────────────────────────────
        st.markdown("---")
        st.subheader("📊 Head-to-Head Comparison")

        for metric, (v1, v2) in stats.items():
            st.markdown(f"#### {metric}")
            mc1, mc2, mc3 = st.columns([3, 3, 2])

            mc1.metric(label=movie_1[:25], value=_format_value(metric, v1))
            mc2.metric(label=movie_2[:25], value=_format_value(metric, v2))

            with mc3:
                if v1 > v2:
                    st.markdown(_winner_banner(movie_1[:18], "#1ed760"), unsafe_allow_html=True)
                elif v2 > v1:
                    st.markdown(_winner_banner(movie_2[:18], "#1da1f2"), unsafe_allow_html=True)
                else:
                    st.markdown(_winner_banner("Tie", "#ffad1f"), unsafe_allow_html=True)

            st.markdown("---")

        # ── Bar charts ───────────────────────────────────────────────────────
        st.subheader("Visual Analysis")

        m1_label = movie_1[:15] + "…" if len(movie_1) > 15 else movie_1
        m2_label = movie_2[:15] + "…" if len(movie_2) > 15 else movie_2

        chart_metrics = {
            "⭐ Rating":     "⭐ Rating",
            "📊 Popularity": "📊 Popularity",
            "Runtime":    "Runtime",
        }

        for label, metric_key in chart_metrics.items():
            v1, v2 = stats[metric_key]
            chart_df = pd.DataFrame(
                {label: [v1, v2]},
                index=[m1_label, m2_label]
            )
            st.markdown(f"**{label}**")
            st.bar_chart(chart_df, height=180)

        # ── Final Verdict ────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("🏆 Final Verdict")

        # Exclude Budget from verdict (it's a cost, not a positive metric)
        verdict_metrics = {k: v for k, v in stats.items() if "Budget" not in k}
        score_1 = sum(v1 > v2 for v1, v2 in verdict_metrics.values())
        score_2 = sum(v2 > v1 for v1, v2 in verdict_metrics.values())
        ties    = sum(v1 == v2 for v1, v2 in verdict_metrics.values())

        vc1, vc2, vc3 = st.columns(3)
        vc1.metric(movie_1[:20], f"{score_1} wins")
        vc2.metric("🤝 Ties", ties)
        vc3.metric(movie_2[:20], f"{score_2} wins")

        st.markdown("<br>", unsafe_allow_html=True)

        if score_1 > score_2:
            st.success(f"🏆 **{movie_1}** wins the battle with **{score_1}** out of {len(verdict_metrics)} metrics!")
        elif score_2 > score_1:
            st.success(f"🏆 **{movie_2}** wins the battle with **{score_2}** out of {len(verdict_metrics)} metrics!")
        else:
            st.info("🤝 **It's a perfect draw!** Both movies are equally matched.")