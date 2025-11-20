import pandas as pd
import numpy as np

def load_data(file_path, file_type='auto'):
    if file_type == 'auto':
        if file_path.endswith('.xlsx'):
            file_type = 'excel'
        elif file_path.endswith('.csv'):
            file_type = 'csv'
    
    if file_type == 'excel':
        return pd.read_excel(file_path)
    elif file_type == 'csv':
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file type")

def save_data(df, file_path, file_type='auto'):
    if file_type == 'auto':
        if file_path.endswith('.xlsx'):
            file_type = 'excel'
        elif file_path.endswith('.csv'):
            file_type = 'csv'
    
    if file_type == 'excel':
        df.to_excel(file_path, index=False)
    elif file_type == 'csv':
        df.to_csv(file_path, index=False)
    else:
        raise ValueError("Unsupported file type")

def clean_data(df):
    df_clean = df.copy()
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    
    categorical_cols = df_clean.select_dtypes(exclude=[np.number]).columns
    for col in categorical_cols:
        df_clean[col] = df_clean[col].fillna('未知')
    
    return df_clean
