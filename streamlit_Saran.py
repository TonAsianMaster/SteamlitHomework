import streamlit as st
import pandas as pd
import numpy as np
import folium as fo
import geopandas as gp
import altair as alt
import pydeck as pdk
from streamlit_folium import folium_static


st.title("Intelligent Traffic Information Center (iTIC) ")
st.markdown("Homework streamlit Saran Suaysukwicha 6030801021 ")
st.markdown("Please select date at sidebar on leftside.")

#เลือกข้อมูลตามวันที่ที่จะใช้
select_date = st.sidebar.selectbox('Date :' , ['1 January 2019','2 January 2019','3 January 2019','4 January 2019','5 January 2019'])
if select_date=="1 January 2019":
    DATA_URL = ("https://raw.githubusercontent.com/TonAsianMaster/SteamlitHomework/master/Data/20190101.csv")
elif select_date=="2 January 2019":
    DATA_URL = ("https://raw.githubusercontent.com/TonAsianMaster/SteamlitHomework/master/Data/20190102.csv")
elif select_date=="3 January 2019":
    DATA_URL = ("https://raw.githubusercontent.com/TonAsianMaster/SteamlitHomework/master/Data/20190103.csv")
elif select_date=="4 January 2019":
    DATA_URL = ("https://raw.githubusercontent.com/TonAsianMaster/SteamlitHomework/master/Data/20190104.csv")
elif select_date=="5 January 2019":
    DATA_URL = ("https://raw.githubusercontent.com/TonAsianMaster/SteamlitHomework/master/Data/20190105.csv")

# import data ด้วย URL ก่อนหน้า
DATE_TIME = "timestart" #ชื่อตรงกับหัว Column
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME],format='%d/%m/%Y %H:%M')
    return data
data = load_data(100000)

#create slidebar for raw data and Map
hour = st.slider("Hour to look at", 0, 23,0,3)  #start,stop,begin,step
data = data[data[DATE_TIME].dt.hour == hour]

#Show raw data
if st.checkbox("Show raw data", False):
    st.subheader("Raw data by hour at %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(data)
    # '## Raw data at %sh' % hour,data

#set geometry
crs = "EPSG:4326"  #wgs84
geometry = gp.points_from_xy(data.lonstartl,data.latstartl)
geo_df  = gp.GeoDataFrame(data,crs=crs,geometry=geometry)

#setup Map
st.subheader("Traffic map at %i:00" %hour)
longi = 100.523186
lati = 13.736717
station_map = fo.Map(
                location = [lati, longi], 
                zoom_start = 10)
#fo.Map(location=[lon,lat])

#เตรียม Plot สร้าง List ของ lat lon time จากข้อมูล CSV
latitudes = list(data.latstartl)
longitudes = list(data.lonstartl)
time = list(data.timestart)
labels = list(data.n)

#show location icon popup
for lat, lon,t, label in zip(latitudes, longitudes,time, labels):
    if data.timestart[label].hour==hour and data.timestart[label].year!=2018:
        fo.Marker(
          location = [lat, lon], 
          popup = [label,lat,lon,t],
          icon = fo.Icon(color="orange", icon="heart")
         ).add_to(station_map)
folium_static(station_map)

# Create geo data
st.subheader("Traffic flow data when %i:00" %hour)
midpoint = (np.average(data["latstartl"]), np.average(data["lonstartl"]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=["lonstartl", "latstartl"],
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1100],
            pickable=True,
            extruded=True,
        ),
    ],
))

#สร้างกราฟแท่งแบ่งตามนาที
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ), use_container_width=True)

st.markdown("Thank you for your attention.")
st.markdown("We hope to see you again soon.")

st.sidebar.markdown("Powered by department of Survey Engineering , Chulalongkorn University")
