import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from shapely.geometry import shape
import numpy as np
import pandas as pd
from datetime import date

from indices import INDICES
from stac_utils import search_sentinel
from raster_utils import read_band, compute_index
from visualization import plot_index_map, plot_histogram

# --------------------------------------------------
# KONFIGURACJA STRONY
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("🛰️ Sentinel-2 – analiza indeksów spektralnych")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
index_name = st.sidebar.selectbox("Indeks spektralny", list(INDICES.keys()))

start_date = st.sidebar.date_input(
    "Data początkowa",
    value=date(2024, 5, 1),
)

end_date = st.sidebar.date_input(
    "Data końcowa",
    value=date(2024, 8, 31),
)

cloud_cover = st.sidebar.slider(
    "Maksymalne zachmurzenie (%)",
    0, 100, 60, 5
)

# --------------------------------------------------
# MAPA – RYSOWANIE AOI
# --------------------------------------------------
base_map = folium.Map(
    location=[52, 19],
    zoom_start=6,
    tiles="OpenStreetMap",
)

Draw(export=True).add_to(base_map)

map_data = st_folium(base_map, height=500, width=900)

# --------------------------------------------------
# OBSŁUGA AOI
# --------------------------------------------------
if map_data and map_data.get("all_drawings"):
    geoms = [shape(f["geometry"]) for f in map_data["all_drawings"]]
    gdf = gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")

    # --- kontrola wielkości AOI ---
    gdf_metric = gdf.to_crs(epsg=3857)
    areas_km2 = gdf_metric.area / 1e6

    if any(areas_km2 > 100):
        st.error("❌ Jeden z poligonów przekracza 100 km²")
        st.stop()

    # --------------------------------------------------
    # ANALIZA
    # --------------------------------------------------
    if st.button("▶ Analizuj"):
        with st.spinner("🔍 Wyszukiwanie danych Sentinel-2..."):
            aoi_union = gdf.unary_union
            aoi_geojson = aoi_union.__geo_interface__

            item = search_sentinel(
                aoi_geojson,
                start_date,
                end_date,
                cloud_cover,
            )

            if item is None:
                st.warning("⚠️ Brak danych Sentinel-2 dla wybranego obszaru.")
                st.stop()

        # --------------------------------------------------
        # ODCZYT PASM
        # --------------------------------------------------
        bands = INDICES[index_name]

        try:
            band_num, ref_profile = read_band(
                item,
                bands["num"],
                gdf.geometry,
            )

            band_den, _ = read_band(
                item,
                bands["den"],
                gdf.geometry,
                reference_profile=ref_profile,
            )
        except ValueError:
            st.error("❌ AOI nie pokrywa się z rastrem Sentinel-2.")
            st.stop()

        index = compute_index(band_num, band_den)

        # --------------------------------------------------
        # MAPA INDEKSU
        # --------------------------------------------------
        st.subheader("🗺️ Mapa indeksu spektralnego")
        st.pyplot(
            plot_index_map(
                index,
                index_name,
                bands["cmap"],
                bands["legend"],
            )
        )

        # --------------------------------------------------
        # HISTOGRAM
        # --------------------------------------------------
        st.subheader("📈 Histogram wartości indeksu")
        st.pyplot(plot_histogram(index, index_name))

        # --------------------------------------------------
        # STATYSTYKI
        # --------------------------------------------------
        st.subheader("📋 Statystyki globalne")

        stats = {
            "mean": float(np.nanmean(index)),
            "min": float(np.nanmin(index)),
            "max": float(np.nanmax(index)),
            "std": float(np.nanstd(index)),
        }

        df = pd.DataFrame(stats.items(), columns=["metric", "value"])
        st.dataframe(df)

        st.download_button(
            "⬇ Pobierz CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{index_name}_stats.csv",
            mime="text/csv",
        )

else:
    st.info("✏️ Narysuj jeden lub więcej poligonów na mapie, aby rozpocząć analizę.")
