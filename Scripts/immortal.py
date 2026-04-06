import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import Rbf


# --- 2. THE PLOTTING FUNCTION (Simpler Version) ---
def plot_viking_bin(fig, df_subset: pd.DataFrame, time_label: int, window: int) -> None:
    # print(df_subset["Site_ID"])
    # This dictionary will store the most recent {Site_ID: [Lat, Long, Distance]}
    latest_world_state = {}
    for _, row in df_subset.iterrows():
        latest_world_state[row["Site_ID"]] = {
            "Lat": row["Lat"],
            "Long": row["Long"],
            "Dist": row["Dist"],
        }
        # print(latest_world_state)
    if latest_world_state:
        current_bin_df = pd.DataFrame.from_dict(latest_world_state, orient="index")
        # print(current_bin_df.columns)

    # Aggregate data by location (Average distance per site)
    site_data = current_bin_df.groupby(["Lat", "Long"])["Dist"].mean().reset_index()

    lons = site_data["Long"].values
    lats = site_data["Lat"].values
    vals = site_data["Dist"].values

    # SHAPE ASSERTION: Ensure every Lat/Long has exactly one value
    assert lons.shape == lats.shape == vals.shape, (
        f"Data mismatch! Lons:{lons.shape}, Lats:{lats.shape}, Vals:{vals.shape}"
    )

    if len(current_bin_df) < 3:
        print(f"  Skipping {time_label}: Too few data points.")
        return

    # Create a grid for the heatmap
    # We make the grid slightly LARGER than our zoom so the edges are hidden
    grid_lon, grid_lat = np.mgrid[-60:50:200j, 30:80:200j]

    # Calculate the "Heat"
    rbf = Rbf(lons, lats, vals, function="multiquadric", smooth=0.1)
    z_mesh: np.ndarray = rbf(grid_lon, grid_lat)
    fil = z_mesh > 1
    z_mesh_fil = z_mesh.copy()
    z_mesh_fil[fil] = np.nan
    # z_known = rbf(lons,lats)
    # print("z_og",vals)
    # print("z_nown",z_known)

    # --- 3. THE "SANDWICH" LAYERING ---
    # fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # ZOOM: This "crops" the rectangular edges of the heatmap
    ax.set_extent([-50, 40, 35, 74], crs=ccrs.PlateCarree())

    # LAYER 1 (Bottom): The Heatmap
    # extend='both' helps smooth the color transition at the boundaries
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

    # LAYER 2 (Middle): The Ocean Mask
    # This covers the rectangular "heat" that falls in the sea
    ax.add_feature(cfeature.LAND, facecolor="none", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="cornflowerblue", zorder=2)

    # LAYER 3 (Top): Geographical details
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.4, zorder=3)

    # LAYER 4 (Top): The actual samples as dots
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
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])  # Keep the labels consistent
    cbar.set_label("Genetic Distance (0 = Identical to Iceland Viking)")
    plt.title(f"Time Bin: {time_label} -  {time_label + window}")
    # plt.savefig(f'heatmap_{time_label}.png')
    return (fig,)


def update(t, fig, df, window):
    fig.clear()  # Clear the old map
    subset = df[(df["Mean date (BP)"] >= (t - window)) & (t >= df["Mean date (BP)"])]
    # print(t)
    plot_viking_bin(fig, subset, int(1950 - t), window)
