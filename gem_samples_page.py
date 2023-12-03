import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from PIL import Image
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import numpy as np
from datetime import date

def reset_pages():
     st.session_state.pages = -1

def download_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content

    except Exception as e:
        st.write(f"Failed to download {url}. Error: {e}")
        return None


def get_random_sample(df, col, given_id=None):

    if given_id == None:
        row = df.sample().iloc[0]
    else:
        row = df[df.lot_id == given_id].iloc[0]

    # st.table(row)
    try:
        image_url = row.ImageURL
        img = Image.open(BytesIO(download_image(image_url)))
        # Get the dimensions of the image
        width, height = img.size

        # Determine the size of the square
        size = min(width, height)

        # Calculate the cropping box to keep the center of the image
        left = (width - size) // 2
        top = (height - size) // 2
        right = (width + size) // 2
        bottom = (height + size) // 2

        # Crop the image to the square
        img_cropped = img.crop((left, top, right, bottom))
        # Display the image using matplotlib.pyplot.imshow
        col.image(img_cropped, caption="", use_column_width="auto")
    except:
        col.markdown("No Image")

    # col1.metric("Gemstone", f"{row.gemstone}")
    title = row.Title
    if len(title) < 30:
        title = title + "\n"
    col.markdown(title.upper())
    col.markdown(f"{row.carat} carats")
    if np.isnan(row.PriceRealised):
        col.markdown("**Not sold**")
    else:
        col.markdown(f"**Hammer price** {row.PriceRealised:,.0f} €")
        col.markdown(f"**Price with fees** {row.price_with_fees:,.0f} €")
    col.markdown(f"**Estimation** {row.EstimateLow:,.0f} -  {row.EstimateHigh:,.0f} €")

    col.markdown(
        f"{row.certifier.upper()}, report no. {row.certif_id}: {row.description}"
    )

    # st.markdown("**The original gem URL**")
    # st.markdown(row.URL)


def plot_some_gems(df, number=5, num_cols=3):
    def increment_counter():
        st.session_state.pages += 1

    gemstone_sel = st.selectbox("Select gemstone", ["all"] + list(df.gemstone.unique()), on_change=reset_pages)
    date_range = st.date_input(
        "Select the period",
        (df.index.min(), df.index.max()),
        df.index.min(),
        df.index.max(),
        on_change=reset_pages
    )
    start_date, end_date = date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime(
        "%Y-%m-%d"
    )
    samples_df = df.loc[start_date:end_date]
    if gemstone_sel != "all":
        samples_df = samples_df[samples_df.gemstone == gemstone_sel]
    if st.button("Display the next 40 lots", on_click=increment_counter):
        to_plot = samples_df.iloc[
            st.session_state.pages * 30 : (st.session_state.pages + 1) * 30
        ].copy()
        num_rows = len(to_plot) // num_cols
        # Iterate over rows
        if num_rows == 0:
                st.warning('No lots to plot. Please change your selection.')
        for i in range(num_rows):
            # Create columns for each row
            cols = st.columns(num_cols)
            # Fill each column with content (e.g., text)
            if i * num_cols + num_cols  > len(to_plot):
                st.warning('No more lots to plot. Please change your selection.')
            else:
                for j, col in enumerate(cols):
                    get_random_sample(
                        to_plot, col, given_id=to_plot.iloc[i * num_cols + j].lot_id
                    )
                st.divider()
