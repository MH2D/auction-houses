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
    st.session_state.pages = 0
    st.session_state.displayed_elements = pd.DataFrame()

def download_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content

    except Exception as e:
        st.write(f"Failed to download {url}. Error: {e}")
        return None

def get_random_sample(_df, _col, _given_id=None):
    if _given_id == None:
        row = _df.sample().iloc[0]
    else:
        row = _df[_df.lot_id == _given_id].iloc[0]

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
        _col.image(img_cropped, caption="", use_column_width="auto")
    except:
        _col.markdown("No Image")


    _col.markdown(f"[{row.Title.upper()}]({row.URL})")
    _col.markdown(f"**{row.carat} carats**")
    if np.isnan(row.PriceRealised):
        _col.markdown("**Not sold**")
    else:
        _col.markdown(f'''
        **Hammer price** {row.PriceRealised:,.0f} €
        '''
        )

        _col.markdown(f'''**{row.price_per_ct:,.0f} €/carats**''')
        _col.markdown(f"**Price with fees** {row.price_with_fees:,.0f} €")
        
    _col.markdown(f"**Estimation** {row.EstimateLow:,.0f} -  {row.EstimateHigh:,.0f} €")

    _col.markdown(
        f"{row.certifier.upper()}, report no. {row.certif_id}: {row.description}"
    )

    # st.markdown("**The original gem URL**")
    # st.markdown(row.URL)


def filter_return_df(df):
    gemstone_sel = st.selectbox(
        "Select gemstone", ["all"] + list(df.gemstone.unique()), on_change=reset_pages
    )
    year_sel = st.selectbox(
        "Select the year",
        ["all time"] + sorted(df.index.year.unique()),
        on_change=reset_pages,
    )

    if gemstone_sel == "diamond":
        clarity_sel = st.selectbox(
            "Select clarity", ["all"] + list(df.clarity.unique()), on_change=reset_pages
        )
        color_sel = st.selectbox(
            "Select color", ["all"] + list(df.color.unique()), on_change=reset_pages
        )
    else:
        clarity_sel = "all"
        color_sel = "all"

    sort_method = {
        "price per carat": "price_per_ct",
        "Price": "PriceRealised",
        "Carat": "carat",
    }

    sort_keys = list(sort_method.keys())
    sort_col = st.columns(len(sort_keys))
    we_sort = {sort_ty: False for sort_ty in sort_keys}

    for idx, elt in enumerate(iter(sort_col)):
        with elt:
            we_sort[sort_keys[idx]] = st.checkbox(
                str(sort_keys[idx]), on_change=reset_pages
            )

    samples_df = df.copy()
    if gemstone_sel != "all":
        samples_df = samples_df[samples_df.gemstone == gemstone_sel]

    if clarity_sel != "all":
        samples_df = samples_df[samples_df.clarity == clarity_sel]

    if year_sel != "all time":
        samples_df = samples_df.loc[str(year_sel)]

    if color_sel != "all":
        samples_df = samples_df[samples_df.color == color_sel]

    samples_df = samples_df.sort_values(
        by=[col for name, col in sort_method.items() if we_sort[name] == True],
        ascending=False,
    )

    return samples_df


def get_next_elements(samples_df, current_page, cols_in_page, row_per_pages):
    # Replace this with your logic to fetch the next elements
    next_elements = samples_df.iloc[
        current_page
        * (cols_in_page * row_per_pages) : (current_page + 1)
        * (cols_in_page * row_per_pages)
    ].copy()
    return next_elements


def plot_some_gems(df, number=5, cols_in_page=3, row_per_pages=5):
    def increment_counter():
        st.session_state.pages += 1

    samples_df = filter_return_df(df)

    # Initialize or get the displayed elements list
    displayed_elements = st.session_state.get("displayed_elements", pd.DataFrame())

    # Fetch the next elements
    next_elements = get_next_elements(
        samples_df, st.session_state.pages, cols_in_page, row_per_pages
    )

    st.write("Current Elements:")
    combined_elements = pd.concat([displayed_elements, next_elements])
    num_rows = len(combined_elements) // cols_in_page
    for i in range(num_rows):
        # Create columns for each row
        cols = st.columns(cols_in_page)
        for j, col in enumerate(cols):
            get_random_sample(
                combined_elements,
                col,
                _given_id=combined_elements.iloc[i * cols_in_page + j].lot_id,
            )
        st.divider()

    # Button to show more elements
    if st.button("Show more"):
        # Update the current index for the next batch
        st.session_state.pages += 1

        # Update the displayed elements list
        st.session_state["displayed_elements"] = combined_elements

        # Trigger a rerun of the script to display the next batch
        st.experimental_rerun()

