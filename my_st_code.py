import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px


DATA_PATH = Path("data")
df = pd.read_pickle(DATA_PATH / "certif_one_gem_for_streamlit.pkl")

# preprocessing
df = df[df.carat >= 1].copy()
carat_df = df.copy().set_index("StartDate")
carat_df["price_per_ct"] = carat_df.PriceRealised / carat_df.carat

st.title("My auction house")

# Create a navigation menu
# page = st.sidebar.selectbox("Select a page", ["Diamonds", "Colored gemstones", "My biggest sales"])
is_market, is_diamond, is_gems, is_big_sales = st.tabs(
    ["Overall market", "Diamonds", "Colored gemstones", "My biggest sales"]
)

with is_diamond:

    diamond_df = carat_df[carat_df.gemstone == "diamond"].copy()

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
    bar_over_time = px.bar(
        diamond_df.resample("1M")["PriceRealised"].sum(),
        y="PriceRealised",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    st.plotly_chart(bar_over_time, use_container_width=True)

    st.markdown(
        """
    ### Clarity analysis
    """
    )
    clarity_grouped = (
        diamond_df.groupby("clarity")
        .agg(
            counted=("clarity", "count"),
            valued=("PriceRealised", "sum"),
            mean_price_per_carat=("price_per_ct", "mean"),
        )
        .reset_index()
    )

    clarity_pie = px.pie(
        clarity_grouped,
        values="counted",
        names="clarity",
        title="Diamond Clarity Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    st.plotly_chart(clarity_pie, use_container_width=True)

    bar_price_clarity = px.bar(
        clarity_grouped.sort_values(by="mean_price_per_carat", ascending=False),
        x="clarity",
        y="mean_price_per_carat",
        color="counted",
        color_continuous_scale=px.colors.sequential.RdBu_r,
    )

    bar_price_clarity.update_layout(
        title="Price of the different clarities",
        yaxis=dict(title="Average €/carat"),
        showlegend=False,
    )
    bar_price_clarity.update_coloraxes(showscale=False)

    st.plotly_chart(bar_price_clarity, use_container_width=True)

with is_gems:
    # do_monthly_balance(USERNAME)
    pass

with is_big_sales:

    # do_altair_overall(USERNAME)
    # plot_current_month(USERNAME)
    pass
