import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.core.analyzer import Analyzer
from src.core.visualizer import Visualizer

class Task2Analyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.analyzer = Analyzer(df)
        self.visualizer = Visualizer()
        self.results = {}
    
    def create_heatmaps(self):
        figs = {}
        
        if all(col in self.df.columns for col in ['区域', '商品品类', '利润']):
            if self.df['区域'].str.contains('-').any():
                self.df['省份'] = self.df['区域'].apply(lambda x: x.split('-')[1] if '-' in str(x) else x)
            else:
                self.df['省份'] = self.df['区域']

            self.df['利润'] = pd.to_numeric(self.df['利润'], errors='coerce')
            self.df = self.df.dropna(subset=['利润'])

            category_province_pivot = self.df.pivot_table(
                index='商品品类',
                columns='省份',
                values='利润',
                aggfunc='sum',
                fill_value=0
            )

            if not category_province_pivot.empty and len(category_province_pivot) > 1:
                plt.figure(figsize=(12, 8))
                sns.heatmap(category_province_pivot, cmap='Blues', annot=False)
                plt.title('商品品类和省份交叉的利润热力图')
                plt.tight_layout()
                figs['category_province_profit'] = plt.gcf()
                plt.close()

        self.results['heatmaps'] = figs
        return len(figs) > 0
    
    def perform_clustering_analysis(self):
        return self.analyzer.perform_clustering()
    
    def generate_city_distribution_data(self):
        if '区域' not in self.df.columns:
            return None

        if self.df['区域'].str.contains('-').any():
            self.df['城市'] = self.df['区域'].apply(lambda x: x.split('-')[1] if '-' in str(x) else x)
        else:
            self.df['城市'] = self.df['区域']

        city_stats = self.df['城市'].value_counts().reset_index()
        city_stats.columns = ['城市', '用户数']
        return city_stats.head(15)
    
    def perform_analysis(self):
        results = {}
        
        results['heatmaps_created'] = self.create_heatmaps()
        results['clustering'] = self.perform_clustering_analysis()
        results['city_distribution'] = self.generate_city_distribution_data()
        results['correlations'] = self.analyzer.calculate_correlations()
        
        return results
