import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import Rbf
from scipy.spatial import distance

def plot_heatmap(df, grid_points):
    # 1. Prepare Data (Using the distance we calculated earlier)
    # agg = df.groupby(['Lat', 'Long'])['Genetic_Distance'].mean().reset_index()
    # print(agg)
    lons = df['Long'].values
    lats = df['Lat'].values
    vals = df['Genetic_Distance'].values
    # 2. Create a grid for interpolation
    grid_lon = np.linspace(min(lons)-5, max(lons)+5, 200)
    grid_lat = np.linspace(min(lats)-5, max(lats)+5, 200)
    lon_mesh, lat_mesh = np.meshgrid(grid_lon, grid_lat)

    # 3. Radial Basis Function (Rbf) Interpolation
    # This creates the smooth "heat" effect between points
    rbf = Rbf(lons, lats, vals, 
              function='linear', smooth=0.1)
    z_mesh = rbf(grid_lon, grid_lat)

    # 3.1. Create the Radial Mask
    # Calculate distance from every grid point to the nearest actual sample
    sample_coords = np.c_[df['Long'], df['Lat']]
    tree = distance.cdist(grid_points, sample_coords, 'euclidean')
    min_dist = np.min(tree, axis=1).reshape(grid_lon.shape)

    # C. Apply the Mask: Hide anything further than 5 degrees from a sample
    # You can adjust '5.0' to make the blobs larger or smaller
    z_mesh[min_dist > 5.0] = np.nan

    # 4. Plotting with Zoom
    fig = plt.figure(figsize=(12, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # --- THE ZOOM STEP ---
    # ax.set_extent([-50, 40, 35, 74], crs=ccrs.PlateCarree())

    # 1. Plot the Heatmap (Set a low zorder)
    heatmap = ax.contourf(grid_lon, grid_lat, z_mesh, levels=50, 
                        cmap='RdYlBu_r', alpha=0.9, transform=ccrs.PlateCarree(),
                        zorder=1) 

    # 2. Mask the Ocean (Set a higher zorder)
    # This draws a solid color over all ocean areas, covering the heatmap underneath
    # Add Map Features
    ax.add_feature(cfeature.LAND, facecolor='lightgrey')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', edgecolor='none', zorder=2)

    # 3. Add Details (Set the highest zorder)
    # This ensures lines like coastlines and borders stay visible on top of everything
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black', zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5, zorder=3)

    plt.colorbar(heatmap, label='Genetic Distance to Iceland Vikings', orientation='horizontal', pad=0.05)
    plt.title("European Genetic Distance Map")
    return(plt)
    # plt.savefig('viking_heatmap_europe.png', dpi=300)