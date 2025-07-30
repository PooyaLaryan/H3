from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from h3_sample import HexagonalHierarchicalGeospatialIndexingSystem
import pandas as pd
import folium
import numpy as np
import matplotlib.colors as mcolors
from shapely import wkt
from folium.features import DivIcon

class Clustering:
    def __init__(self):
        pass

    

    def CalculateDBSCAN(self, df : pd.DataFrame, polygon_df : pd.DataFrame, n : float):
        
        coords_rad = self.create_coords(df)

        # DBSCAN با فاصله haversine (زمین کروی)
        kms_per_radian = 6371.0088  # شعاع زمین
        epsilon = n / kms_per_radian  

        db = DBSCAN(eps=epsilon, min_samples=2, metric='haversine')
        df['cluster'] = db.fit_predict(coords_rad)


        df.to_csv('clusters_map.csv')
        self.MapShow(df, polygon_df)
        
    def CalculateH3(self, df: pd.DataFrame, polygon_df : pd.DataFrame, resolution):
        h3 = HexagonalHierarchicalGeospatialIndexingSystem()
        # فرض: df شامل Latitude و Longitude است
        
        df['h3_index'] = df.apply(lambda row: h3.Convert_to_H3_cell(row['Latitude'], row['Longitude'], resolution), axis=1)

        # شمارش تعداد فروشگاه‌ها در هر سلول
        df['cluster'] = df['h3_index']

        df.to_csv('clusters_map.csv')
        self.MapShow(df, polygon_df)


    def CalculateKMeans(self, df : pd.DataFrame, polygon_df : pd.DataFrame, n_clusters, random_state):
        coords_rad = self.create_coords(df)
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(coords_rad)
        df['cluster'] = kmeans.labels_
        df.to_csv('clusters_map.csv')
        self.MapShow(df, polygon_df)

    ###### Private 

    def create_coords(self, df : pd.DataFrame) -> np.ndarray:
            coords = df[['Latitude', 'Longitude']].to_numpy()
            coords_rad = np.radians(coords)
            return coords_rad
    
    def MapShow(self, df : pd.DataFrame, polygon_df : pd.DataFrame, show_legend : bool = True):
        colors = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.CSS4_COLORS.values())

        m = folium.Map(location=[36.3, 59.6], zoom_start=12)

        unique_clusters = sorted(df['cluster'].unique())
        medium_colors = [color for color in colors if self.is_medium_color(color)]
        #cluster_to_color = {cluster: colors[i % len(colors)] for i, cluster in enumerate(unique_clusters)}
        cluster_to_color = {cluster: medium_colors[i % len(medium_colors)] for i, cluster in enumerate(unique_clusters)}
        for _, row in df.iterrows():
            cluster = row['cluster']
            color = cluster_to_color[cluster]
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                tooltip=cluster
            ).add_to(m)

        dark_colors = [color for color in colors if self.is_dark_color(color)]
        polygon_ids = polygon_df['Id']
        polygon_to_color = {polygon: dark_colors[i % len(dark_colors)] for i, polygon in enumerate(polygon_ids)}
        for _,row in polygon_df.iterrows():
            polygon = wkt.loads(row['Border'])
            coords = [(lat, lon) for lon, lat in polygon.exterior.coords]  # تغییر ترتیب به (lat, lon)
            poly_id = row['Id']

            folium.Polygon(
                locations=coords,
                color=polygon_to_color[poly_id],
                weight=2,
                fill=False,
                tooltip = poly_id
            ).add_to(m)

            # محاسبه مرکز پلی‌گون برای نمایش برچسب
            centroid = polygon.centroid
            folium.Marker(
                location=[centroid.y, centroid.x],
                icon=DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 12px; color: black;">{poly_id}</div>',
                )
            ).add_to(m)

        if(show_legend == True):
            self.show_legend(m, cluster_to_color)

        m.save("clusters_map.html")
    
    def show_legend(self, m, cluster_to_color):
        legend_html = '''
        <div style="
            position: fixed;
            bottom: 50px;
            left: 50px;
            width: 200px;
            background-color: white;
            border:2px solid grey;
            z-index:9999;
            font-size:14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>خوشه‌ها (Clusters)</b><br>
        {}
        </div>
        '''.format("".join([
            f'<i style="background:{color};width:12px;height:12px;display:inline-block;margin-right:6px;"></i>{cluster}<br>'
            for cluster, color in cluster_to_color.items()
        ]))

        m.get_root().html.add_child(folium.Element(legend_html))

    
    def is_dark_color(self, hex_color, threshold=0.5):
        r, g, b = mcolors.to_rgb(hex_color)
        # فرمول روشنایی طبق W3C
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return luminance < threshold
    
    def is_medium_color(self, hex_color, min_luminance=0.35, max_luminance=0.75):
        r, g, b = mcolors.to_rgb(hex_color)
        # فرمول استاندارد روشنایی
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return min_luminance <= luminance <= max_luminance