import pandas as pd
import numpy as np
# import folium 
# from folium import plugins
# import geopandas as gpd
from plot import plot_heatmap

# 1. Load your data
df = pd.read_excel('Dataset/Vikings_aDNA.xlsx')
z_cols = [col for col in df.columns if col.startswith('Z_')]

# 2. Calculate the Reference Vector (Iceland Vikings)
ref_viking = df[df['CultureID'] == 1000][z_cols].mean()

# 3. Calculate Euclidean Distance for every individual
def calc_dist(row):
    return np.sqrt(np.sum((row[z_cols] - ref_viking)**2))

df['Genetic_Distance'] = df.apply(calc_dist, axis=1)

# 4. Create 100-year bins (BP = Years Before Present)
# Modern samples would be in Bin 0. 1000 BP would be in Bin 1000.
df['Time_Bin'] = (df['Mean date (BP)'] // 100) * 100

grid_lon, grid_lat = np.mgrid[-50:40:200j, 35:74:200j]
grid_points = np.c_[grid_lon.ravel(), grid_lat.ravel()]

# 5. Loop through bins to create images
unique_bins = sorted(df['Time_Bin'].unique(), reverse=True) # From oldest to newest
for time_bin in unique_bins:
    subset = df[df['Time_Bin'] == time_bin]
    if len(subset) >= 3:
        try: 
            plt = plot_heatmap(subset, grid_points)
            plt.savefig(f'heatmap_{int(1950-time_bin)}.png', dpi=300)
        except ZeroDivisionError:
            print(f"Skipping bin {time_bin} due to mathematical error (possibly collinear points).")
    else: 
        print(f"Skipping bin {time_bin}: Not enough geographic data (found {len(subset)} locations).")