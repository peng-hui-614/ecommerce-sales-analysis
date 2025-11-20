import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

class Visualizer:
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_correlation_heatmap(self, correlation_matrix, figsize=(10, 8)):
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
        ax.set_title('变量相关性热力图')
        return fig
    
    def create_sales_trend_chart(self, sales_data, date_column='日期'):
        fig = px.line(sales_data, x=date_column, y='销售额', title='销售额趋势图')
        return fig
    
    def create_cluster_scatter(self, df, x_col, y_col, cluster_col='cluster'):
        fig = px.scatter(df, x=x_col, y=y_col, color=cluster_col, 
                        title=f'{x_col} vs {y_col} - 聚类分布')
        return fig
    
    def create_bar_chart(self, df, x_col, y_col, title=None):
        if title is None:
            title = f'{y_col} by {x_col}'
        fig = px.bar(df, x=x_col, y=y_col, title=title)
        return fig
