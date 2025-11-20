import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, OrdinalEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class DataProcessor:
    """核心数据处理器 - 与主应用完全兼容"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.column_types = {}
    
    def clean_numeric_columns(self, df):
        """清洗数值列中的非数值字符 - 与主应用保持一致"""
        df_clean = df.copy()
        
        # 价格相关字段清洗
        price_keywords = ['价格', '售价', '金额', '销售额', '利润', '成本']
        price_cols = [col for col in df.columns if any(kw in col for kw in price_keywords)]
        
        for col in price_cols:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 处理百分比字段
        percent_keywords = ['率', '百分比', '占比']
        percent_cols = [col for col in df.columns if any(kw in col for kw in percent_keywords)]
        for col in percent_cols:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[%]', '', regex=True)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce') / 100
        
        return df_clean
    
    def auto_detect_column_types(self, df):
        """自动识别字段类型 - 与主应用完全一致"""
        column_types = {
            'numeric': [],
            'ordinal': [],
            'nominal': [],
            'identifier': []
        }

        # 标识型字段规则：唯一值占比>80% 或 字段名包含"ID/订单号/日期"
        id_keywords = ['id', '订单号', '日期', '编号', '序号']
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in id_keywords) or (df[col].nunique() / len(df) > 0.8):
                column_types['identifier'].append(col)
                continue

        # 数值型字段
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        column_types['numeric'] = [col for col in numeric_cols if col not in column_types['identifier']]

        # 分类字段（非数值、非标识）
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        categorical_cols = [col for col in categorical_cols if col not in column_types['identifier']]

        # 区分有序/无序分类
        ordinal_keywords = ['等级', '年龄', '评分', '段位', '层次']
        for col in categorical_cols:
            if any(keyword in col for keyword in ordinal_keywords):
                column_types['ordinal'].append(col)
            else:
                column_types['nominal'].append(col)
        
        # 保存类型信息
        self.column_types = column_types
        return column_types
    
    def process_categorical_variables(self, df, column_types=None, fit_encoder=True):
        """处理分类变量：有序→序数编码，无序→独热编码 - 与主应用一致"""
        if column_types is None:
            column_types = self.auto_detect_column_types(df)
            
        df_processed = df.copy()
        encoders = {}

        # 1. 有序分类：序数编码
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

        # 2. 无序分类：独热编码
        if column_types['nominal'] and fit_encoder:
            onehot_encoder = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
            df_onehot = onehot_encoder.fit_transform(df_processed[column_types['nominal']])
            # 生成独热编码字段名
            feature_names = []
            for i, col in enumerate(column_types['nominal']):
                categories = onehot_encoder.categories_[i][1:]  # 跳过第一个类别
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
    
    def step2_price_processing(self, df):
        """步骤2: 进货价格处理（按照独立脚本逻辑）"""
        df_step2 = df.copy()

        # 处理进货价格字段 - 按照独立脚本逻辑
        if '进货价格' in df_step2.columns:
            # 使用正则表达式去除非数字和非小数点字符
            df_step2['进货价格'] = df_step2['进货价格'].apply(
                lambda x: float(re.sub(r'[^\d\.]', '', str(x))) if re.search(r'[\d\.]', str(x)) else None
            )
            # 转换为整数型（四舍五入）
            df_step2['进货价格'] = df_step2['进货价格'].round().astype('Int64')

            # 处理缺失值（如果有）
            if df_step2['进货价格'].isnull().sum() > 0:
                if '商品品类' in df_step2.columns:
                    # 用品类中位数填充
                    category_price = df_step2.groupby('商品品类')['进货价格'].transform('median')
                    df_step2['进货价格'] = df_step2['进货价格'].fillna(category_price)
                else:
                    # 用整体中位数填充
                    df_step2['进货价格'] = df_step2['进货价格'].fillna(df_step2['进货价格'].median())

        return df_step2
    
    def step3_profit_correction(self, df):
        """步骤3: 修正利润计算错误（使用随机森林和KNN模型）"""
        df_step3 = df.copy()

        # 检查必要字段是否存在
        required_cols = ['实际售价', '进货价格', '销售数', '利润']
        missing_cols = [col for col in required_cols if col not in df_step3.columns]
        if missing_cols:
            print(f"利润修正缺少字段: {missing_cols}，跳过利润修正")
            return df_step3

        # 计算理论利润
        df_step3['理论利润'] = (df_step3['实际售价'] - df_step3['进货价格']) * df_step3['销售数']

        # 筛选错误和正确数据
        error_data = df_step3[df_step3['利润'] != df_step3['理论利润']].copy()
        correct_data = df_step3[df_step3['利润'] == df_step3['理论利润']].copy()

        print(f"利润计算错误数据条数：{len(error_data)}")
        print(f"利润计算正确数据条数（训练数据）：{len(correct_data)}")

        if len(correct_data) == 0:
            print("无利润计算正确的数据，无法训练模型进行补插")
            return df_step3

        if len(error_data) == 0:
            print("没有发现利润计算错误的数据")
            df_step3 = df_step3.drop(columns='理论利润')
            return df_step3

        # 准备模型训练数据
        features = ['实际售价', '进货价格', '销售数']
        X = correct_data[features]
        y = correct_data['利润']

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 1. 训练随机森林模型
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        rf_pred_test = rf_model.predict(X_test)
        rf_mse = mean_squared_error(y_test, rf_pred_test)
        print(f"随机森林模型测试集均方误差：{round(rf_mse, 2)}")

        # 2. 训练KNN模型
        knn_model = KNeighborsRegressor(n_neighbors=5)
        knn_model.fit(X_train, y_train)
        knn_pred_test = knn_model.predict(X_test)
        knn_mse = mean_squared_error(y_test, knn_pred_test)
        print(f"KNN模型测试集均方误差：{round(knn_mse, 2)}")

        # 选择MSE较小的模型进行利润补插
        if rf_mse <= knn_mse:
            print("选择随机森林模型进行利润补插")
            error_X = error_data[features]
            pred_error = rf_model.predict(error_X)
            pred_error = pred_error.round().astype(df_step3['利润'].dtype)
        else:
            print("选择KNN模型进行利润补插")
            error_X = error_data[features]
            pred_error = knn_model.predict(error_X)
            pred_error = pred_error.round().astype(df_step3['利润'].dtype)

        # 更新错误利润值
        df_step3 = df_step3.reset_index(drop=True)
        error_data = error_data.reset_index(drop=True)
        df_step3.loc[error_data.index, '利润'] = pred_error

        # 删除临时的理论利润列
        df_step3 = df_step3.drop(columns='理论利润')

        return df_step3
    
    def step4_abnormal_correction(self, df):
        """步骤4: 修正成本高于售价异常（使用模型预测合理售价）"""
        df_step4 = df.copy()

        # 检查必要字段是否存在
        required_cols = ['实际售价', '进货价格', '销售数', '客户年龄']
        missing_cols = [col for col in required_cols if col not in df_step4.columns]
        if missing_cols:
            print(f"异常修正缺少字段: {missing_cols}，跳过异常修正")
            return df_step4

        # 标记异常数据（实际售价 < 进货价格）
        abnormal_mask = df_step4['实际售价'] < df_step4['进货价格']
        abnormal_data = df_step4[abnormal_mask].copy()
        normal_data = df_step4[~abnormal_mask].copy()

        print(f"成本高于售价的异常数据条数：{len(abnormal_data)}")
        print(f"正常数据条数（训练数据）：{len(normal_data)}")

        if len(normal_data) == 0:
            print("无正常售价数据，无法训练模型进行异常修正")
            return df_step4

        if len(abnormal_data) == 0:
            print("没有发现成本高于售价的异常数据")
            # 重新计算利润确保正确性
            if all(col in df_step4.columns for col in ['实际售价', '进货价格', '销售数']):
                df_step4['利润'] = (df_step4['实际售价'] - df_step4['进货价格']) * df_step4['销售数']
            return df_step4

        # 准备模型训练数据（预测合理实际售价）
        features = ['进货价格', '销售数', '客户年龄']
        target = '实际售价'
        X = normal_data[features]
        y = normal_data[target]

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 1. 训练随机森林模型
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        rf_pred_test = rf_model.predict(X_test)
        rf_mse = mean_squared_error(y_test, rf_pred_test)
        print(f"随机森林模型（售价预测）测试集均方误差：{round(rf_mse, 2)}")

        # 2. 训练KNN模型
        knn_model = KNeighborsRegressor(n_neighbors=5)
        knn_model.fit(X_train, y_train)
        knn_pred_test = knn_model.predict(X_test)
        knn_mse = mean_squared_error(y_test, knn_pred_test)
        print(f"KNN模型（售价预测）测试集均方误差：{round(knn_mse, 2)}")

        # 综合两种模型结果进行售价补插（取平均值）
        abnormal_X = abnormal_data[features]
        rf_pred_abnormal = rf_model.predict(abnormal_X)
        knn_pred_abnormal = knn_model.predict(abnormal_X)
        combined_pred = (rf_pred_abnormal + knn_pred_abnormal) / 2
        combined_pred = combined_pred.round().astype(df_step4[target].dtype)

        # 更新异常数据的售价
        df_step4.loc[abnormal_mask, target] = combined_pred

        # 二次检查剩余异常（若仍有售价<进货价，将售价设为进货价）
        remaining_abnormal_mask = df_step4['实际售价'] < df_step4['进货价格']
        if remaining_abnormal_mask.sum() > 0:
            print(f"二次检查发现{remaining_abnormal_mask.sum()}条剩余异常数据，将售价设为进货价")
            df_step4.loc[remaining_abnormal_mask, '实际售价'] = df_step4.loc[remaining_abnormal_mask, '进货价格']

        # 重新计算正确利润（替换原利润列）
        df_step4['利润'] = (df_step4['实际售价'] - df_step4['进货价格']) * df_step4['销售数']

        return df_step4
    
    def step5_standardization(self, df):
        """步骤5: 标准化处理（按照独立脚本逻辑）"""
        df_original = df.copy()

        # 定义需标准化的数值列（与独立脚本完全一致）
        required_cols = ["进货价格", "实际售价", "销售数", "利润"]
        # 若存在销售额列，加入标准化范围
        if "销售额" in df_original.columns:
            required_cols.append("销售额")

        # 检查列是否存在
        missing_cols = [col for col in required_cols if col not in df_original.columns]
        if missing_cols:
            print(f"标准化缺少字段: {missing_cols}")

        # 筛选数值型列
        numeric_cols = [col for col in required_cols if col in df_original.columns and
                        pd.api.types.is_numeric_dtype(df_original[col])]

        if not numeric_cols:
            print("无可用的数值型列进行标准化")
            # 返回原始数据
            return df_original, df_original

        print(f"待标准化的数值列：{numeric_cols}")

        # 1. Z-Score标准化
        df_zscore = df_original.copy()
        scaler_z = StandardScaler()
        df_zscore[numeric_cols] = scaler_z.fit_transform(df_zscore[numeric_cols])

        # 2. Min-Max标准化
        df_minmax = df_original.copy()
        scaler_mm = MinMaxScaler(feature_range=(0, 1))
        df_minmax[numeric_cols] = scaler_mm.fit_transform(df_minmax[numeric_cols])

        # 输出标准化统计信息
        print("Z-Score标准化后统计描述：")
        print(df_zscore[numeric_cols].describe().round(4))
        print("Min-Max标准化后统计描述（0-1区间）：")
        print(df_minmax[numeric_cols].describe().round(4))

        return df_minmax, df_zscore
    
    def get_column_statistics(self, df):
        """获取字段统计信息"""
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
        """生成缺失值统计报告"""
        missing_stats = pd.DataFrame({
            '字段名': df.columns,
            '数据类型': df.dtypes.values,
            '总行数': len(df),
            '非空值数量': df.notnull().sum(),
            '缺失值数量': df.isnull().sum(),
            '缺失比例%': (df.isnull().sum() / len(df) * 100).round(2)
        })
        return missing_stats

# ============================================================================
# 便捷函数 - 与主应用保持一致
# ============================================================================
def auto_detect_column_types(df):
    """便捷函数：自动识别字段类型"""
    processor = DataProcessor()
    return processor.auto_detect_column_types(df)

def clean_numeric_columns(df):
    """便捷函数：清洗数值列"""
    processor = DataProcessor()
    return processor.clean_numeric_columns(df)

def process_categorical_variables(df, column_types, fit_encoder=True):
    """便捷函数：处理分类变量"""
    processor = DataProcessor()
    return processor.process_categorical_variables(df, column_types, fit_encoder)
