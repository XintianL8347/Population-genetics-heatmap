import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf


# The plotting function for MODERN dataset
def plot_heatmap(df: pd.DataFrame):
    # Average the data points on the same location
    df = df.groupby(["Lat", "Long"])["Dist"].mean().reset_index()

    # Extract arrays from dataframe
    lons = df["Long"].values
    lats = df["Lat"].values
    vals = df["Dist"].values

    # Create a grid for the world heatmap
    grid_lon, grid_lat = np.mgrid[-180:180:500j, -90:90:250j]

    # Calculate the "heat"
    # Fit a rbf interpolation to "predict" the uncovered locations
    rbf = Rbf(lons, lats, vals, function="multiquadric", smooth=0.1)
    z_mesh: np.ndarray = rbf(grid_lon, grid_lat)
    # As there were not so large area with predictions exceeding the limit,
    # we set >1 to 1 and <0 to 0 instead of cutting them away for a nicer visualization
    z_mesh = np.clip(z_mesh, 0, 1)

    # Set fig size and plot the global map
    fig = plt.figure(figsize=(15, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()

    # Plot the Heatmap
    color_levels = np.linspace(0, 1, 51)
    heatmap = ax.contourf(
        grid_lon,
        grid_lat,
        z_mesh,
        vmin=0,
        vmax=1,
        levels=color_levels,
        cmap="jet",
        alpha=0.7,
        zorder=1,
    )

    # Add layers: mask the ocean and add geographical details
    ax.add_feature(cfeature.OCEAN, facecolor="cornflowerblue", zorder=2)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.4, zorder=3)

    # Add the actual data points on the top layer
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
    cbar.ax.tick_params(labelsize=14)  # Set font size for better readability
    cbar.set_label("Genetic Distance (0 = Identical to Iceland Viking)", fontsize=18)
    # Shrink the margin
    plt.tight_layout()
    return fig
