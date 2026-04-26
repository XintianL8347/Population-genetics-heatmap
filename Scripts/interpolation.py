import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf


# The "3D-RBF" algorithm
# It fills in the time bins where not enough individuals were present by prediction from other time bins.
# Fit a 3D rbf interpolation model to the whole dataset across time and locations
def create_3drbf(df):
    times = df["Mean date (BP)"].values
    lons = df["Long"].values
    lats = df["Lat"].values
    vals = df["Dist"].values

    rbf_3d = Rbf(lons, lats, times, vals, function="multiquadric", smooth=0.05)
    return rbf_3d


# The heatmap plotting function derived from multimap.plot_acient_bin()
def plot_viking_bin(fig, df_subset: pd.DataFrame, time_label: int, rbf_3d: Rbf, window: int) -> None:
    # Extract data for the subset within chosen time bin
    lons_sub = df_subset["Long"].values
    lats_sub = df_subset["Lat"].values
    vals_sub = df_subset["Dist"].values

    # Skip the time bin if too few data points are available
    if len(df_subset) < 3:
        print(f"  Skipping {time_label}: Too few data points.")
        return

    # Create a zoomed grid for the heatmap (slightly larger than the map zoom so no sharp edges shown)
    grid_lon, grid_lat = np.mgrid[-60:50:200j, 30:80:200j]

    # Use the "midpoint" in the time bin for rbf interpolation
    t_constant = time_label + 50
    # NOTE: all three arguments to the Rbf need to be arrays; convert time to an array of the same shape
    z_mesh = rbf_3d(grid_lon, grid_lat, np.full_like(grid_lon, t_constant))
    # Set >1 to 1 and <0 to 0 instead of cutting them away for a nicer visualization
    z_mesh = np.clip(z_mesh, 0, 1)

    # Set up the map and zoom scale
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-50, 40, 35, 74], crs=ccrs.PlateCarree())

    # Plot the Heatmap (slightly different from the other two algos due to different treatment to z_mesh)
    color_levels = np.linspace(0, 1, 51)
    heatmap = ax.contourf(grid_lon, grid_lat, z_mesh, levels=color_levels, cmap="jet", alpha=0.7, zorder=1)

    # Mask the ocean and add geographical details: SAME
    ax.add_feature(cfeature.LAND, facecolor="none", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="cornflowerblue", zorder=2)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.4, zorder=3)

    # Add the actual data points on top
    ax.scatter(
        lons_sub,
        lats_sub,
        c=vals_sub,
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
    # Add title and return that frame
    plt.title(f"Time Bin: {time_label} - {time_label + window}")
    return fig


# Function to update the frames in animation; NOTE: arguments differ
def update(t, fig, df, rbf_3d, window):
    fig.clear()
    subset = df[(df["Mean date (BP)"] >= (t - window)) & (t >= df["Mean date (BP)"])]
    plot_viking_bin(fig, subset, int(1950 - t), rbf_3d, window)
