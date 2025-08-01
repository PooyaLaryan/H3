from transaction import SQLTransaction
from h3_sample import HexagonalHierarchicalGeospatialIndexingSystem
from clustering import Clustering
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Repository:
    def __init__(self):
        self.t = SQLTransaction()
        self.h3 = HexagonalHierarchicalGeospatialIndexingSystem()
        self.cluster = Clustering()
        pass

    def AnalysisStoreInH3(self, resolution = 7):
        df, polygon_df = self.prepare_data()
        self.cluster.CalculateH3(df, polygon_df, resolution)

    def AnalysisStoreInKMeans(self, n_clusters = 5, random_state = 100):
        df, polygon_df = self.prepare_data()
        self.cluster.CalculateKMeans(df, polygon_df, n_clusters, random_state)
    
    def AnalysisStoreInDBSCAN(self, n = .6):
        df, polygon_df = self.prepare_data()
        self.cluster.CalculateDBSCAN(df, polygon_df, n)
    
    def prepare_data(self):
        df = self.t.execute_query('''
                        SELECT
                            ps.StoreId
                            ,s.Location.STY AS Latitude
                            ,s.Location.STX AS Longitude
                            ,PolygonId
                        FROM CS_Dispatcher.DP.PolygonStore ps
                        INNER JOIN CS_Dispatcher.DP.Store s ON ps.StoreId = s.Id
                        INNER JOIN CS_Public.Haf.City c ON s.CityId = c.Id
                        WHERE ps.IsActive = 1 AND c.Id = 464
                        ''')

        polygon_df = self.t.execute_query('''
                        SELECT p.Border.STAsText() AS Border, p.Id
                        FROM CS_Dispatcher.DP.Polygon p
                        WHERE p.Id IN (
                            SELECT DISTINCT ps.PolygonId
                            FROM CS_Dispatcher.DP.PolygonStore ps
                            JOIN CS_Dispatcher.DP.Store s ON ps.StoreId = s.Id
                            WHERE ps.IsActive = 1 AND s.CityId = 464
                        );
                        ''')
        return df, polygon_df
    
    def insert_h3(self, df : pd.DataFrame) :
        for resolution in np.arange(5,12): 
            for index, item in df.iterrows():
                latitude = item.Latitude
                longitude = item.Longitude
                store_id = item.StoreId
                polygon_id = item.PolygonId
                h3id = self.h3.Convert_to_H3_cell(latitude, longitude, resolution)

                self.t.insert(f'''
                        INSERT INTO DataEngineering_ML.dbo.H3(StoreId, Resolution, H3Id, PolygonId)
                        VALUES({store_id},{resolution},'{h3id}',{polygon_id})
                        ''')
    
    def insert_h3_r7(self, df : pd.DataFrame):
            try:
                for index, item in df.iterrows():
                    latitude = item.Latitude
                    longitude = item.Longitude
                    store_id = item.StoreId
                    polygon_id = item.PolygonId
                    h3id = self.h3.Convert_to_H3_cell(latitude, longitude, 7)
                    
                    self.t.insert(f'''
                        INSERT INTO DataEngineering_ML.dbo.H3(StoreId, Resolution, H3Id, PolygonId)
                        VALUES({store_id},7 ,'{h3id}',{polygon_id})
                        ''')
                    print(f"✅ store {store_id} inserted in H3 {h3id}.")
            except Exception as e:
                print("❌ خطا در درج رکورد:", e)
    
    def AnalysisOrderCount(self, rank, title):
        analysis_df = self.t.execute_query('''
                        DECLARE
                            @StartDate BIGINT = 20250701000000000,
                            @EndDate BIGINT = 20250727235959999
                        ;WITH cte AS (
                                    SELECT
                                        h.StoreId,
                                        h.H3Id,
                                        cr.CreateDate,
                                        cr.ReferenceCode,
                                        ps.PolygonId
                                    FROM DataEngineering_ML.dbo.H3 h
                                    JOIN CS_OrderManagement.OM.CourierRequest cr ON h.StoreId = cr.StoreId
                                    JOIN CS_Dispatcher.DP.PolygonStore ps ON h.StoreId = ps.StoreId AND ps.IsActive = 1
                                    WHERE cr.CreateDate BETWEEN @StartDate AND @EndDate
                                    AND h.Resolution = 7
                                    --ORDER BY cr.CreateDate
                        )
                        SELECT
                            LEFT(CreateDate,8) AS DateKey,
                            H3Id,
                            PolygonId,
                            COUNT(ReferenceCode) AS OrderCount
                        FROM cte
                        GROUP BY
                            H3Id,
                            LEFT(CreateDate,8),
                            PolygonId
                        ''')

        analysis_df['rk'] = analysis_df.groupby('DateKey')['OrderCount']\
                    .rank(method='dense', ascending=False)

        result = analysis_df[analysis_df['rk'] == rank][['DateKey', 'H3Id', 'PolygonId', 'OrderCount']]
        result = result.sort_values(by='DateKey')
        self.show_polt(result, title)
        print(result)

    def show_polt(self, result, title):
        plt.rcParams['font.sans-serif'] = ['Tahoma'] 
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=result, x='DateKey', y='OrderCount', marker='o')
        
        for i in range(len(result)):
            x = result.iloc[i]['DateKey']
            y = result.iloc[i]['OrderCount']
            label = str(result.iloc[i]['H3Id'])
            plt.text(x, y + 0.5, label, ha='center', fontsize=9, color='black')

        plt.title(title)
        plt.xlabel('تاریخ')
        plt.ylabel('تعداد سفارش‌ها')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        plt.show()