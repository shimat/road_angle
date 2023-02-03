import geopandas as gpd
from matplotlib.axes import Axes
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, mapping, LineString
import time


@st.experimental_memo
def load_gdf(path: str) -> pd.DataFrame:
    return gpd.read_file(path, encoding="shift-jis")


st.title("Road")

# gdf = gpd.read_file("data/N01-07L-01-01.0a_GML/N01-07L-2K-01_Road.shp")
start_time = time.perf_counter()
gdf = load_gdf("data/sapporoauthorizedroad202111/路線区間オープンデータ.shp")
# gdf
print(f"{time.perf_counter() - start_time}s")

f = plt.figure(figsize=(6, 6))
a: Axes = f.gca()
for i in range(len(gdf)):
    a.plot(*gdf.iloc[i]["geometry"].xy)

st.pyplot(f)
