import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Video Game Analytics Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C63FF, #FF6584);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #6C63FF;
    }
</style>
""", unsafe_allow_html=True)

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    games = pd.read_csv("data/games.csv")
    vgsales = pd.read_csv("data/vgsales.csv")

    # --- Clean games.csv ---
    games = games.drop(columns=["Unnamed: 0"], errors="ignore")
    # Convert K-notation columns to numeric
    def parse_k(s):
        if pd.isna(s):
            return 0
        s = str(s).strip().replace(",", "")
        if s.endswith("K"):
            return float(s[:-1]) * 1000
        try:
            return float(s)
        except ValueError:
            return 0

    for col in ["Times Listed", "Number of Reviews", "Plays", "Playing", "Backlogs", "Wishlist"]:
        games[col] = games[col].apply(parse_k)

    # Parse release year
    games["Year"] = pd.to_datetime(games["Release Date"], errors="coerce").dt.year

    # --- Clean vgsales.csv ---
    vgsales = vgsales.dropna(subset=["Year", "Publisher"])
    vgsales["Year"] = vgsales["Year"].astype(int)

    return games, vgsales

games, vgsales = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎮 Filters")
page = st.sidebar.radio(
    "Navigate to",
    ["🏠 Overview", "📊 Sales Analysis", "🕹️ Game Ratings", "🌍 Regional Breakdown"],
)
st.sidebar.markdown("---")

# Shared year range filter (vgsales)
year_min = int(vgsales["Year"].min())
year_max = int(vgsales["Year"].max())
year_range = st.sidebar.slider(
    "Sales Year Range", year_min, year_max, (2000, year_max)
)

# Genre filter (vgsales)
all_genres = sorted(vgsales["Genre"].dropna().unique())
selected_genres = st.sidebar.multiselect("Genres", all_genres, default=all_genres[:6])

vg_filtered = vgsales[
    (vgsales["Year"].between(*year_range)) &
    (vgsales["Genre"].isin(selected_genres if selected_genres else all_genres))
]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🎮 Video Game Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Explore game ratings, global sales trends, and regional performance.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 – Overview
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Games (Sales DB)", f"{len(vgsales):,}")
    c2.metric("🌐 Global Sales (M units)", f"{vgsales['Global_Sales'].sum():,.1f}")
    c3.metric("⭐ Avg Rating (Backloggd)", f"{games['Rating'].mean():.2f}")
    c4.metric("🕹️ Games Reviewed", f"{len(games):,}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Best-Selling Games")
        top10 = vgsales.nlargest(10, "Global_Sales")[["Name", "Platform", "Global_Sales"]]
        fig = px.bar(
            top10.sort_values("Global_Sales"),
            x="Global_Sales",
            y="Name",
            orientation="h",
            color="Global_Sales",
            color_continuous_scale="Purples",
            labels={"Global_Sales": "Global Sales (M)", "Name": ""},
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sales by Genre")
        genre_sales = vg_filtered.groupby("Genre")["Global_Sales"].sum().reset_index()
        fig = px.pie(
            genre_sales,
            names="Genre",
            values="Global_Sales",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Plasma_r,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Annual Global Sales Trend")
    annual = vg_filtered.groupby("Year")["Global_Sales"].sum().reset_index()
    fig = px.area(
        annual,
        x="Year",
        y="Global_Sales",
        labels={"Global_Sales": "Global Sales (M)"},
        color_discrete_sequence=["#6C63FF"],
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 – Sales Analysis
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Sales Analysis":
    st.subheader("Sales Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 15 Publishers by Global Sales")
        pub_sales = (
            vg_filtered.groupby("Publisher")["Global_Sales"]
            .sum()
            .nlargest(15)
            .reset_index()
        )
        fig = px.bar(
            pub_sales.sort_values("Global_Sales"),
            x="Global_Sales",
            y="Publisher",
            orientation="h",
            color="Global_Sales",
            color_continuous_scale="Teal",
            labels={"Global_Sales": "Global Sales (M)", "Publisher": ""},
        )
        fig.update_layout(coloraxis_showscale=False, height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Genre Sales Over Time")
        g_year = (
            vg_filtered.groupby(["Year", "Genre"])["Global_Sales"]
            .sum()
            .reset_index()
        )
        fig = px.line(
            g_year,
            x="Year",
            y="Global_Sales",
            color="Genre",
            labels={"Global_Sales": "Sales (M)"},
        )
        fig.update_layout(height=420, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Platform Market Share (Filtered Period)")
    plat_sales = (
        vg_filtered.groupby("Platform")["Global_Sales"]
        .sum()
        .nlargest(12)
        .reset_index()
    )
    fig = px.treemap(
        plat_sales,
        path=["Platform"],
        values="Global_Sales",
        color="Global_Sales",
        color_continuous_scale="RdBu",
        title="",
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 – Game Ratings  (games.csv)
# ════════════════════════════════════════════════════════════════════════════
elif page == "🕹️ Game Ratings":
    st.subheader("Game Ratings & Popularity (Backloggd)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Rating Distribution")
        fig = px.histogram(
            games.dropna(subset=["Rating"]),
            x="Rating",
            nbins=30,
            color_discrete_sequence=["#FF6584"],
        )
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Top 15 Most Played Games")
        top_played = games.nlargest(15, "Plays")[["Title", "Plays", "Rating"]]
        fig = px.bar(
            top_played.sort_values("Plays"),
            x="Plays",
            y="Title",
            orientation="h",
            color="Rating",
            color_continuous_scale="Viridis",
            labels={"Plays": "Total Plays", "Title": ""},
        )
        fig.update_layout(coloraxis_showscale=True, height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Rating vs Wishlist Size")
    fig = px.scatter(
        games.dropna(subset=["Rating"]),
        x="Rating",
        y="Wishlist",
        size="Plays",
        color="Rating",
        hover_name="Title",
        color_continuous_scale="Plasma",
        labels={"Wishlist": "Wishlist Count"},
        opacity=0.7,
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Browse Games")
    min_r, max_r = st.slider("Filter by Rating", 0.0, 5.0, (3.5, 5.0), step=0.1)
    filtered_g = games[(games["Rating"] >= min_r) & (games["Rating"] <= max_r)].copy()
    st.dataframe(
        filtered_g[["Title", "Rating", "Plays", "Backlogs", "Wishlist", "Genres", "Release Date"]]
        .sort_values("Rating", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=350,
    )


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 – Regional Breakdown
# ════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Regional Breakdown":
    st.subheader("Regional Sales Breakdown")

    regions = {"NA": "NA_Sales", "EU": "EU_Sales", "JP": "JP_Sales", "Other": "Other_Sales"}

    total_regional = {r: vg_filtered[c].sum() for r, c in regions.items()}
    c1, c2, c3, c4 = st.columns(4)
    for col, (region, val) in zip([c1, c2, c3, c4], total_regional.items()):
        col.metric(f"{region} Sales (M)", f"{val:,.1f}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Regional Share (Filtered)")
        fig = px.pie(
            names=list(total_regional.keys()),
            values=list(total_regional.values()),
            hole=0.4,
            color_discrete_sequence=["#6C63FF", "#FF6584", "#43C59E", "#FFB347"],
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Regional Trend Over Years")
        reg_year = (
            vg_filtered.groupby("Year")[list(regions.values())]
            .sum()
            .reset_index()
            .melt(id_vars="Year", var_name="Region", value_name="Sales")
        )
        reg_year["Region"] = reg_year["Region"].str.replace("_Sales", "")
        fig = px.line(
            reg_year,
            x="Year",
            y="Sales",
            color="Region",
            labels={"Sales": "Sales (M)"},
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Genre Performance by Region")
    genre_region = (
        vg_filtered.groupby("Genre")[list(regions.values())]
        .sum()
        .reset_index()
        .melt(id_vars="Genre", var_name="Region", value_name="Sales")
    )
    genre_region["Region"] = genre_region["Region"].str.replace("_Sales", "")
    fig = px.bar(
        genre_region,
        x="Genre",
        y="Sales",
        color="Region",
        barmode="group",
        color_discrete_sequence=["#6C63FF", "#FF6584", "#43C59E", "#FFB347"],
        labels={"Sales": "Sales (M)"},
    )
    fig.update_layout(height=400, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sources: Backloggd (games.csv) · VGChartz (vgsales.csv) · Built with Streamlit & Plotly")
