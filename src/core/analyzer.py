import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

class Analyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.results = {}
    
    def perform_clustering(self, n_clusters=3):
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return None
            
        df_numeric = self.df[numeric_cols].fillna(0)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(df_numeric)
        
        self.df['cluster'] = cluster_labels
        self.results['clustering'] = {
            'labels': cluster_labels,
            'centers': kmeans.cluster_centers_,
            'inertia': kmeans.inertia_
        }
        
        return cluster_labels
    
    def calculate_correlations(self):
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return None
            
        correlation_matrix = self.df[numeric_cols].corr()
        self.results['correlations'] = correlation_matrix
        
        return correlation_matrix
    
    def analyze_sales_trends(self, date_column=None):
        if date_column and date_column in self.df.columns:
            self.df[date_column] = pd.to_datetime(self.df[date_column])
            daily_sales = self.df.groupby(self.df[date_column].dt.date).agg({
                '销售额': 'sum',
                '利润': 'sum',
                '销售数': 'sum'
            }).reset_index()
            
            self.results['sales_trends'] = daily_sales
            return daily_sales
        return None
