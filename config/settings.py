class Settings:
    PAGE_CONFIG = {
        "page_title": "电商销售分析与策略优化系统",
        "page_icon": "📊",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }

    DATA_CONFIG = {
        "supported_formats": [".xlsx", ".csv"],
        "max_file_size": 200
    }

    ANALYSIS_CONFIG = {
        "default_test_size": 0.2,
        "random_state": 42
    }


settings = Settings()