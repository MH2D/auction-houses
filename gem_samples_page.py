import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from PIL import Image
import matplotlib.pyplot as plt
import requests
from io import BytesIO




def download_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content

    except Exception as e:
        st.write(f"Failed to download {url}. Error: {e}")
        return None


def get_random_sample(df, given_id=None):

    if given_id == None:
        row = df.sample().iloc[0]
    else:
        row = df[df.lot_id == given_id].iloc[0]
    st.markdown(f"## {row.Title}")
    # st.table(row)
    try:
        image_url = row.ImageURL
        img = Image.open(BytesIO(download_image(image_url)))
        # Display the image using matplotlib.pyplot.imshow
        st.image(img, caption="", width=400)
    except:
        st.markdown("No Image")

    col1, col2, col3 = st.columns(3)
    col1.metric("Gemstone", f"{row.gemstone}")
    col2.metric("Carat", f"{row.carat} carats")
    col3.metric(
        "Price Realised",
        f"{row.PriceRealised:,.0f} €",
        f"{row.PriceRealised - row.EstimateLow:,.0f} €",
        help="The value underneath is the difference with the expert's low estimation",
    )

    st.markdown(
        f"**Estimation window: {row.EstimateLow:,.0f} -  {row.EstimateHigh:,.0f} €**"
    )

    st.markdown("**The original gem URL**")
    st.markdown(row.URL)


def plot_some_gems(df, number=5):
    gemstone_sel = st.selectbox('Select gemstone', df.gemstone.unique())
    year_sel = st.selectbox('Select the year', sorted(df.index.year.unique()))
    engine_choice = st.selectbox('Select a price range', ['a', 'b', 'c'])

    if st.button('Display'):
        for idx, row in samples_df.iterrows():
            get_random_sample(df, given_id=row.lot_id)
            st.divider()