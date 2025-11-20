SETTINGS = {
    'data_processing': {
        'missing_threshold': 0.5,
        'outlier_threshold': 3.0,
        'standardization_method': 'zscore'
    },
    'analysis': {
        'clustering_n_clusters': 3,
        'correlation_threshold': 0.7,
        'confidence_level': 0.95
    },
    'visualization': {
        'color_palette': 'viridis',
        'figure_size': (12, 8),
        'dpi': 300
    },
    'forecasting': {
        'test_size': 0.2,
        'arima_order': (2, 1, 2),
        'forecast_horizon': 14
    }
}
