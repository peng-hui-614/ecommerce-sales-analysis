import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def create_plot(df, plot_type='line', x_col=None, y_col=None, **kwargs):
    if plot_type == 'line':
        fig = px.line(df, x=x_col, y=y_col, **kwargs)
    elif plot_type == 'bar':
        fig = px.bar(df, x=x_col, y=y_col, **kwargs)
    elif plot_type == 'scatter':
        fig = px.scatter(df, x=x_col, y=y_col, **kwargs)
    elif plot_type == 'histogram':
        fig = px.histogram(df, x=x_col, **kwargs)
    else:
        raise ValueError("Unsupported plot type")
    
    return fig

def save_plot(fig, file_path, format='png'):
    if hasattr(fig, 'write_image'):
        fig.write_image(file_path)
    else:
        fig.savefig(file_path, format=format, dpi=300, bbox_inches='tight')
