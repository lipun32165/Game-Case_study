# 🎮 Video Game Analytics Dashboard

An interactive dashboard built with **Streamlit** and **Plotly** to explore video game ratings, global sales trends, and regional performance.

## 📊 Features

| Page | What you'll find |
|---|---|
| 🏠 Overview | KPI cards, top-selling games, genre pie, annual trend |
| 📊 Sales Analysis | Publisher rankings, genre-over-time lines, platform treemap |
| 🕹️ Game Ratings | Rating histogram, most-played games, scatter explorer, filterable table |
| 🌍 Regional Breakdown | NA / EU / JP / Other metrics, regional trend lines, genre-by-region bars |

## 🗂️ Project Structure

```
vgdashboard/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Theme & server configuration
└── data/
    ├── games.csv           # Backloggd game ratings dataset
    └── vgsales.csv         # VGChartz global sales dataset
```

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create & activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501** by default.

## ☁️ Deploy to Streamlit Community Cloud (free)

1. Push this repository to GitHub (make sure `data/` folder is committed).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Deploy** — it will install requirements and launch automatically.

> ⚠️ Keep both CSV files inside `data/` when you push to GitHub. Streamlit Cloud reads them from the repo.

## 🛠️ Dependencies

- [Streamlit](https://streamlit.io/) `1.35`
- [Pandas](https://pandas.pydata.org/) `2.2`
- [Plotly](https://plotly.com/python/) `5.22`
