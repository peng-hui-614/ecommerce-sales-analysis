import streamlit as st
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入标准库
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 根据你的实际结构调整导入
try:
    # 修正导入路径 - 匹配你的实际文件结构
    from core.data_processor import DataProcessor  # 注意是 data_processor 不是 data.processor
    from tasks.task1_preprocessing import Task1Preprocessor
    from tasks.task2_multidimensional import Task2Analyzer
    from tasks.task3_forecasting import Task3Forecaster
    from tasks.task4_optimization import Task4Optimizer
    from utils.config_utils import load_config  # 注意是 config_utils 不是 config.utils
    st.success("✅ 所有模块导入成功！")
except ImportError as e:
    st.error(f"❌ 模块导入失败: {e}")
    # 显示详细的调试信息
    st.info("调试信息：")
    st.write(f"当前目录: {current_dir}")
    st.write(f"Python路径: {sys.path}")
    # 列出目录内容帮助调试
    if os.path.exists('./core'):
        st.write("core目录内容:", os.listdir('./core'))
    if os.path.exists('./tasks'):
        st.write("tasks目录内容:", os.listdir('./tasks'))
    if os.path.exists('./utils'):
        st.write("utils目录内容:", os.listdir('./utils'))

def initialize_session_state():
    default_states = {
        'raw_data': None,
        'task1_data': None,
        'task2_data': None,
        'task3_data': None,
        'task4_data': None,
        'step1_missing_data': None,
        'step2_price_data': None,
        'step3_profit_data': None,
        'step4_abnormal_data': None,
        'step5_minmax_data': None,
        'step5_zscore_data': None,
        'processed_data': None,
        'category_encoder': None,
        'current_file': None,
        'task1_completed': False,
        'task2_completed': False,
        'task3_completed': False,
        'task4_completed': False,
        'task2_visualizations': None,
        'column_types': None
    }

    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    st.set_page_config(
        page_title="电商销售分析与策略优化系统",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">📊 电商销售分析与策略优化系统</div>', unsafe_allow_html=True)

    initialize_session_state()

    pages = {
        "项目概览": show_project_overview,
        "数据预处理": show_task1_preprocessing,
        "多维分析": show_task2_analysis,
        "销售预测": show_task3_forecasting,
        "运营优化": show_task4_optimization,
        "系统状态": show_system_status
    }

    selected_page = st.sidebar.selectbox("选择页面", list(pages.keys()))
    pages[selected_page]()

def show_project_overview():
    st.header("🎯 项目概览")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 系统功能概述
        完整的电商销售分析流程，每个任务都支持独立数据导入：

        - **数据预处理**: 按论文要求生成6个标准化输出文件
        - **多维特征分析**: 支持自定义数据或使用预处理数据
        - **销售预测**: 独立数据导入，自动检测时间序列字段  
        - **运营优化**: 灵活的数据源选择，支持多维度分析
        """)

    with col2:
        st.metric("标准输出文件", "6个")
        st.metric("分析任务", "4个")
        st.metric("数据导入方式", "每个任务独立")
        st.metric("支持格式", "Excel/CSV")

    st.subheader("任务完成状态")
    tasks = [
        ("数据预处理", st.session_state.task1_completed),
        ("多维分析", st.session_state.task2_completed),
        ("销售预测", st.session_state.task3_completed),
        ("运营优化", st.session_state.task4_completed)
    ]

    for task_name, completed in tasks:
        status = "✅ 已完成" if completed else "⏳ 待完成"
        st.write(f"- {task_name}: {status}")

def show_task1_preprocessing():
    st.header("📁 任务1: 数据预处理")
    
    uploaded_file = st.file_uploader("上传原始数据表（支持Excel或CSV格式）", type=["xlsx", "csv"])

    if uploaded_file is not None:
        try:
            processor = DataProcessor()
            
            # 改进的文件读取逻辑
            if uploaded_file.name.endswith('.xlsx'):
                try:
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                except ImportError:
                    st.error("❌ 缺少 openpyxl 库，无法读取 Excel 文件")
                    st.info("请在 requirements.txt 中添加 'openpyxl>=3.1.0'")
                    return
            else:
                df = pd.read_csv(uploaded_file)

            df_clean = processor.clean_numeric_columns(df)
            st.session_state.raw_data = df_clean
            st.session_state.current_file = uploaded_file.name

            st.success(f"文件上传成功！共 {len(df)} 条记录，{len(df.columns)} 个字段")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("原始数据预览")
                st.dataframe(df.head())
            with col2:
                st.subheader("清洗后数据预览")
                st.dataframe(df_clean.head())

            if st.button("🚀 开始数据预处理", type="primary"):
                with st.spinner("正在执行数据预处理..."):
                    task1 = Task1Preprocessor(df_clean)
                    result_files, progress_log = task1.generate_all_results()

                    if result_files:
                        st.session_state.task1_completed = True
                        st.success("✅ 数据预处理完成！")
                        
                        for log in progress_log:
                            st.write(f"▪️ {log}")
                        
                        st.subheader("📥 下载预处理结果")
                        for filename, data in result_files.items():
                            st.download_button(
                                label=f"下载 {filename}",
                                data=data.to_csv(index=False).encode('utf-8'),
                                file_name=filename.replace('.xlsx', '.csv'),
                                mime="text/csv"
                            )

        except Exception as e:
            st.error(f"文件处理错误: {str(e)}")

def show_task2_analysis():
    st.header("🔍 任务2: 多维特征分析")
    
    if st.session_state.raw_data is None:
        st.warning("请先在数据预处理页面上传数据")
        return
    
    analyzer = Task2Analyzer(st.session_state.raw_data)
    
    if st.button("执行多维分析", type="primary"):
        with st.spinner("正在执行多维分析..."):
            results = analyzer.perform_analysis()
            st.session_state.task2_completed = True
            st.success("✅ 多维分析完成！")
            
            for key, value in results.items():
                if hasattr(value, 'shape'):
                    st.write(f"{key}: {value.shape}")
                else:
                    st.write(f"{key}: {type(value)}")

def show_task3_forecasting():
    st.header("📈 任务3: 销售预测")
    
    if st.session_state.raw_data is None:
        st.warning("请先在数据预处理页面上传数据")
        return
    
    forecaster = Task3Forecaster(st.session_state.raw_data)
    
    if st.button("执行销售预测", type="primary"):
        with st.spinner("正在执行销售预测..."):
            results = forecaster.perform_forecasting()
            st.session_state.task3_completed = True
            st.success("✅ 销售预测完成！")
            st.write(f"预测精度: {results.get('mape', 'N/A')}%")

def show_task4_optimization():
    st.header("💡 任务4: 运营优化")
    
    if st.session_state.raw_data is None:
        st.warning("请先在数据预处理页面上传数据")
        return
    
    optimizer = Task4Optimizer(st.session_state.raw_data)
    
    if st.button("执行运营优化", type="primary"):
        with st.spinner("正在执行运营优化..."):
            results = optimizer.perform_optimization()
            st.session_state.task4_completed = True
            st.success("✅ 运营优化完成！")
            
            if 'strategies' in results:
                st.subheader("运营策略推荐")
                for strategy in results['strategies']:
                    st.write(f"▪️ {strategy}")

def show_system_status():
    st.header("🔧 系统状态")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("任务完成状态")
        tasks = [
            ("数据预处理", st.session_state.task1_completed),
            ("多维特征分析", st.session_state.task2_completed),
            ("销售预测", st.session_state.task3_completed),
            ("运营优化", st.session_state.task4_completed)
        ]
        for task_name, completed in tasks:
            status_icon = "✅" if completed else "⏳"
            st.write(f"{status_icon} {task_name}")

    with col2:
        st.subheader("数据状态")
        if st.session_state.raw_data is not None:
            df = st.session_state.raw_data
            st.metric("总记录数", len(df))
            st.metric("字段数量", len(df.columns))
            st.metric("当前文件", st.session_state.current_file)
        else:
            st.info("暂无数据")

if __name__ == "__main__":
    main()

