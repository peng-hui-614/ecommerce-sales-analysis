import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor

class Task3Forecaster:
    def __init__(self, df):
        self.df = df.copy()
        self.results = {}
    
    def prepare_time_series_data(self):
        if '日期' not in self.df.columns or '利润' not in self.df.columns:
            return False
            
        self.df['日期'] = pd.to_numeric(self.df['日期'], errors='coerce')
        self.df = self.df.dropna(subset=['日期'])
        
        daily_profit = self.df.groupby('日期')['利润'].sum().reset_index()
        daily_profit = daily_profit.rename(columns={'利润': '每日总利润'})
        
        train = daily_profit[daily_profit['日期'] <= 24]
        test = daily_profit[daily_profit['日期'] > 24]
        
        if len(train) == 0 or len(test) == 0:
            return False
            
        self.results['time_series_data'] = daily_profit
        self.results['train_data'] = train
        self.results['test_data'] = test
        self.results['y_train'] = train['每日总利润'].values
        self.results['y_test'] = test['每日总利润'].values
        
        return True
    
    def hybrid_forecast(self):
        train = self.results['train_data']
        test = self.results['test_data']
        y_train = self.results['y_train']
        y_test = self.results['y_test']
        
        try:
            arima_model = ARIMA(y_train, order=(2, 1, 2))
            arima_fit = arima_model.fit()
            arima_test_pred = arima_fit.forecast(steps=len(y_test))
        except:
            arima_test_pred = np.full_like(y_test, y_train.mean())
        
        features = ['进货价格', '销售数', '客户年龄']
        existing_features = [col for col in features if col in self.df.columns]
        
        if len(existing_features) > 0:
            train_features = self.df[self.df['日期'] <= 24][existing_features].fillna(0)
            test_features = self.df[self.df['日期'] > 24][existing_features].fillna(0)
            
            if len(train_features) > 0 and len(test_features) > 0:
                xgb_model = XGBRegressor(random_state=42)
                xgb_model.fit(train_features, y_train[:len(train_features)])
                xgb_residual_pred = xgb_model.predict(test_features)
                
                final_pred = arima_test_pred + xgb_residual_pred
            else:
                final_pred = arima_test_pred
        else:
            final_pred = arima_test_pred
        
        mape = mean_absolute_percentage_error(y_test, final_pred) * 100
        
        self.results['final_pred'] = final_pred
        self.results['mape'] = mape
        
        results_df = pd.DataFrame({
            '日期': test['日期'],
            '实际每日总利润': y_test,
            '预测利润': final_pred,
            '相对误差(%)': np.abs(y_test - final_pred) / y_test * 100
        })
        self.results['detailed_results'] = results_df
        
        return True
    
    def perform_forecasting(self):
        if not self.prepare_time_series_data():
            return {'error': '时间序列数据准备失败'}
            
        if not self.hybrid_forecast():
            return {'error': '混合预测失败'}
            
        return {
            'mape': self.results['mape'],
            'predictions': len(self.results['final_pred']),
            'details': self.results['detailed_results']
        }
