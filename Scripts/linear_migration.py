import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf


# The "Linear Migration" algorithm
# It assumes active migration: old individuals will be discarded once new individuals with the same CultureID are founded in the new time bin
# A variation of the heatmap plotting function
def plot_viking_bin(fig, df_subset: pd.DataFrame, time_label: int, window: int, latest_world_state: dict):
    # Capture all the CultureIDs in current time bin
    culture_group = df_subset.groupby("CultureID")
    for id, group in culture_group:
        # latest_world_state is a global dict; replace the old info for that population/cultural group if it already exist otherwise add it
        latest_world_state[id] = group[["Lat", "Long", "Dist"]]
    # Make sure the dict if not empty; Extract the lat, long, dist
    if latest_world_state:
        current_bin_df = pd.concat(latest_world_state.values(), ignore_index=True)

    # Average the genetic distances on the same location
    site_data = current_bin_df.groupby(["Lat", "Long"])["Dist"].mean().reset_index()
    # Extract the values again
    lons = site_data["Long"].values
    lats = site_data["Lat"].values
    vals = site_data["Dist"].values

    # Ensure every Lat/Long has exactly one value
    assert lons.shape == lats.shape == vals.shape, f"Data mismatch! Lons:{lons.shape}, Lats:{lats.shape}, Vals:{vals.shape}"
    # Skip the time bin if too few data points are available
    if len(current_bin_df) < 3:
        print(f"  Skipping {time_label}: Too few data points.")
        return

    # The following are the same as in site_turnover.py
    grid_lon, grid_lat = np.mgrid[-60:50:200j, 30:80:200j]

    rbf = Rbf(lons, lats, vals, function="multiquadric", smooth=0.1)
    z_mesh: np.ndarray = rbf(grid_lon, grid_lat)
    fil = z_mesh > 1
    z_mesh_fil = z_mesh.copy()
    z_mesh_fil[fil] = np.nan

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-50, 40, 35, 74], crs=ccrs.PlateCarree())

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

    ax.add_feature(cfeature.LAND, facecolor="none", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="cornflowerblue", zorder=2)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.4, zorder=3)

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

    cbar = plt.colorbar(heatmap, orientation="horizontal", pad=0.05)
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cbar.set_label("Genetic Distance (0 = Identical to Iceland Viking)")
    plt.title(f"Time Bin: {time_label} - {time_label + window}")
    return fig


# Function to update the frames in animation
def update(t, fig, df, window, latest_world_state):
    fig.clear()  # Clear the old map
    # Extract data within the customized window size
    subset = df[(df["Mean date (BP)"] >= (t - window)) & (t >= df["Mean date (BP)"])]
    # Call the plotting function for each update
    plot_viking_bin(fig, subset, int(1950 - t), window, latest_world_state)
