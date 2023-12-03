import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from diamond_dashboard import (
    main_diamond,
    plot_over_time_diamond,
    plots_clarity,
    get_sample_lot,
)
from colored_gems_dashboard import map_gemstones
import geopandas as gpd

DATA_PATH = Path("data")
df = pd.read_pickle(DATA_PATH / "certified_one_gem_processed_data.pkl")
df["clarity"] = df.clarity.str.replace(" ", "")
world_gdf = gpd.read_file(DATA_PATH / "gem_location/gem_location.shp")
# preprocessing
df = df[df.carat >= 1].copy()
carat_df = df.copy().set_index("StartDate")
carat_df["price_per_ct"] = carat_df.PriceRealised / carat_df.carat

st.title("My auction house")

# Create a navigation menu
page = st.sidebar.selectbox(
    "Select a page",
    [
        "Gems examples",
        "Diamonds",
        "Colored gemstones",
        "My biggest sales",
    ],
)

if page == "Gems examples":
    pass

if page == "Diamonds":
    over_time, clarity_analysis, color_analysis, visual_checks = st.tabs(
        [
            "Sales over time",
            "Clarity analysis",
            "Color analysis",
            "Check some diamonds sales",
        ]
    )
    diamond_df = carat_df[carat_df.gemstone == "diamond"].copy()

    with over_time:
        st.markdown(
            f"""
        ## Main information
        Total number of diamonds analysed: **{len(diamond_df):,.0f}**

        Total valued sold: **{diamond_df.PriceRealised.sum():,.0f} €**
        """
        )

        st.markdown(
            """
        ### Diamonds sales over time
        """
        )
        bar_over_time = plot_over_time_diamond(diamond_df)
        st.plotly_chart(bar_over_time, use_container_width=True)

    with clarity_analysis:
        st.markdown(
            """
        ### Clarity analysis
        This section purpose is to better understand the sales with regard to the clarity of the diamonds.
        """
        )
        plots_clarity(diamond_df)

    with visual_checks:
        st.markdown(
            """
            ### Get some data examples
            """
        )

        if st.button("Plot a data example"):
            get_sample_lot(diamond_df)


if page == "Colored gemstones":
    # do_monthly_balance(USERNAME)
    map_gemstones(carat_df, world_gdf)
