import rasterio
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio.warp import reproject
import numpy as np
import geopandas as gpd


def read_band(item, band_name, geometries, reference_profile=None):
    asset = item.assets[band_name]
    href = asset.href

    gdf = gpd.GeoDataFrame(geometry=geometries, crs="EPSG:4326")

    with rasterio.open(href) as src:
        # --- AOI → CRS rastra ---
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)

        shapes = [geom.__geo_interface__ for geom in gdf.geometry]

        # 🔑 mask BEZ nan
        out_image, out_transform = mask(
            src,
            shapes,
            crop=True,
            filled=True,
            nodata=src.nodata,  # ← ważne
        )

        band = out_image[0].astype("float32")

        # 🔑 nodata → nan
        if src.nodata is not None:
            band[band == src.nodata] = np.nan

        profile = src.profile.copy()
        profile.update(
            height=band.shape[0],
            width=band.shape[1],
            transform=out_transform,
            dtype="float32",
        )

        # --- RESAMPLING DO REFERENCJI ---
        if reference_profile is not None:
            resampled = np.empty(
                (reference_profile["height"], reference_profile["width"]),
                dtype="float32",
            )

            reproject(
                source=band,
                destination=resampled,
                src_transform=profile["transform"],
                src_crs=profile["crs"],
                dst_transform=reference_profile["transform"],
                dst_crs=reference_profile["crs"],
                resampling=Resampling.bilinear,
            )

            return resampled, reference_profile

        return band, profile


def compute_index(band_num, band_den):
    np.seterr(divide="ignore", invalid="ignore")
    return (band_num - band_den) / (band_num + band_den)
