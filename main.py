from transaction import SQLTransaction
from h3_sample import HexagonalHierarchicalGeospatialIndexingSystem
from clustering import Clustering

import numpy as np 
import pandas as pd
t = SQLTransaction()
h3 = HexagonalHierarchicalGeospatialIndexingSystem()
cluster = Clustering()

df = t.execute_query('''
                        SELECT
                        ps.StoreId
                        ,s.Location.STY AS Latitude
                        ,s.Location.STX AS Longitude
                        FROM CS_Dispatcher.DP.PolygonStore ps
                        INNER JOIN CS_Dispatcher.DP.Store s ON ps.StoreId = s.Id
                        INNER JOIN CS_Public.Haf.City c ON s.CityId = c.Id
                        WHERE ps.IsActive = 1 AND c.Id = 464
                        ''')

polygon_df = t.execute_query('''
SELECT p.Border.STAsText() AS Border, p.Id
FROM CS_Dispatcher.DP.Polygon p
WHERE p.Id IN (
    SELECT DISTINCT ps.PolygonId
    FROM CS_Dispatcher.DP.PolygonStore ps
    JOIN CS_Dispatcher.DP.Store s ON ps.StoreId = s.Id
    WHERE ps.IsActive = 1 AND s.CityId = 464
);
                        ''')

#cluster.CalculateDBSCAN(df, .6)
#cluster.CalculateKMeans(df, 5, 100)
cluster.CalculateH3(df, polygon_df, 8)

# data = pd.read_csv('clusters_map.csv')
# a = data['cluster'].unique()
# b = data['cluster'].value_counts()
# print(a)
# print(b)

def insert_h3():
    for resolution in np.arange(5,12): 
        for index, item in df.iterrows():
            latitude = item.Latitude
            longitude = item.Longitude
            store_id = item.StoreId
            h3id = h3.Convert_to_H3_cell(latitude, longitude, resolution)
            t.insert(f'''
                    INSERT INTO DataEngineering_ML.dbo.H3(StoreId, Resolution, H3Id)
                    VALUES({store_id},{resolution},'{h3id}')
                    ''')


