import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf


# The "Site Turnover" algorithm
# It assumes that individuals remain at the same location after their time bin, until a new individual enters and covers the exact same location.
# The heatmap plotting function derived from multimap.plot_acient_bin()
def plot_viking_bin(fig, df_subset: pd.DataFrame, time_label: int, window: int, latest_world_state: dict):
    # Create a set of site (location) ids for each iteration. Purpose: to allow multiple individuals at the same site within the same timebin
    # NOTE: updated_this_frame is local to each frame, differing from latest_world_state which is global
    updated_this_frame = set()

    # Store the most recent {Site_ID: [Lat, Long, Distance]}
    # Each Site_ID represent a uniq location
    for _, row in df_subset.iterrows():
        s_id = row["Site_ID"]
        # If a Site_ID is found the first time WITHIN the time bin
        if s_id not in updated_this_frame:
            # Replace the old info at that site if site exist else add that site; add site-id to the set
            latest_world_state[s_id] = {"Lat": row["Lat"], "Long": row["Long"], "Dist": [row["Dist"]]}
            updated_this_frame.add(s_id)
        else:
            # Append the distance list if there are multiple individuals
            latest_world_state[s_id]["Dist"].append(row["Dist"])

    lats = []
    lons = []
    vals = []

    # Extract info from the global dictionary
    for info in latest_world_state.values():
        lats.append(info["Lat"])
        lons.append(info["Long"])
        # Average the data points on the same location
        vals.append(np.mean(info["Dist"]))

    # Ensure every Lat/Long has exactly one value
    assert len(lons) == len(lats) == len(vals), f"Data mismatch! Lons:{len(lons)}, Lats:{len(lats)}, Vals:{len(vals)}"
    # Skip the time bin if too few data points are available
    if len(vals) < 3:
        print(f"  Skipping {time_label}: Too few data points.")
        return

    # Create a zoomed grid for the heatmap (slightly larger than the map zoom so no sharp edges shown)
    grid_lon, grid_lat = np.mgrid[-60:50:200j, 30:80:200j]

    # Calculate the "heat"
    # Again a rbf interpolation used
    rbf = Rbf(lons, lats, vals, function="multiquadric", smooth=0.1)
    z_mesh: np.ndarray = rbf(grid_lon, grid_lat)
    # Cut away the predictions that are greater than 1 or less than 0
    fil = z_mesh > 1
    z_mesh_fil = z_mesh.copy()
    z_mesh_fil[fil] = np.nan

    # Set up the map and zoom scale
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
    # Add title and return that frame
    plt.title(f"Time Bin: {time_label} - {time_label + window}")
    return fig


# Function to update the frames in animation
def update(t, fig, df, window, latest_world_state):
    fig.clear()  # Clear the old map
    # Extract data within the customized window size
    subset = df[(df["Mean date (BP)"] >= (t - window)) & (t >= df["Mean date (BP)"])]
    # Call the plotting function for each update
    plot_viking_bin(fig, subset, int(1950 - t), window, latest_world_state)
