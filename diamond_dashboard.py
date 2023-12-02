import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px


def main_diamond(carat_df):
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
    all_years = diamond_df.index.year.unique()

    values = st.slider(
        "Select the time you want to display",
        all_years.min(),
        all_years.max(),
        (all_years.min(), all_years.max()),
    )

    bar_over_time = px.bar(
        diamond_df.loc[str(values[0]) : str(values[1])]
        .resample("1M")["PriceRealised"]
        .sum(),
        y="PriceRealised",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    bar_over_time.update_layout(dragmode=False)
    st.plotly_chart(bar_over_time, use_container_width=True)

    st.markdown(
        """
    ### Clarity analysis
    This section purpose is to better understand the sales with regard to the clarity of the diamonds.
    """
    )
    clarity_grouped = (
        diamond_df.groupby("clarity")
        .agg(
            counted=("clarity", "count"),
            valued=("PriceRealised", "sum"),
            mean_price_per_carat=("price_per_ct", "mean"),
            average_carat=("carat", "mean"),
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

    left_column, right_column = st.columns([0.3, 0.9])
    # Display tick variables in the left column
    with left_column:
        st.markdown('#### Select the variable to plot')
        tick_variables = {
            "total price realised (EUR)": "valued",
            "Average (EUR/carat)": "mean_price_per_carat",
            "Average size (carat)": "average_carat",
        }
        selected_variable = st.radio("", tick_variables.keys())

    # Display the plot in the right column
    with right_column:
        bar_price_clarity = px.bar(
            clarity_grouped.sort_values(by=tick_variables[selected_variable], ascending=False),
            x="clarity",
            y=tick_variables[selected_variable],
            color="counted",
            color_continuous_scale=px.colors.sequential.RdBu_r,
        )

        bar_price_clarity.update_layout(
            title=selected_variable,
            yaxis=dict(title="Average €/carat"),
            showlegend=False,
        )

        bar_price_clarity.update_coloraxes(showscale=False)
        bar_price_clarity.update_layout(dragmode=False)
        st.plotly_chart(bar_price_clarity, use_container_width=True)


    st.markdown(
        """
    ### Color analysis
    """
    )