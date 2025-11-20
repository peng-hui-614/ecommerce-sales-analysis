import pandas as pd
import numpy as np

class Task4Optimizer:
    def __init__(self, df):
        self.df = df.copy()
        self.results = {}
    
    def abc_classification_analysis(self):
        if '商品品类' not in self.df.columns or '销售额' not in self.df.columns:
            return None
            
        category_stats = self.df.groupby('商品品类').agg({
            '销售额': 'sum',
            '利润': 'sum'
        }).reset_index()
        
        category_stats = category_stats.sort_values('销售额', ascending=False)
        category_stats['销售额累计占比%'] = (
            category_stats['销售额'].cumsum() / category_stats['销售额'].sum() * 100
        ).round(2)
        
        def assign_abc_class(cumulative_percent):
            if cumulative_percent <= 70:
                return 'A类'
            elif cumulative_percent <= 90:
                return 'B类'
            else:
                return 'C类'
        
        category_stats['ABC分类'] = category_stats['销售额累计占比%'].apply(assign_abc_class)
        
        self.results['abc_classification'] = category_stats
        return category_stats
    
    def price_sensitivity_analysis(self):
        if '商品品类' not in self.df.columns or '实际售价' not in self.df.columns or '销售数' not in self.df.columns:
            return None
            
        sensitivity_results = []
        
        for category in self.df['商品品类'].unique():
            category_data = self.df[self.df['商品品类'] == category]
            
            if len(category_data) < 5:
                continue
                
            try:
                price_correlation = category_data['实际售价'].corr(category_data['销售数'])
                
                if price_correlation < -0.3:
                    sensitivity_level = '高敏感'
                elif price_correlation < -0.1:
                    sensitivity_level = '中敏感'
                else:
                    sensitivity_level = '低敏感'
                    
                sensitivity_results.append({
                    '商品品类': category,
                    '价格销量相关性': round(price_correlation, 4),
                    '敏感度等级': sensitivity_level,
                    '平均价格': round(category_data['实际售价'].mean(), 2),
                    '平均销量': round(category_data['销售数'].mean(), 2)
                })
            except:
                continue
                
        sensitivity_df = pd.DataFrame(sensitivity_results)
        self.results['price_sensitivity'] = sensitivity_df.sort_values('价格销量相关性')
        return sensitivity_df
    
    def generate_operation_strategies(self):
        strategies = []
        
        abc_data = self.results.get('abc_classification')
        price_data = self.results.get('price_sensitivity')
        
        if abc_data is not None:
            for _, row in abc_data.iterrows():
                category = row['商品品类']
                abc_class = row['ABC分类']
                
                if abc_class == 'A类':
                    strategies.append(f"{category}: 重点管理，优化库存和定价策略")
                elif abc_class == 'B类':
                    strategies.append(f"{category}: 适度关注，可进行促销活动")
                else:
                    strategies.append(f"{category}: 简化管理，考虑减少库存")
        
        if price_data is not None:
            for _, row in price_data.iterrows():
                if row['敏感度等级'] == '高敏感':
                    strategies.append(f"{row['商品品类']}: 价格敏感，建议谨慎调价")
        
        self.results['strategies'] = strategies
        return strategies
    
    def perform_optimization(self):
        results = {}
        
        results['abc_analysis'] = self.abc_classification_analysis()
        results['price_sensitivity'] = self.price_sensitivity_analysis()
        results['strategies'] = self.generate_operation_strategies()
        
        return results
