from pystac_client import Client
import planetary_computer as pc
import streamlit as st


@st.cache_data(show_spinner=False)
def search_sentinel(aoi_geojson, start_date, end_date, cloud_cover):
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace,
    )

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=aoi_geojson,
        datetime=f"{start_date}/{end_date}",
        query={"eo:cloud_cover": {"lt": cloud_cover}},
        max_items=5,
    )

    items = list(search.get_items())

    if not items:
        return None

    items.sort(key=lambda i: i.properties.get("eo:cloud_cover", 100))
    return items[0]
