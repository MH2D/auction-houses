import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib
import numpy as np
from streamlit_folium import st_folium

def map_gemstones(carat_df, world_gdf):
    # Clean up and process the data
    df = carat_df.copy()
    df["location"] = df["location"].replace(
        {
            "ceylon": "ceylon",
            "ceylan": "ceylon",
            "siam": "thailand",
            "mozambi": "mozambique",
        }
    )

    name_mapping = {
        "colombia": "Colombia",
        "burma": "Myanmar",
        "tajikistan": "Tajikistan",
        "ceylon": "Sri Lanka",
        "madagascar": "Madagascar",
        "tanzania": "Tanzania",
        "ethiopia": "Ethiopia",
        "zambi": "Zambia",
        "kashmir": "Kashmir",  # Note: Kashmir might not be a country in the GeoDataFrame
        "thailand": "Thailand",
        "siam": "Thailand",  # Siam is an old name for Thailand
        "mozambi": "Mozambique",
        "malawi": "Malawi",
    }
    # Count occurrences of each location
    location_counts = df["location"].value_counts()
    df.location = df.location.map(name_mapping)
    # Count occurrences of each country
    country_counts = Counter(df["location"])

    world_gdf["color"] = world_gdf["NAME"].apply(lambda x: country_counts.get(x, 0))
    sub_world = world_gdf[world_gdf.color > 0][['NAME', 'color', 'geometry']].copy()

    colname = 'color'
    xmin, ymin, xmax, ymax = sub_world.total_bounds

    centroidx = np.mean([xmin, xmax])
    centroidy = np.mean([ymin, ymax])

    map1 = folium.Map(
        location=[centroidy, centroidx],
        tiles='cartodbpositron',
        zoom_start=2,
        width=900
    )

    cmap = matplotlib.cm.get_cmap('viridis')

    vmin = sub_world[colname].min()
    vmax = sub_world[colname].max()


    norm = matplotlib.colors.SymLogNorm(vmin=vmin, vmax=vmax, linthresh=0.1)

    def fetchHexFromValue(value):
        NormedValue = norm(value)
        RGBAValue = cmap(NormedValue)
        HEXValue = matplotlib.colors.to_hex(RGBAValue)
        return HEXValue


    for idx, r in sub_world.iterrows():

        lat = r["geometry"].centroid.y
        lon = r["geometry"].centroid.x
        # folium.Marker(location=[lat, lon],
        #             popup='idx:{0} <br> {1}: {2}'.format(idx,
        #                                                 colname, 
        #                                                 r[colname])
        # ).add_to(map1)

    sub_world.explore(colname, cmap="viridis", m=map1)

    st_folium(map1)