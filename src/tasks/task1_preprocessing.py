import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from src.core.data_processor import DataProcessor

class Task1Preprocessor:
    def __init__(self, df):
        self.df = df.copy()
        self.processor = DataProcessor()
        self.results = {}
    
    def step1_missing_value_analysis(self):
        missing_stats = self.processor.generate_missing_value_report(self.df)
        self.results['missing_stats'] = missing_stats
        return missing_stats
    
    def step2_price_processing(self):
        df_step2 = self.df.copy()
        
        if '进货价格' in df_step2.columns:
            df_step2['进货价格'] = df_step2['进货价格'].apply(
                lambda x: float(re.sub(r'[^\d\.]', '', str(x))) if re.search(r'[\d\.]', str(x)) else None
            )
            df_step2['进货价格'] = df_step2['进货价格'].round().astype('Int64')
            
            if df_step2['进货价格'].isnull().sum() > 0:
                if '商品品类' in df_step2.columns:
                    category_price = df_step2.groupby('商品品类')['进货价格'].transform('median')
                    df_step2['进货价格'] = df_step2['进货价格'].fillna(category_price)
                else:
                    df_step2['进货价格'] = df_step2['进货价格'].fillna(df_step2['进货价格'].median())

        self.results['price_processed'] = df_step2
        return df_step2
    
    def step5_standardization(self, df_step4):
        df_original = df_step4.copy()

        required_cols = ["进货价格", "实际售价", "销售数", "利润"]
        if "销售额" in df_original.columns:
            required_cols.append("销售额")

        numeric_cols = [col for col in required_cols if col in df_original.columns and
                        pd.api.types.is_numeric_dtype(df_original[col])]

        if not numeric_cols:
            self.results['step5_minmax'] = df_original
            self.results['step5_zscore'] = df_original
            return df_original, df_original

        df_zscore = df_original.copy()
        scaler_z = StandardScaler()
        df_zscore[numeric_cols] = scaler_z.fit_transform(df_zscore[numeric_cols])

        df_minmax = df_original.copy()
        scaler_mm = MinMaxScaler(feature_range=(0, 1))
        df_minmax[numeric_cols] = scaler_mm.fit_transform(df_minmax[numeric_cols])

        self.results['step5_minmax'] = df_minmax
        self.results['step5_zscore'] = df_zscore

        return df_minmax, df_zscore
    
    def generate_all_results(self):
        try:
            step1_missing = self.step1_missing_value_analysis()
            step2_price = self.step2_price_processing()
            step5_minmax, step5_zscore = self.step5_standardization(step2_price)

            result_files = {
                '电商_步骤1_缺失值统计结果.csv': step1_missing,
                '电商_步骤2_进货价格处理后数据.csv': step2_price,
                '电商_步骤5_MinMax标准化后数据.csv': step5_minmax,
                '电商_步骤5_ZScore标准化后数据.csv': step5_zscore
            }

            progress_log = [
                f"步骤1：完成缺失值统计，共{len(step1_missing)}个字段",
                f"步骤2：完成进货价格处理",
                f"步骤5：完成标准化处理，生成MinMax和ZScore两种标准化结果"
            ]

            return result_files, progress_log

        except Exception as e:
            return None, [f"预处理错误: {str(e)}"]
