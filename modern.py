import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import Rbf

# --- 1. DATA PREPARATION ---
df = pd.read_excel('Dataset/ModernSamples/GeneticDistances.xlsx')

# --- 2. THE PLOTTING FUNCTION (Simpler Version) ---
def plot_heatmap(df:pd.DataFrame)-> None:
    # Aggregate data by location (Average distance per site)
    df = df.groupby(['Lat', 'Long'])['Dist'].mean().reset_index()
    
    lons = df['Long'].values
    lats = df['Lat'].values
    vals = df['Dist'].values

    # Create a grid for the heatmap
    # Use a higher resolution (e.g., 500j) for a global map to keep it from looking pixelated
    grid_lon, grid_lat = np.mgrid[-180:180:500j, -90:90:250j]

    # Calculate the "Heat"
    rbf = Rbf(lons, lats, vals, function='multiquadric', smooth=0.1)
    z_mesh :np.ndarray= rbf(grid_lon, grid_lat)
    # fil = z_mesh > 1
    # z_mesh_fil = z_mesh.copy()
    # z_mesh_fil[fil] = np.nan
    z_mesh = np.clip(z_mesh, 0, 1)
    # z_known = rbf(lons,lats)
    # print("z_og",vals)
    # print("z_nown",z_known)

    # --- 3. THE "SANDWICH" LAYERING ---
    fig = plt.figure(figsize=(15, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # ZOOM: This "crops" the rectangular edges of the heatmap
    ax.set_global()

    # LAYER 1 (Bottom): The Heatmap
    # extend='both' helps smooth the color transition at the boundaries
    color_levels = np.linspace(0, 1, 51)
    heatmap = ax.contourf(grid_lon, grid_lat, z_mesh, vmin=0, vmax=1, levels=color_levels, 
                    cmap='jet', alpha=0.7, zorder=1)

    # LAYER 2 (Middle): The Ocean Mask
    # This covers the rectangular "heat" that falls in the sea
    # ax.add_feature(cfeature.LAND, facecolor='none', zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor='cornflowerblue', zorder=2)

    # LAYER 3 (Top): Geographical details
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.4, zorder=3)

    # LAYER 4 (Top): The actual samples as dots
    ax.scatter(lons, lats, c=vals, cmap='jet', edgecolors='black', s=40, zorder=4, vmin=0, vmax=1)

    cbar = plt.colorbar(heatmap, orientation='horizontal', pad=0.05)
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]) # Keep the labels consistent
    cbar.set_label('Genetic Distance (0 = Identical to Iceland Viking)', fontsize=18)
    plt.savefig('mordern_heatmap.png')

plot_heatmap(df)