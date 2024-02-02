import math
import geopandas as gpd
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck
from matplotlib.axes import Axes
from pyproj import Transformer
from shapely.geometry import Polygon, mapping, LineString


@st.cache_data
def load_gdf(path: str) -> pd.DataFrame:
    return gpd.read_file(path, encoding="shift-jis")


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


# p1 = (0, 0)
# p2 = (1, 1)
# st.write(angle(p1, p2))


def calc_color(p: tuple[tuple[float, float], tuple[float, float]]) -> tuple[int, int, int]:
    TARGET_ANGLE = 15

    deg = angle(*p)
    if deg < 0:
        deg += 180
    diff = abs(TARGET_ANGLE - deg)
    if diff > 90:
        diff = 180 - diff
    if diff < 10:
        return (255, 0, 0)
    else:
        return (128, 128, 128)
    #d = diff / 90
    r = 255 / (1 + math.exp(0.9 * (45 - diff)))
    #st.write(r, diff)
    # st.write(f"{p1=}, {p2=}, {rad=}, {deg=}")
    return (255, r, r)


st.set_page_config(page_title="Road Angle", layout="wide")
st.title("Road Angle")

# gdf = gpd.read_file("data/N01-07L-01-01.0a_GML/N01-07L-2K-01_Road.shp")
gdf = load_gdf("data/sapporoauthorizedroad202111/路線区間オープンデータ.shp")
# gdf = gdf[:1000]

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

deck = pydeck.Deck(
    layers=(layer, ),
    initial_view_state=pydeck.ViewState(
        latitude=43.08,
        longitude=141.35,
        zoom=10.0,
        max_zoom=16,
        pitch=0,
        bearing=0,
        height=800, 
        width=1200),
    tooltip={"text": "{路線名}"})
st.pydeck_chart(deck)
deck.to_html("path_layer.html")
