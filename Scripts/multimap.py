import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf


def aDNA_pre_process(df):
    # Collect all the genetic pool columns
    z_cols = [col for col in df.columns if col.startswith("Z_")]

    # Calculate the "baseline" (average Iceland Viking ref)
    ref_viking = df[df["CultureID"] == 1000][z_cols].mean()

    # Calculate Euclidean distance for every individual
    def cal_dist(row):
        return np.sqrt(np.sum((row[z_cols] - ref_viking) ** 2))

    df["Dist"] = df.apply(cal_dist, axis=1)
    return df


# The multi-heatmap plotting function
def plot_acient_bin(df_subset: pd.DataFrame, time_label: int):
    # Average the data points on the same location
    site_data = df_subset.groupby(["Lat", "Long"])["Dist"].mean().reset_index()

    # Extract arrays from dataframe
    lons = site_data["Long"].values
    lats = site_data["Lat"].values
    vals = site_data["Dist"].values

    # Ensure every Lat/Long has exactly one value
    assert lons.shape == lats.shape == vals.shape, f"Data mismatch! Lons:{lons.shape}, Lats:{lats.shape}, Vals:{vals.shape}"

    # Skip the time bin if too few data points are available (more than 3 datapoints are needed per timebin for 2d-rbf prediction)
    if len(site_data) < 3:
        return

    # Create a zoomed grid for the heatmap (slightly larger than the map zoom so no sharp edges shown)
    grid_lon, grid_lat = np.mgrid[-60:50:200j, 30:80:200j]

    # Calculate the "heat"
    # Fit a rbf interpolation to "predict" the uncovered locations
    rbf = Rbf(lons, lats, vals, function="multiquadric", smooth=0.1)
    z_mesh: np.ndarray = rbf(grid_lon, grid_lat)
    # Cut away the predictions that are greater than 1 or less than 0
    fil = z_mesh > 1
    z_mesh_fil = z_mesh.copy()
    z_mesh_fil[fil] = np.nan

    # Set the fig size, map, and zoom
    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-50, 40, 35, 74], crs=ccrs.PlateCarree())

    # Plot the Heatmap
    color_levels = np.linspace(0, 1, 51)
    heatmap = ax.contourf(
        grid_lon,
        grid_lat,
        z_mesh_fil,
        vmin=0,
        vmax=1,
        levels=color_levels,
        cmap="jet",
        alpha=0.7,
        zorder=1,
    )

    # Mask the ocean and add geographical details
    ax.add_feature(cfeature.LAND, facecolor="none", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="cornflowerblue", zorder=2)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.4, zorder=3)

    # Add the actual data points on top
    ax.scatter(
        lons,
        lats,
        c=vals,
        cmap="jet",
        edgecolors="black",
        s=40,
        zorder=4,
        vmin=0,
        vmax=1,
    )

    # Add the color bar indicating the gradient
    cbar = plt.colorbar(heatmap, orientation="horizontal", pad=0.05)
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])  # Keep the labels consistent
    cbar.set_label("Genetic Distance (0 = Identical to Iceland Viking)")
    # Add title, shrink margin, and return the map
    plt.title(f"Time bin: {time_label - 50} -  {time_label + 50}")
    plt.tight_layout()
    return fig
