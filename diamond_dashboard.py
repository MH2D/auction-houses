import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from PIL import Image
import matplotlib.pyplot as plt
import requests
from io import BytesIO


def plot_over_time_diamond(diamond_df):
    all_years = sorted(diamond_df.index.year.unique())
    # Use st.beta_container to create a horizontal layout

    # Sample list of options
    selected_years = {one_year: False for one_year in all_years}
    selected_years[2023] = True
    # Create a row of checkboxes
    # year_col = st.columns([1/len(all_years) for _ in range(len(all_years))])
    year_col = st.columns(len(all_years))
    for idx, elt in enumerate(iter(year_col)):
        with elt:
            if idx < len(all_years) - 1:
                selected_years[all_years[idx]] = st.checkbox(str(all_years[idx]))
            else:
                selected_years[all_years[idx]] = st.checkbox(
                    str(all_years[idx]), value=True
                )
    over_time_price_df = (diamond_df
        .groupby(pd.Grouper(freq='1M'))[["PriceRealised", "certifier"]]
        .agg({"PriceRealised": "sum", "certifier": "count"})
        .rename(columns={"certifier": "Number of lot"})
        .dropna()
        .copy()
    )
    over_time_price_df = over_time_price_df[
            over_time_price_df.index.year.isin(
                [year for year, booli in selected_years.items() if booli == True]
            )
        ].copy()
    # Extract month names and years from the index
    over_time_price_df["Month"] = over_time_price_df.index.month_name()
    over_time_price_df["Year"] = over_time_price_df.index.year.astype(str)

    # Specify the order of months
    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    price_over_time = px.bar(
        over_time_price_df,
        x="Month",
        y="PriceRealised",
        color="Year",
        barmode="group",
        # text='Number of lot',
        # color_discrete_sequence=px.colors.sequential.Oranges,
        category_orders={"Month": month_order},
    )
    price_over_time.update_layout(dragmode=False)
    st.plotly_chart(price_over_time, use_container_width=True)

    count_over_time = px.bar(
        over_time_price_df,
        x="Month",
        y="Number of lot",
        color="Year",
        barmode="group",
        # color_discrete_sequence=px.colors.sequential.Oranges,
        category_orders={"Month": month_order},
    )
    
    count_over_time.update_layout(dragmode=False)
    st.plotly_chart(count_over_time, use_container_width=True)

    # bar_over_time.update_xaxes(
    #     tickmode="array",
    #     tickvals=list(range(1, 13)),  # Tick values for each month
    #     ticktext=month_order,  # Tick labels for each month
    # )


def plots_clarity(diamond_df):
    clarity_order = [
        "if",
        "fl",
        "vvs1",
        "vvs2",
        "vs1",
        "vs2",
        "si1",
        "si2",
        "i1",
        "i2",
        "i3",
    ]

    clarity_grouped = (
        diamond_df.groupby("clarity")
        .agg(
            counted=("clarity", "count"),
            valued=("PriceRealised", "sum"),
            mean_price_per_carat=("price_per_ct", "mean"),
            average_carat=("carat", "mean"),
        )
        .reindex(clarity_order)
        .reset_index()
    )

    clarity_pie = px.pie(
        clarity_grouped,
        values="counted",
        names="clarity",
        title="Diamond Clarity Distribution",
        color=px.colors.sequential.RdBu_r,
        category_orders={"clarity": clarity_order},
    )
    st.plotly_chart(clarity_pie, use_container_width=True)

    left_column, right_column = st.columns([0.3, 0.9])
    # Display tick variables in the left column
    with left_column:
        st.markdown("#### Select the variable to plot")
        tick_variables = {
            "total price realised (EUR)": "valued",
            "Average (EUR/carat)": "mean_price_per_carat",
            "Average size (carat)": "average_carat",
        }
        selected_variable = st.radio("", tick_variables.keys())

    # Display the plot in the right column
    with right_column:
        clarity_grouped_sorted = (
            clarity_grouped.set_index("clarity").reindex(clarity_order).reset_index()
        )
        bar_price_clarity = px.bar(
            clarity_grouped_sorted,
            x="clarity",
            y=tick_variables[selected_variable],
            # color="counted",
            color_continuous_scale=px.colors.sequential.RdBu_r,
            category_orders={"clarity": clarity_order},
        )

        bar_price_clarity.update_layout(
            title=selected_variable,
            yaxis=dict(title=selected_variable),
            showlegend=False,
        )

        bar_price_clarity.update_coloraxes(showscale=False)
        bar_price_clarity.update_layout(dragmode=False)
        st.plotly_chart(bar_price_clarity, use_container_width=True)


def download_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content

    except Exception as e:
        st.write(f"Failed to download {url}. Error: {e}")
        return None


def get_sample_lot(df, given_id=None):

    if given_id == None:
        row = df.sample().iloc[0]
    else:
        row = df[df.lot_id == given_id].iloc[0]
    st.markdown(f"**Title: {row.Title}**")
    # st.table(row)
    try:
        image_url = row.ImageURL
        img = Image.open(BytesIO(download_image(image_url)))
        # Display the image using matplotlib.pyplot.imshow
        st.image(img, caption="", width=400)
    except:
        st.markdown("No Image")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Price Realised",
        f"{row.PriceRealised:,.0f} €",
        f"{row.PriceRealised - row.EstimateLow:,.0f} €",
        help="The value underneath is the difference with the expert's low estimation",
    )
    col2.metric("Carat", f"{row.carat} carats")
    col3.metric("Clarity", f"{row.clarity}")

    st.markdown("**Description**")
    st.markdown(
        f"**Estimation window: {row.EstimateLow:,.0f} -  {row.EstimateHigh:,.0f} €**"
    )

    st.markdown(row.Description)
    st.markdown("**The original gem URL**")
    st.markdown(row.URL)


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
    plot_over_time_diamond(diamond_df)

    st.markdown(
        """
    ### Clarity analysis
    This section purpose is to better understand the sales with regard to the clarity of the diamonds.
    """
    )
    plots_clarity(diamond_df)

    st.markdown(
        """
        ### Get some data examples
        """
    )

    if st.button("Plot a data example"):
        get_sample_lot(diamond_df)
