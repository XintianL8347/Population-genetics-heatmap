import pandas as pd
import numpy as np
import folium 
from folium import plugins
import geopandas as gpd

# 1. Load your data
df = pd.read_excel('Dataset/Vikings_aDNA.xlsx')
z_cols = [col for col in df.columns if col.startswith('Z_')]

# 2. Calculate the Reference Vector (Iceland Vikings)
reference_viking = df[df['CultureID'] == 1000][z_cols].mean()

# 3. Calculate Euclidean Distance for every individual
def calc_dist(row):
    return np.sqrt(np.sum((row[z_cols] - reference_viking)**2))

df['Genetic_Distance'] = df.apply(calc_dist, axis=1)

# 4. Create 100-year bins (BP = Years Before Present)
# Modern samples would be in Bin 0. 1000 BP would be in Bin 1000.
df['Time_Bin'] = (df['Mean date (BP)'] // 100) * 100
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["Long"], df["Lat"]), crs="EPSG:4326")
map = folium.Map(location=[15, 30], tiles="Cartodb dark_matter", zoom_start=2)
heat_data = [[point.xy[1][0], point.xy[0][0], dist] for point, dist in zip(gdf.geometry, gdf["Genetic_Distance"])]
# print(heat_data)
plugins.HeatMap(heat_data, radius=25, blur=20, max_zoom=5).add_to(map)

map.save('heatmap_aDNA.html')

# 5. Loop through bins to create images
unique_bins = sorted(df['Time_Bin'].unique(), reverse=True) # From oldest to newest
for time_bin in unique_bins:
    subset = gdf[gdf['Time_Bin'] == time_bin]
    # Create your geographic heatmap here using Lat, Long, and Genetic_Distance
    # savefig(f'heatmap_{time_bin}.png')
    map = folium.Map(location=[15, 30], tiles="Cartodb dark_matter", zoom_start=2)
    heat_data = [[point.xy[1][0], point.xy[0][0], dist] for point, dist in zip(subset.geometry, subset["Genetic_Distance"])]
    # print(heat_data)
    plugins.HeatMap(heat_data, radius=25, blur=20, max_zoom=5).add_to(map)

    map.save(f'heatmap_{1950-time_bin}.html')