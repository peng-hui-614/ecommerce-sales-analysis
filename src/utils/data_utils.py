import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, OrdinalEncoder


class DataProcessor:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}

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

        return column_types