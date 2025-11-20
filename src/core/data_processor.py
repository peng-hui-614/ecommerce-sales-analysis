import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, OrdinalEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class DataProcessor:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.column_types = {}
    
    def clean_numeric_columns(self, df):
        df_clean = df.copy()
        
        price_keywords = ['价格', '售价', '金额', '销售额', '利润', '成本']
        price_cols = [col for col in df.columns if any(kw in col for kw in price_keywords)]
        
        for col in price_cols:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        percent_keywords = ['率', '百分比', '占比']
        percent_cols = [col for col in df.columns if any(kw in col for kw in percent_keywords)]
        for col in percent_cols:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[%]', '', regex=True)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce') / 100
        
        return df_clean
    
    def auto_detect_column_types(self, df):
        column_types = {
            'numeric': [],
            'ordinal': [],
            'nominal': [],
            'identifier': []
        }

        id_keywords = ['id', '订单号', '日期', '编号', '序号']
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in id_keywords) or (df[col].nunique() / len(df) > 0.8):
                column_types['identifier'].append(col)
                continue

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        column_types['numeric'] = [col for col in numeric_cols if col not in column_types['identifier']]

        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        categorical_cols = [col for col in categorical_cols if col not in column_types['identifier']]

        ordinal_keywords = ['等级', '年龄', '评分', '段位', '层次']
        for col in categorical_cols:
            if any(keyword in col for keyword in ordinal_keywords):
                column_types['ordinal'].append(col)
            else:
                column_types['nominal'].append(col)
        
        self.column_types = column_types
        return column_types
    
    def process_categorical_variables(self, df, column_types=None, fit_encoder=True):
        if column_types is None:
            column_types = self.auto_detect_column_types(df)
            
        df_processed = df.copy()
        encoders = {}

        if column_types['ordinal'] and fit_encoder:
            ordinal_encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            df_ordinal = ordinal_encoder.fit_transform(df_processed[column_types['ordinal']])
            df_ordinal = pd.DataFrame(
                df_ordinal,
                columns=[f"{col}_编码" for col in column_types['ordinal']],
                index=df_processed.index
            )
            df_processed = pd.concat([df_processed, df_ordinal], axis=1)
            encoders['ordinal'] = ordinal_encoder

        if column_types['nominal'] and fit_encoder:
            onehot_encoder = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
            df_onehot = onehot_encoder.fit_transform(df_processed[column_types['nominal']])
            feature_names = []
            for i, col in enumerate(column_types['nominal']):
                categories = onehot_encoder.categories_[i][1:]
                feature_names.extend([f"{col}_{cat}" for cat in categories])
            df_onehot = pd.DataFrame(
                df_onehot,
                columns=feature_names,
                index=df_processed.index
            )
            df_processed = pd.concat([df_processed, df_onehot], axis=1)
            encoders['onehot'] = onehot_encoder
            encoders['onehot_features'] = feature_names

        return df_processed, encoders
    
    def get_column_statistics(self, df):
        if not self.column_types:
            self.auto_detect_column_types(df)
            
        stats = {}
        for col_type, columns in self.column_types.items():
            for col in columns:
                if col in df.columns:
                    if col_type == 'numeric':
                        stats[col] = {
                            'type': 'numeric',
                            'mean': df[col].mean(),
                            'std': df[col].std(),
                            'min': df[col].min(),
                            'max': df[col].max(),
                            'missing': df[col].isnull().sum()
                        }
                    else:
                        stats[col] = {
                            'type': col_type,
                            'unique_count': df[col].nunique(),
                            'missing': df[col].isnull().sum(),
                            'sample_values': df[col].dropna().unique()[:5].tolist()
                        }
        return stats
    
    def generate_missing_value_report(self, df):
        missing_stats = pd.DataFrame({
            '字段名': df.columns,
            '数据类型': df.dtypes.values,
            '总行数': len(df),
            '非空值数量': df.notnull().sum(),
            '缺失值数量': df.isnull().sum(),
            '缺失比例%': (df.isnull().sum() / len(df) * 100).round(2)
        })
        return missing_stats
