import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import datetime
import os
from pathlib import Path

# === Resolve project directories ===
# Determine the project root based on this file's location so that the
# script works regardless of the current working directory.
BASE_DIR = Path(__file__).resolve().parent.parent

# === Load and clean data from TXT ===
txt_file = BASE_DIR / "data" / "Hotspot_Indonesia.txt"
csv_file = BASE_DIR / "data" / "Hotspot_Indonesia.csv"

with open(txt_file, 'r') as file:
    lines = file.readlines()

header = lines[0].strip().split('\t')
valid_rows = [line.strip().split('\t') for line in lines[1:] if len(line.strip().split('\t')) == 12]
df = pd.DataFrame(valid_rows, columns=header)

# Convert types
df["BUJUR"] = df["BUJUR"].astype(float)
df["LINTANG"] = df["LINTANG"].astype(float)
df["KEPERCAYAAN"] = df["KEPERCAYAAN"].astype(int)

# Save cleaned CSV
df.to_csv(csv_file, index=False)

# === Filter by confidence ===
low = df[df['KEPERCAYAAN'] == 7]
med = df[df['KEPERCAYAAN'] == 8]
high = df[df['KEPERCAYAAN'] == 9]

# === Create GeoDataFrames ===
def to_gdf(df):
    geometry = [Point(xy) for xy in zip(df['BUJUR'], df['LINTANG'])]
    return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

lo_gdf = to_gdf(low)
md_gdf = to_gdf(med)
hi_gdf = to_gdf(high)

# === Region-wise counts ===
regions = ['SUMATERA', 'JAWA', 'KEPULAUAN NUSA TENGGARA', 'KALIMANTAN', 'SULAWESI', 'KEPULAUAN MALUKU', 'PAPUA']
region_counts = {
    r: {
        'low': len(low[low['REGION'] == r]),
        'med': len(med[med['REGION'] == r]),
        'high': len(high[high['REGION'] == r])
    }
    for r in regions
}

# === Load shapefiles ===
shp_indonesia = gpd.read_file(BASE_DIR / "shp" / "Indonesia_38_Provinsi.shp")
shp_others = gpd.read_file(BASE_DIR / "shp" / "world_without_idn.shp")

# === Create map ===
fig, ax = plt.subplots(figsize=(10, 7.5))
shp_others.plot(ax=ax, color='white', edgecolor='black')
shp_indonesia.plot(ax=ax, color='lightgrey', edgecolor='black')

# Plot hotspots
if not lo_gdf.empty: lo_gdf.plot(ax=ax, color='green', markersize=10, zorder=3)
if not md_gdf.empty: md_gdf.plot(ax=ax, color='yellow', markersize=10, zorder=3)
if not hi_gdf.empty: hi_gdf.plot(ax=ax, color='red', markersize=10, zorder=3)

# === Gridlines (no axis labels) ===
ax.set_xlim(95, 143)
ax.set_ylim(-19, 14)
ax.set_xticks(range(95, 145, 5))
ax.set_yticks(range(-15, 20, 5))
ax.grid(True, linestyle='--', linewidth=0.5, color='gray')
ax.tick_params(axis='both', labelsize=8)
ax.set_xlabel("")
ax.set_ylabel("")

# === Confidence level legend (lower left) ===
legend_x, legend_y = 96, -13
ax.add_patch(Rectangle((legend_x, legend_y), 9, 5, color='moccasin', zorder=1))
ax.text(legend_x + 0.5, legend_y + 4.3, 'Tingkat Kepercayaan', weight='bold', fontsize=9, family='monospace')
ax.scatter(legend_x + 1, legend_y + 3.2, color='green', s=30, edgecolor='black', zorder=3)
ax.text(legend_x + 2, legend_y + 3.2, 'Rendah', fontsize=9, va='center', family='monospace')
ax.scatter(legend_x + 1, legend_y + 2.0, color='yellow', s=30, edgecolor='black', zorder=3)
ax.text(legend_x + 2, legend_y + 2.0, 'Sedang', fontsize=9, va='center', family='monospace')
ax.scatter(legend_x + 1, legend_y + 0.8, color='red', s=30, edgecolor='black', zorder=3)
ax.text(legend_x + 2, legend_y + 0.8, 'Tinggi', fontsize=9, va='center', family='monospace')

# === Region count box (top right) ===
box_x, box_y = 127.5, 14.5
row_height = 0.6
box_width = 15
box_height = (len(regions) + 2) * row_height + 0.5

ax.add_patch(Rectangle((box_x, box_y - box_height), box_width, box_height, color='moccasin', zorder=1))

# Header with colored markers
ax.text(box_x + 0.2, box_y - 0.5, f"{'Wilayah':<24}", fontsize=8, family='monospace', weight='bold')
ax.scatter(box_x + 10.1, box_y - 0.3, color='green', s=30, edgecolor='black', zorder=3)
ax.scatter(box_x + 11.9, box_y - 0.3, color='yellow', s=30, edgecolor='black', zorder=3)
ax.scatter(box_x + 14, box_y - 0.3, color='red', s=30, edgecolor='black', zorder=3)


# Region rows
for i, region in enumerate(regions):
    low_c = region_counts[region]['low']
    med_c = region_counts[region]['med']
    high_c = region_counts[region]['high']
    label = f"{region.title():<24} {low_c:>4} {med_c:>4} {high_c:>5}"
    ax.text(box_x + 0.2, box_y - (i + 1) * row_height - 0.5, label, fontsize=8, family='monospace')

# Indonesia total row
total_label = f"{'INDONESIA':<24} {len(low):>4} {len(med):>4} {len(high):>5}"
ax.text(box_x + 0.2, box_y - (len(regions) + 1.5) * row_height - 0.5, total_label, fontsize=8, weight='bold', family='monospace')

# === Title and logo ===
today = datetime.date.today() - datetime.timedelta(days=1)
ax.text(98.8, -15.2, 'PETA SEBARAN HOTSPOT', weight='bold', fontsize=11, family='monospace')
ax.text(98.8, -16.2, f'Tanggal: {today.strftime("%d-%m-%Y")}', family='monospace')
ax.text(98.8, -17.2, 'Satelit: Terra, Aqua, Suomi NPP, NOAA-20, dan NOAA-21', family='monospace')

try:
    logo_path = BASE_DIR / "images" / "logo_bmkg.png"
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.15)
    ab = AnnotationBbox(imagebox, (97.3, -16.0), frameon=False)
    ax.add_artist(ab)
except FileNotFoundError:
    print("BMKG logo not found")

plt.tight_layout()
output_path = BASE_DIR / "images" / "update_hotspot.png"
plt.savefig(output_path, dpi=150)

print("Work has been completed.")

