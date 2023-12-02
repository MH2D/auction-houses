import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from diamond_dashboard import main_diamond
from colored_gems_dashboard import map_gemstones
import geopandas as gpd

DATA_PATH = Path("data")
df = pd.read_pickle(DATA_PATH / "certified_one_gem_processed_data.pkl")
world_gdf = gpd.read_file(DATA_PATH / "gem_location/gem_location.shp")
# preprocessing
df = df[df.carat >= 1].copy()
carat_df = df.copy().set_index("StartDate")
carat_df["price_per_ct"] = carat_df.PriceRealised / carat_df.carat

st.title("My auction house")

# Create a navigation menu
# page = st.sidebar.selectbox("Select a page", ["Diamonds", "Colored gemstones", "My biggest sales"])
is_diamond, is_gems, is_big_sales = st.tabs(
    ["Diamonds", "Colored gemstones", "My biggest sales"]
)

with is_diamond:
    main_diamond(carat_df)

with is_gems:
    # do_monthly_balance(USERNAME)
    map_gemstones(carat_df, world_gdf)

with is_big_sales:

    # do_altair_overall(USERNAME)
    # plot_current_month(USERNAME)
    pass
