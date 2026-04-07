# from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf


def create_3drbf(df):
    times = df["Mean date (BP)"].values
    lons = df["Long"].values
    lats = df["Lat"].values
    vals = df["Dist"].values

    # Calculate the "Heat"
    rbf_3d = Rbf(lons, lats, times, vals, function="multiquadric", smooth=0.05)
    return rbf_3d


# --- 2. THE PLOTTING FUNCTION (Simpler Version) ---
def plot_viking_bin(fig, df_subset: pd.DataFrame, time_label: int, rbf_3d: Rbf, window: int) -> None:

    lons_sub = df_subset["Long"].values
    lats_sub = df_subset["Lat"].values
    vals_sub = df_subset["Dist"].values

    if len(df_subset) < 3:
        print(f"  Skipping {time_label}: Too few data points.")
        return

    # Create a grid for the heatmap
    # We make the grid slightly LARGER than our zoom so the edges are hidden
    grid_lon, grid_lat = np.mgrid[-60:50:200j, 30:80:200j]

    t_constant = time_label + 50

    z_mesh = rbf_3d(grid_lon, grid_lat, np.full_like(grid_lon, t_constant))
    z_mesh = np.clip(z_mesh, 0, 1)
    # z_known = rbf(lons,lats)
    # print(z_mesh)
    # print("z_nown",z_known)

    # --- 3. THE "SANDWICH" LAYERING ---
    # fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # ZOOM: This "crops" the rectangular edges of the heatmap
    ax.set_extent([-50, 40, 35, 74], crs=ccrs.PlateCarree())
    # LAYER 1 (Bottom): The Heatmap
    # extend='both' helps smooth the color transition at the boundaries
    color_levels = np.linspace(0, 1, 51)
    heatmap = ax.contourf(grid_lon, grid_lat, z_mesh, levels=color_levels, cmap="jet", alpha=0.7, zorder=1)

    # LAYER 2 (Middle): The Ocean Mask
    # This covers the rectangular "heat" that falls in the sea
    ax.add_feature(cfeature.LAND, facecolor="none", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="cornflowerblue", zorder=2)

    # LAYER 3 (Top): Geographical details
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.4, zorder=3)

    # LAYER 4 (Top): The actual samples as dots
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

    cbar = plt.colorbar(heatmap, orientation="horizontal", pad=0.05)
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])  # Keep the labels consistent
    cbar.set_label("Genetic Distance (0 = Identical to Iceland Viking)")
    plt.title(f"Time Bin: {time_label} - {time_label + window}")
    plt.tight_layout()
    # plt.savefig(f'heatmap_{time_label}.png')
    return (fig,)


# --- 4. LOOP THROUGH TIME BINS ---
# df['Time_Bin'] = (df['Mean date (BP)'] // 100) * 100 + 50

# fig, ax = plt.subplots()
# fig = plt.figure(figsize=(10, 7))


def update(t, fig, df, rbf_3d, window):
    fig.clear()  # Clear the old map
    subset = df[(df["Mean date (BP)"] >= (t - window)) & (t >= df["Mean date (BP)"])]
    # print(t)
    plot_viking_bin(fig, subset, int(1950 - t), rbf_3d, window)


# ani = FuncAnimation(fig, update, frames=range(1250, 750, -5), repeat=False)
# ani.save("viking_migration_3drbf.gif", fps=10)
