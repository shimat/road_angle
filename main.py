import geopandas as gpd
from matplotlib.axes import Axes
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, mapping, LineString
import pydeck
from pyproj import Transformer
import math


#@st.experimental_memo
def load_gdf(path: str) -> pd.DataFrame:
    return gpd.read_file(path, encoding="shift-jis", rows=100)


# https://stackoverflow.com/questions/62053253/how-to-split-a-linestring-to-segments
def segment(line_string: LineString):
    return list(map(tuple, zip(line_string[:-1], line_string[1:])))


def flatten(row: pd.Series):
    df1_data = {c: row[c] for c in ("路線番号", "路線名", "区コード")}
    df1 = pd.DataFrame([df1_data])
    df2 = pd.Series(segment(row["segment_lonlat"])).to_frame(name='segment_lonlat')
    df1['key'] = df2['key'] = 0
    return df1.merge(df2, how='outer').drop(columns='key')


def angle(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    rad = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    deg = math.degrees(rad)
    return deg


p1 = (0, 0)
p2 = (1, 1)
st.write(angle(p1, p2))


def calc_color(p: tuple[tuple[float, float], tuple[float, float]]) -> tuple[int, int, int]:
    deg = angle(*p)
    if deg < 0:
        deg += 180
    diff = abs(105 - deg)
    if diff > 90:
        diff = 180 - diff
    #d = diff / 90
    r = 255 / (1 + math.exp(0.9 * (45 - diff)))
    #st.write(r, diff)
    # st.write(f"{p1=}, {p2=}, {rad=}, {deg=}")
    return (255, r, r)


st.title("Road")

# gdf = gpd.read_file("data/N01-07L-01-01.0a_GML/N01-07L-2K-01_Road.shp")
gdf = load_gdf("data/sapporoauthorizedroad202111/路線区間オープンデータ.shp")

transformer = Transformer.from_proj(2454, 4326)
gdf["segment_lonlat"] = gdf["geometry"].apply(
    lambda p: tuple(transformer.transform(c[1], c[0])[::-1] for c in p.coords))
#gdf

gdf2 = pd.concat(gdf.apply(flatten, axis=1).values)
gdf2["color"] = gdf2["segment_lonlat"].apply(calc_color)

gdf2
#x, y = -72972.527, -92327.287
#lat, lon = transformer.transform(y, x)
#print(lon, lat)

#f = plt.figure(figsize=(6, 6))
#a: Axes = f.gca()
#for i in range(len(gdf)):
#    a.plot(*gdf.iloc[i]["geometry"].xy)
#st.pyplot(f)

DATA_URL = {
    "AIRPORTS": "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/line/airports.json",
    "FLIGHT_PATHS": "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/line/heathrow-flights.json",  # noqa
}


"""
line_layer = pydeck.Layer(
    "LineLayer",
    df,
    get_source_position="lat",
    get_target_position="lon",
    get_color=GET_COLOR_JS,
    get_width=10,
    highlight_color=[255, 255, 0],
    picking_radius=10,
    auto_highlight=True,
    pickable=True,
)
"""


layer = pydeck.Layer(
    type="PathLayer",
    data=gdf2,
    pickable=True,
    get_color="color",
    width_scale=4,
    width_min_pixels=1,
    get_path="segment_lonlat",
    get_width=5,
)

st.pydeck_chart(
    pydeck.Deck(
        layers=(layer, ),
        initial_view_state=pydeck.ViewState(
            latitude=43.08,
            longitude=141.35,
            zoom=10.0,
            max_zoom=16,
            pitch=0,
            bearing=0)))
